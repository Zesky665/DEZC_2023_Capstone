import json
import os
import pandas as pd
import re
from prefect import flow, task
from prefect_aws import AwsCredentials, S3Bucket, ECSTask
from prefect_sqlalchemy import ConnectionComponents, SyncDriver, DatabaseCredentials
from prefect.blocks.system import Secret
from prefect.filesystems import S3
from prefect_dbt.cli import DbtCliProfile
from prefect_dbt.cli.configs import GlobalConfigs, TargetConfigs
from prefect_dbt.cloud import DbtCloudCredentials
from prefect import get_run_logger
from pathlib import Path


@task(name="setup .aws credentials")
def create_aws_creds():
    
    aws_key_id = ""
    aws_key = ""
    aws_region = ""
    
    if ("AWS_KEY_ID" in os.environ):
        aws_key_id = os.environ['AWS_KEY_ID']
 
    if ("AWS_KEY" in os.environ):
        aws_key = os.environ['AWS_KEY']
        
    if ("AWS_REGION" in os.environ):
        aws_region = os.environ['AWS_REGION']

    config = '''
[default]
region = {0}'''.format(aws_region)
    
    f = open("/root/.aws/config", "w")
    f.write(config)
    f.close()
    
    credentials = '''
[default]
aws_access_key_id = {0}
aws_secret_access_key = {1}'''.format(aws_key_id, aws_key)
    
    f = open("/root/.aws/credentials", "w")
    f.write(credentials)
    f.close()


@task(name="deploy_aws")
def deploy_aws_credentials_block(aws_key_id, aws_key, aws_region):
    logger = get_run_logger()
    logger.info("INFO: Started aws creds block deployment.")
    
    aws_credentials = AwsCredentials(
    aws_access_key_id = aws_key_id,
    aws_secret_access_key = aws_key,
    aws_region=aws_region
    )
    
    aws_credentials.save("aws-creds", overwrite=True)
    
    logger.info("INFO: Finished aws creds block deployment.")
    
    
@task(name="deploy_s3")
def deploy_s3_block(aws_key_id, aws_key):
    logger = get_run_logger()
    logger.info("INFO: Started s3 block deployment.")
    
    # S3 values
    s3_block_name = "deployments"
    bucket_name = "my-zoomcamp-capstone-bucket-zharec"
    bucket_path = f'{bucket_name}/{s3_block_name}'
    
    logger.info(f'{s3_block_name} {bucket_name} {bucket_path}')
    
    sf3s = S3(
        bucket_path=bucket_path,
        aws_access_key_id=aws_key_id,
        aws_secret_access_key=aws_key
    )
    
    sf3s.save("capstone-sf3s-bucket", overwrite=True)
    
    aws_creds = AwsCredentials.load("aws-creds")

    boto3 = S3Bucket(
        bucket_name="my-zoomcamp-capstone-bucket-zharec",
        aws_credentials=aws_creds,
        basepath="subfolder"
    )
    
    boto3.save("capstone-boto3-bucket", overwrite=True)
    logger.info("INFO: Finished se bucket block deployment.")
    
@task(name="deploy secret value")
def deploy_redshift_password(redshift_password):
    logger = get_run_logger()
    logger.info("INFO: Started redshift secret deployment.")
    
    secret = Secret(
        value=redshift_password,
    )

    secret.save("redshift-password", overwrite=True)
    logger.info("INFO: Finished redshift secret deployment.")
    
@task(name="deploy redshift credentials")
def deploy_redshift_credentials(host, database, port, username, password):
    logger = get_run_logger()
    logger.info("INFO: Started redshift block deployment.")
    logger.info(f'DB_VALEU: {host}')
    logger.info(f'DB_VALEU: {database}')
    logger.info(f'DB_VALEU: {port}')
    logger.info(f'DB_VALEU: {username}')
    logger.info(f'DB_VALEU: {password}')
    
    sqlalchemy_credentials = DatabaseCredentials(
        driver=SyncDriver.POSTGRESQL_PSYCOPG2,
        host=host,
        database=database,
        port=port,
        username=username,
        password=password,
    )

    sqlalchemy_credentials.save("redshift-credentials", overwrite=True)
    logger.info("INFO: Finished redshift block deployment.")
   
@task(name="deploy dbt credentials")
def deploy_dbt_credentials_block(dbt_api_key, dbt_account_id):
    logger = get_run_logger()
    logger.info("INFO: Started dbt credentials block deployment.")

    DbtCloudCredentials(
        api_key=dbt_api_key,
        account_id=dbt_account_id
    ).save("dbt-creds", overwrite=True)
    
    
@task(name="deploy dbt profile")
def deploy_dbt_profile(host, database, port, username, password):
    logger = get_run_logger()
    logger.info("INFO: Started dbt profile block deployment.")

    target_configs_extras = dict(
        host=host,
        user=username,
        password=password,
        port=port,
        dbname=database,
    )
    target_configs = TargetConfigs(
        type="redshift",
        schema="capstone_db",
        threads=4,
        extras=target_configs_extras
    )
    
    target_configs.save("dbt-redshift-configs", overwrite=True)
    
    dbt_cli_profile = DbtCliProfile(
        name="default",
        target="dev",
        target_configs=target_configs,
    )
    dbt_cli_profile.save("dbt-profile-redshift",overwrite=True)
    
# def deploy_ecs_task_block():
    
#     # Opening JSON file
#     f = open('Prefect/Flows/output.js')
    
#     # returns JSON object as
#     # a dictionary
#     data = json.loads(f)
    
#     # Loading the AWSCredentials
#     aws_creds = AwsCredentials.load("aws-credentials")
    
    
#     # ECS Task values
#     ecs_task_block_name = "flow-runner"
#     ecs_task_def = data["task_definition"]["value"].replace("\"", "")
#     cpu_value = ''
#     cpu_memory = ''
#     cpu_image = ''
#     vpc_id = data["vpc_id"]["value"]
#     cluster_arn = data["ecs-cluster"]["value"]
#     execution_role_arn = data["execution_role"]["value"]
#     task_role_arn = data["task_role"]["value"]
#     launch_type = "FARGATE_SPOT"
    
#     # Closing file
#     f.close()
    
@flow(name="deploy block flow")
def deploy_blocks(aws_key_id, aws_key, aws_region, dbt_api_key, dbt_account_id, host, database, port, username, password):

    deploy_aws_credentials_block(aws_key_id, aws_key, aws_region)
    deploy_s3_block(aws_key_id, aws_key)
    deploy_redshift_password(password)
    deploy_redshift_credentials(host, database, port, username, password)
    deploy_dbt_credentials_block(dbt_api_key, dbt_account_id)
    deploy_dbt_profile(host, database, port, username, password)
    

if __name__ == "__main__":
    aws_key_id = ""
    aws_key = ""
    aws_region = ""
    dbt_api_key = ""
    dbt_account_id = 0
    host = "" 
    database = "" 
    port = 0
    username = "" 
    password = ""
    
    if ("AWS_ACCESS_KEY_ID" in os.environ):
        aws_key_id = os.environ['AWS_ACCESS_KEY_ID']
 
    if ("AWS_SECRET_ACCESS_KEY" in os.environ):
        aws_key = os.environ['AWS_SECRET_ACCESS_KEY']
        
    if ("AWS_REGION" in os.environ):
        aws_region = os.environ['AWS_REGION']
        
    if ("DBT_API_KEY" in os.environ):
        dbt_api_key = os.environ['DBT_API_KEY']
 
    if ("DBT_ACCOUNT" in os.environ):
        dbt_account_id = os.environ['DBT_ACCOUNT']
        
    if ("HOST" in os.environ):
        host = os.environ['HOST']
 
    if ("DATABASE" in os.environ):
        database = os.environ['DATABASE']
        
    if ("PORT" in os.environ):
        port = os.environ['PORT']
        
    if ("USERNAME" in os.environ):
        username = os.environ['USERNAME']
 
    if ("PASSWORD" in os.environ):
        password = os.environ['PASSWORD']
    
    dbt_account_id = int(dbt_account_id)
    deploy_blocks(aws_key_id, aws_key, aws_region, dbt_api_key, dbt_account_id, host, database, port, username, password)
