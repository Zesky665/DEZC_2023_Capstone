from copy_to_redshift import copy_to_redshift
from run_dbt import run_dbt
from get_aws_data import get_aws_data
from get_azure_data import get_azure_data
from prefect import get_run_logger, flow, task
from prefect.deployments import Deployment
from prefect_aws import S3Bucket
from prefect.orion.schemas.schedules import CronSchedule

@task(name="deploy deploy flow")
def deploy_deploy_flow():
    logger = get_run_logger()
    logger.info("INFO: Starting deploy flow deployment.")
    s3_block = S3Bucket.load("capstone-boto3-bucket")

    deployment = Deployment.build_from_flow(
        flow=deploy_flows,
        name="deploy-flows",
        parameters={},
        infra_overrides={"env": {"PREFECT_LOGGING_LEVEL": "DEBUG"}},
        work_queue_name="default",
        storage=s3_block,
    )
    
    deployment.apply()
    logger.info("INFO: Finished deploy flow deployment.")
    
@task(name="deploy aws etl flow")
def deploy_aws_etl_flow():
    logger = get_run_logger()
    logger.info("INFO: Starting aws_etl flow deployment.")
    s3_block = S3Bucket.load("capstone-boto3-bucket")

    logger.info("INFO: Starting aws_pull flow deployment.")
    deployment = Deployment.build_from_flow(
        flow=get_aws_data,
        name="getting aws data",
        parameters={"aws_azs": ["eu-central-1a", "eu-central-1b"]},
        schedule=(CronSchedule(cron="00 10 * * *", timezone="UTC")),
        infra_overrides={"env": {"PREFECT_LOGGING_LEVEL": "DEBUG"}},
        work_queue_name="default",
        storage=s3_block,
    )
    deployment.apply()
    logger.info("INFO: Finished aws_pull flow deployment.")
    
    logger.info("INFO: Starting azure_pull flow deployment.")
    deployment = Deployment.build_from_flow(
        flow=get_azure_data,
        name="getting azure data",
        parameters={ "az_azs": "germanywestcentral"},
        schedule=(CronSchedule(cron="00 10 * * *", timezone="UTC")),
        infra_overrides={"env": {"PREFECT_LOGGING_LEVEL": "DEBUG"}},
        work_queue_name="default",
        storage=s3_block,
    )
    deployment.apply()
    logger.info("INFO: Finished azure_pull flow deployment.")
    
    logger.info("INFO: Starting copy_to_redshift flow deployment.")
    deployment = Deployment.build_from_flow(
        flow=copy_to_redshift,
        name="copy to redshift",
        parameters={},
        schedule=(CronSchedule(cron="00 11 * * *", timezone="UTC")),
        infra_overrides={"env": {"PREFECT_LOGGING_LEVEL": "DEBUG"}},
        work_queue_name="default",
        storage=s3_block,
    )
    deployment.apply()
    logger.info("INFO: Finished copy_to_redshift flow deployment.")
    
    logger.info("INFO: Starting run_dbt flow deployment.")
    deployment = Deployment.build_from_flow(
        flow=run_dbt,
        name="run dbt models",
        parameters={},
        schedule=(CronSchedule(cron="00 12 * * *", timezone="UTC")),
        infra_overrides={"env": {"PREFECT_LOGGING_LEVEL": "DEBUG"}},
        work_queue_name="default",
        storage=s3_block,
    )
    deployment.apply()
    logger.info("INFO: Finished run_dbt flow deployment.")
    

    logger.info("INFO: Finished aws_etl flow deployment.")
    
    
@flow(name="deploy flows flow")
def deploy_flows():
    logger = get_run_logger()
    logger.info("INFO: Starting flow deployment.")
    deploy_deploy_flow()
    deploy_aws_etl_flow()
    logger.info("INFO: Finished flow deployment.")

if __name__ == "__main__":
    deploy_flows()
