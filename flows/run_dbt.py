from prefect_sqlalchemy import DatabaseCredentials
from prefect_dbt.cli import DbtCoreOperation
from prefect.blocks.system import Secret
from prefect import flow, task, get_run_logger
import subprocess

@task(name="create dbt profile")
def create_dbt_profile():
    database_block = DatabaseCredentials.load("redshift-credentials")
    redshift_secret = Secret.load("redshift-password")
    logger = get_run_logger()
    logger.info(f'INFO : {database_block}.')
    profile_yml = f"""
default:
  outputs:
    dev:
        dbname: {database_block.database}
        host: {database_block.host}
        password: {redshift_secret.get()}
        port: {database_block.port}
        schema: {database_block.database}
        threads: 4
        type: redshift
        user: {database_block.username}
  target: dev
config: {{}}
    """
    f = open("/root/.dbt/profiles.yml", "w")
    f.write(profile_yml)
    f.close()
    
@task(name="run dbt staging script")
def create_staging_tables():
    logger = get_run_logger()
    logger.info("INFO : Begin creating staging tables.")

    output = subprocess.getoutput("pwd")
    
    logger.info(f'INFO : {output}')
    
    output = subprocess.getoutput("ls /opt/Prefect/Flows/dbt")
    
    logger.info(f'INFO : {output}')
    
    output = subprocess.getoutput("ls dbt")
    
    logger.info(f'INFO : {output}')
    
    output = subprocess.getoutput("ls dbt/models")
    
    logger.info(f'INFO : {output}')
    
    dbt_init = DbtCoreOperation(
        overwrite_profiles=False,
        commands=["dbt deps", "dbt debug", "dbt list", 
                  "dbt build --select staging_aws_spec_info --project-dir /opt/Prefect/Flows", 
                  "dbt run --select staging_aws_spec_info --project-dir /opt/Prefect/Flows",
                  "dbt build --select staging_aws_spot_prices --project-dir /opt/Prefect/Flows", 
                  "dbt run --select staging_aws_spot_prices --project-dir /opt/Prefect/Flows"]
    )
    dbt_init.run()
    logger.info("INFO : End creating staging tables.")
  
@task(name="run dbt prod script")
def create_prod_tables():
    logger = get_run_logger()
    logger.info("INFO : Begin creating production tables.")

    dbt_init = DbtCoreOperation(
        overwrite_profiles=False,
        commands=["dbt deps", "dbt debug", "dbt list", 
                  "dbt build --select prod_aws_spot_catalog --project-dir /opt/Prefect/Flows", 
                  "dbt run --select prod_aws_spot_catalog --project-dir /opt/Prefect/Flows"],
    )
    dbt_init.run()
    logger.info("INFO : End creating production tables.")
    
@flow(name="aws_to_redshift_etl") 
def run_dbt():
    create_dbt_profile()
    create_staging_tables()
    create_prod_tables()
 
if __name__ == "__main__":

    run_dbt()