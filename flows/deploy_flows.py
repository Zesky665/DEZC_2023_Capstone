from datetime import datetime
from copy_to_redshift import copy_to_redshift
from run_dbt import run_dbt
from pull_aws_data import pull_aws_data
from prefect import get_run_logger, flow, task
from prefect.deployments import Deployment
from prefect.filesystems import S3

@task(name="deploy deploy flow")
def deploy_deploy_flow():
    logger = get_run_logger()
    logger.info("INFO: Starting deploy flow deployment.")
    s3_block = S3.load("capstone-sf3s-bucket")

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
    s3_block = S3.load("capstone-sf3s-bucket")

    logger.info("INFO: Starting aws_pull flow deployment.")
    deployment = Deployment.build_from_flow(
        flow=pull_aws_data,
        name="pull data from aws",
        parameters={"start_date": datetime.today(), "end_date": datetime.today(), "azs": ["eu-central-1a", "eu-central-1b"]},
        infra_overrides={"env": {"PREFECT_LOGGING_LEVEL": "DEBUG"}},
        work_queue_name="default",
        storage=s3_block,
    )
    deployment.apply()
    logger.info("INFO: Finished aws_pull flow deployment.")
    
    logger.info("INFO: Starting copy_to_redshift flow deployment.")
    deployment = Deployment.build_from_flow(
        flow=copy_to_redshift,
        name="copy to redshift",
        parameters={},
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
