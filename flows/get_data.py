from prefect.blocks.system import Secret
from prefect_aws import AwsCredentials, S3Bucket
from prefect import flow, task, get_run_logger
from datetime import datetime
from prefect.filesystems import S3
from dateutil.relativedelta import relativedelta
import pandas as pd
import requests
import json
from azure.identity import DefaultAzureCredential


@task(name="pull aws spot price data and store in s3")
def pull_spot_price_data_from_aws(start_date: datetime, end_date: datetime, az: str):
    logger = get_run_logger()
    logger.info("INFO : Starting aws spot price extraction.")
    aws_creds = AwsCredentials.load("aws-creds")
    
    logger.info("INFO : Creating boto3 client for ec2.")
    client = aws_creds.get_boto3_session().client("ec2")
    
    logger.info("INFO : Requesting ec2 spot history data.")
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
    MaxResults=10000,
    ProductDescriptions=[
        'Linux/UNIX (Amazon VPC)'
    ],
    StartTime=start_date
    )
    
    logger.info("INFO : Extract data into dataframe.")
    data = response['SpotPriceHistory']

    df = pd.DataFrame.from_dict(data)

    logger.info("INFO : Cleaning the data.")
    df['Timestamp'] = pd.to_datetime(df['Timestamp']).dt.tz_localize(None)
    df['Timestamp'] = df['Timestamp'].astype(str)
    df['SpotPrice'] = pd.to_numeric(df['SpotPrice'], downcast="float")
    
    start_date_str = start_date.strftime("%Y-%m")
    end_date_str = end_date.strftime("%Y-%m")

    file_name = f'spot_prices_{az}_{start_date_str}_{end_date_str}.parquet'
    
    fdf = df.assign(Timestamp="")
    fdf = df.assign(provider='AWS')
    
    logger.info("INFO : Converting data into a parquet file.")
    fdf.to_parquet(file_name, engine='fastparquet')

    s3_bucket = S3Bucket.load("capstone-boto3-bucket")
    logger.info("INFO : Uploading parquet file to S3 bucket.")
    s3_bucket.upload_from_path(file_name, f'aws_data/{file_name}')
    
@task(name="pull azure spot price data and store in s3")
def pull_spot_price_data_from_azure(az):
    logger = get_run_logger()
    logger.info("INFO : Starting azure spot price extraction.")
    table_data = []
    table_data.append(['SKU', 'Retail Price', 'Unit of Measure', 'Region', 'Meter', 'Product Name'])
    
    api_url = "https://prices.azure.com/api/retail/prices?api-version=2021-10-01-preview"
    query = "armRegionName eq '{0}' and armSkuName eq 'Standard_A1_v2' and priceType eq 'Consumption' and contains(meterName, 'Spot')".format(az)
    response = requests.get(api_url, params={'$filter': query})
    json_data = json.loads(response.text)
    
    for item in json_data['Items']:
        meter = item['meterName']
        table_data.append([item['armSkuName'], item['retailPrice'], item['unitOfMeasure'], item['armRegionName'], meter, item['productName']])
    
    nextPage = json_data['NextPageLink']
    
    while(nextPage):
        response = requests.get(nextPage)
        json_data = json.loads(response.text)
        nextPage = json_data['NextPageLink']
        for item in json_data['Items']:
            meter = item['meterName']
            table_data.append([item['armSkuName'], item['retailPrice'], item['unitOfMeasure'], item['armRegionName'], meter, item['productName']])
    df = pd.DataFrame(table_data, columns=["SKU", "Retail Price", "Unit of Measure", "Region", "Meter", "Product Name"])

    df = df.tail(-1)
    df = df.drop('Unit of Measure', axis=1)
    df = df.drop('Meter', axis=1)
    df.rename(columns={"SKU": "InstanceType", "Product Name": "ProductDescription", "Region": "AvailabilityZone", "Retail Price": "SpotPrice"}, inplace=True)
    df = df[['AvailabilityZone','InstanceType','ProductDescription','SpotPrice']]
    df = df.assign(provider='Azure')
    date = datetime.today()
    timestamp = date.strftime("%Y-%m-%d %H:%M:%S")
    df = df.assign(Timestamp=timestamp)
    df['Timestamp'] = df['Timestamp'].astype(str)
    df['SpotPrice'] = pd.to_numeric(df['SpotPrice'], downcast="float")
    
    logger.info("INFO : Converting data into a parquet file.")

    file_name = f'spot_prices_{az}_{timestamp}.parquet'
    df.to_parquet(file_name, engine='fastparquet')

    s3_bucket = S3Bucket.load("capstone-boto3-bucket")
    logger.info("INFO : Uploading parquet file to S3 bucket.")
    s3_bucket.upload_from_path(file_name, f'azure_data/{file_name}')
    
@task(name="read on_demand price data and store in s3")
def upload_on_demand_price_data():
    logger = get_run_logger()
    logger.info("INFO : Starting on-demand price extraction.")

    logger.info("INFO : Reading on-demand data.")
    data = pd.read_json("/opt/flows/misc/on_demand_ec2.json")

    logger.info("INFO : Converting on-demand data into dataframe.")
    df = pd.DataFrame(data)

    logger.info("INFO : Cleaning on-demand data.")
    df['OnDemandPrice'] = df['OnDemandPrice'].str.strip('$€£¥₣₹')
    df['OnDemandPrice'] = pd.to_numeric(df['OnDemandPrice'], downcast="float")
    fdf = df.assign(provider='AWS')

    logger.info("INFO : Converting data to parquet file.")
    fdf.to_parquet('on_demand_prices.parquet', engine='fastparquet')

    s3_bucket = S3Bucket.load("capstone-boto3-bucket")
    
    logger.info("INFO : Uploading parquet file to S3 bucket.")
    s3_bucket.upload_from_path("on_demand_prices.parquet", "aws_data/on_demand_prices.parquet")
    
@task(name="pull aws spec info data and store in s3")
def pull_spec_info_data_from_aws():
    logger = get_run_logger()
    logger.info("INFO : Starting aws spec info data extraction.")
    aws_creds = AwsCredentials.load("aws-creds")
    
    logger.info("INFO : Creating boto3 client for ec2.")
    client = aws_creds.get_boto3_session().client("ec2")
    
    logger.info("INFO : Requesting ec2 specs data.")
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
    
    logger.info("INFO : Extract data into dataframe.")
    data = response["InstanceTypes"]

    df = pd.DataFrame.from_dict(data)

    logger.info("INFO : Clean data.")
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

    logger.info("INFO : Convert data to parquet file.")
    fdf.to_parquet('aws_spec_info.parquet', engine='fastparquet')

    s3_bucket = S3Bucket.load("capstone-boto3-bucket")
    
    logger.info("INFO : Upload parquet file to S3 bucket.")
    s3_bucket.upload_from_path("aws_spec_info.parquet", "aws_data/aws_spec_info.parquet")
    

def get_token():
    credential = DefaultAzureCredential()
    scope = "https://management.azure.com/.default"
    token = credential.get_token(scope)
    return token.token

@task(name="pull azure spec info data and store in s3")
def pull_spec_info_data_from_azure():
    logger = get_run_logger()
    logger.info("INFO : Starting azure spec info data extraction.")
    sub_id_secret = Secret.load("sub-id")
    sub_id = sub_id_secret.get()
    table_data = []
    table_data.append(['SKUName', 'Number of Cores', 'OS Disk Size in MB', 'Resource Disk Size in MB', 'Memory in MB', 'Max Data Disk Count'])
    api_url = f'https://management.azure.com/subscriptions/{sub_id}/providers/Microsoft.Compute/locations/germanywestcentral/vmSizes?api-version=2022-11-01'
    query = "armRegionName eq 'germanywestcentral'"
    token = get_token()
    logger.info("INFO : Requesting azure spec info data extraction.")
    response = requests.get(api_url, params={'$filter': query}, headers={'Authorization': f'Bearer {token}'})
    json_data = json.loads(response.text)
    
    for item in json_data['value']:
        table_data.append([item['name'], item['numberOfCores'], item['osDiskSizeInMB'], item['resourceDiskSizeInMB'], item["memoryInMB"], item['maxDataDiskCount']])
    
    logger.info("INFO : Clean azure spec info data extraction.")
    df = pd.DataFrame(table_data, columns=['SKUName', 'Number of Cores', 'OS Disk Size in MB', 'Resource Disk Size in MB', 'Memory in MB', 'Max Data Disk Count'])
    df = df.tail(-1)
    df = df.drop('OS Disk Size in MB', axis=1)
    df = df.drop('Resource Disk Size in MB', axis=1)
    df = df.drop('Max Data Disk Count', axis=1)
    df.rename(columns={'SKUName': 'instance_type', 'Number of Cores': 'vpc', "Memory in MB": "memory"}, inplace=True)
    df['vpc'] = pd.to_numeric(df['vpc'], downcast="float")
    df['memory'] = pd.to_numeric(df['memory'], downcast="float")
    df = df.assign(provider='Azure')
    
    logger.info("INFO : Convert data to parquet file.")
    df.to_parquet('azure_spec_info.parquet', engine='fastparquet')

    s3_bucket = S3Bucket.load("capstone-boto3-bucket")
    
    logger.info("INFO : Upload parquet file to S3 bucket.")
    s3_bucket.upload_from_path("azure_spec_info.parquet", "azure_data/azure_spec_info.parquet")
    
    
@flow(name="aws_to_redshift_etl") 
def get_data(aws_azs: list, az_azs: str):
    logger = get_run_logger()
    gen_date   = datetime.today()
    logger.info("INFO : Starting aws_data_extraction.")
    for az in aws_azs:   
        logger.info("INFO : Starting aws_data_extraction for az: {0}.".format(az))
        for x in range(1, 4):
            start_date = gen_date - relativedelta(months=x)
            end_date = gen_date - relativedelta(months=x-1)
            pull_spot_price_data_from_aws(start_date, end_date, az)


    upload_on_demand_price_data()
    pull_spec_info_data_from_aws()
    
    pull_spec_info_data_from_azure()
    pull_spot_price_data_from_azure(az_azs)
    logger.info("INFO : Finished aws_data_extraction.")

if __name__ == "__main__":

    aws_azs = ["eu-central-1a", "eu-central-1b"]
    az_azs = "germanywestcentral"
    
    get_data(aws_azs, az_azs)
