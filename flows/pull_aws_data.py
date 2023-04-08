from prefect_aws import AwsCredentials, S3Bucket
from prefect import flow, task, get_run_logger
from datetime import datetime
from prefect.filesystems import S3
import pandas as pd

@task(name="pull spot price data and store in s3")
def pull_spot_price_data_from_aws(start_date: datetime, end_date: datetime, az: str):
    logger = get_run_logger()
    logger.info("INFO : Starting.")
    aws_creds = AwsCredentials.load("aws-creds")
    client = aws_creds.get_boto3_session().client("ec2")
    
    response = client.describe_spot_price_history(
    Filters=[{},],
    AvailabilityZone=az,
    DryRun=False,
    EndTime=end_date,
    InstanceTypes=[
        'a1.medium',
        'a1.large',
        'm5a.large'
        ],
    MaxResults=123,
    ProductDescriptions=[
        'Linux/UNIX (Amazon VPC)'
    ],
    StartTime=start_date
    )
    
    data = response['SpotPriceHistory']

    df = pd.DataFrame.from_dict(data)

    df['Timestamp'] = pd.to_datetime(df['Timestamp']).dt.tz_localize(None)
    df['Timestamp'] = df['Timestamp'].astype(str)
    df['SpotPrice'] = pd.to_numeric(df['SpotPrice'], downcast="float")
    
    start_date_str = start_date.strftime("%Y-%m")
    end_date_str = end_date.strftime("%Y-%m")

    file_name = f'spot_prices_{az}_{start_date_str}_{end_date_str}.parquet'
    
    fdf = df.assign(provider='AWS')
    
    fdf.to_parquet(file_name, engine='fastparquet')

    s3_bucket = S3.load("capstone-sf3s-bucket")
    
    s3_bucket.upload_from_path(file_name, f'aws_data/{file_name}')
    
@task(name="read on_demand price data and store in s3")
def upload_on_demand_price_data():
    logger = get_run_logger()
    logger.info("INFO : Starting.")

    data = pd.read_json("/opt/flows/misc/on_demand_ec2.json")

    df = pd.DataFrame(data)

    df['OnDemandPrice'] = df['OnDemandPrice'].str.strip('$€£¥₣₹')
    df['OnDemandPrice'] = pd.to_numeric(df['OnDemandPrice'], downcast="float")
    fdf = df.assign(provider='AWS')

    fdf.to_parquet('on_demand_prices.parquet', engine='fastparquet')

    s3_bucket = S3.load("capstone-sf3s-bucket")
    
    s3_bucket.upload_from_path("on_demand_prices.parquet", "aws_data/on_demand_prices.parquet")
    
@task(name="pull spec info data and store in s3")
def pull_spec_info_data_from_aws():
    logger = get_run_logger()
    logger.info("INFO : Starting.")
    aws_creds = AwsCredentials.load("aws-creds")
    client = aws_creds.get_boto3_session().client("ec2")
    
    response = client.describe_instance_types(
        DryRun=False,
        InstanceTypes=[
            'a1.medium',
            'a1.large',
            'm5a.large'],
        Filters=[
            {},
        ],
    )
        
    data = response["InstanceTypes"]

    df = pd.DataFrame.from_dict(data)

    dff = pd.DataFrame(columns = ["instance_type", "free_tier", "architecture", "cpu_speed", "vpc", "memory"])

    dff["instance_type"] = df["InstanceType"]
    dff["free_tier"] = df["FreeTierEligible"]
    dff["architecture"] = [d.get('SupportedArchitectures')[0] for d in df["ProcessorInfo"]]
    dff["cpu_speed"] = [d.get('SustainedClockSpeedInGhz') for d in df["ProcessorInfo"]]
    dff['cpu_speed'] = pd.to_numeric(dff['cpu_speed'], downcast="float")
    dff["vpc"] = [d.get('DefaultVCpus') for d in df["VCpuInfo"]]
    dff['vpc'] = pd.to_numeric(dff['vpc'], downcast="float")
    dff["memory"] = [d.get('SizeInMiB') for d in df["MemoryInfo"]]
    dff['memory'] = pd.to_numeric(dff['memory'], downcast="float")
    
    fdf = dff.assign(provider='AWS')

    fdf.to_parquet('spec_info.parquet', engine='fastparquet')

    s3_bucket = S3.load("capstone-sf3s-bucket")
    
    s3_bucket.upload_from_path("spec_info.parquet", "aws_data/spec_info.parquet")
    

@flow(name="aws_to_redshift_etl") 
def pull_aws_data(start_date: datetime, end_date: datetime, azs: list):

    for az in azs:   
        pull_spot_price_data_from_aws(start_date, end_date, az)
    
    upload_on_demand_price_data()
    pull_spec_info_data_from_aws()

if __name__ == "__main__":
    start_date = datetime.today()
    end_date   = datetime.fromisoformat('2022-01-01')
    azs = ["eu-central-1a", "eu-central-1b"]
    pull_aws_data(start_date, end_date, azs)
