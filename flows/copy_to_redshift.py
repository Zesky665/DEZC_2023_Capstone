from prefect_aws import AwsCredentials
from prefect_sqlalchemy import DatabaseCredentials
from prefect.blocks.system import Secret
from prefect import flow, task, get_run_logger
import redshift_connector

@task(name="Redshift initial setup")
def redshift_setup():
    database_block = DatabaseCredentials.load("redshift-credentials")
    redshift_secret = Secret.load("redshift-password")
    logger = get_run_logger()
    logger.info("INFO : Starting redshift setup.")
    logger.info("INFO : Connecting to Redshift.")

    logger.info("INFO : Redshift: {0}.".format(database_block.host))
    logger.info("INFO : Redshift: {0}.".format(database_block.database))
    logger.info("INFO : Redshift: {0}.".format(database_block.port))
    logger.info("INFO : Redshift: {0}.".format(database_block.username))
    logger.info("INFO : Redshift: {0}.".format(redshift_secret.get()))
    
    conn = redshift_connector.connect(
        host=database_block.host,
        database=database_block.database,
        port=int(database_block.port),
        user=database_block.username,
        password=redshift_secret.get()
    )
    cursor = conn.cursor()
    conn.autocommit = True
    logger.info("INFO : Connected to Redshift.")
    logger.info(f'INFO: Creating TEMP tables.')
    cursor.execute("CREATE TABLE IF NOT EXISTS TEMP_AWS_SPOT_PRICES( az varchar(100) NOT NULL, instance_type varchar(100) NOT NULL, prod_desc varchar(100) NOT NULL, spot_price REAL NOT NULL, time_stamp varchar(100) NOT NULL, provider varchar(100) NOT NULL);")
    cursor.execute("CREATE TABLE IF NOT EXISTS TEMP_AWS_SPEC_INFO( instance_type varchar(100) NOT NULL, free_tier BOOL NOT NULL, architecture varchar(100), cpu_speed REAL NOT NULL, vpc REAL NOT NULL, memory REAL NOT NULL, provider varchar(100) NOT NULL);")
    cursor.execute("CREATE TABLE IF NOT EXISTS TEMP_AWS_ON_DEMAND_PRICES( instance_type varchar(100) NOT NULL, on_demand_price REAL NOT NULL, provider varchar(100) NOT NULL);")
    
    cursor.execute("CREATE TABLE IF NOT EXISTS TEMP_AZURE_SPOT_PRICES( az varchar(100) NOT NULL, instance_type varchar(100) NOT NULL, prod_desc varchar(100) NOT NULL, spot_price REAL NOT NULL, time_stamp varchar(100) NOT NULL, provider varchar(100) NOT NULL);")
    cursor.execute("CREATE TABLE IF NOT EXISTS TEMP_AZURE_SPEC_INFO( instance_type varchar(100) NOT NULL, vpc REAL NOT NULL, memory REAL NOT NULL, provider varchar(100) NOT NULL)")
    logger.info(f'INFO: Finished redshift setup.')
    
@task(name="Copy aws spot price data file to redshift")
def copy_aws_spot_prices_to_redshift():
    logger = get_run_logger()
    logger.info("INFO : Begin copying data to redshift.")
    database_block = DatabaseCredentials.load("redshift-credentials")
    redshift_secret = Secret.load("redshift-password")
    
    logger.info("INFO : Connecting to Redshift.")
    conn = redshift_connector.connect(
        host=database_block.host,
        database=database_block.database,
        port=int(database_block.port),
        user=database_block.username,
        password=redshift_secret.get()
    )
    
    cursor = conn.cursor()
    conn.autocommit = False
    
    logger.info("INFO : Connecting to S3 bucket.")
    aws_creds = AwsCredentials.load("aws-creds")
    client = aws_creds.get_boto3_session().client("s3")
    response = client.list_objects_v2(
        Bucket='my-zoomcamp-capstone-bucket-zharec',
        Prefix='aws_data/')

    contents = []
    for content in response.get('Contents', []):
        contents.append(content['Key'])

    contents = [x for x in contents if "spot_prices" in x]
    for content in contents:
            logger.info("INFO : Connected to Redshift.")
            logger.info("INFO : Copy to {file_name} TEMP_Table.".format(file_name = content))
            copy_str = "copy TEMP_AWS_SPOT_PRICES from 's3://my-zoomcamp-capstone-bucket-zharec/{file_name}' iam_role 'arn:aws:iam::229947305276:role/redshift_copy_unload' parquet;".format(file_name = content)
            cursor.execute(copy_str)
    conn.commit()
    logger.info("INFO : Finished copying data.")
    
    
@task(name="Copy azure spot price data file to redshift")
def copy_azure_spot_prices_to_redshift():
    logger = get_run_logger()
    logger.info("INFO : Begin copying data to redshift.")
    database_block = DatabaseCredentials.load("redshift-credentials")
    redshift_secret = Secret.load("redshift-password")
    
    logger.info("INFO : Connecting to Redshift.")
    conn = redshift_connector.connect(
        host=database_block.host,
        database=database_block.database,
        port=int(database_block.port),
        user=database_block.username,
        password=redshift_secret.get()
    )
    
    cursor = conn.cursor()
    conn.autocommit = False
    
    logger.info("INFO : Connecting to S3 bucket.")
    aws_creds = AwsCredentials.load("aws-creds")
    client = aws_creds.get_boto3_session().client("s3")
    response = client.list_objects_v2(
        Bucket='my-zoomcamp-capstone-bucket-zharec',
        Prefix='azure_data/')

    contents = []
    for content in response.get('Contents', []):
        contents.append(content['Key'])

    contents = [x for x in contents if "spot_prices" in x]
    for content in contents:
            logger.info("INFO : Connected to Redshift.")
            logger.info("INFO : Copy to {file_name} TEMP_Table.".format(file_name = content))
            copy_str = "copy TEMP_AZURE_SPOT_PRICES from 's3://my-zoomcamp-capstone-bucket-zharec/{file_name}' iam_role 'arn:aws:iam::229947305276:role/redshift_copy_unload' parquet;".format(file_name = content)
            cursor.execute(copy_str)
    conn.commit()
    logger.info("INFO : Finished copying data.")

@task(name="copy on-demand price data to redshift")
def copy_aws_on_demand_to_redshift():
    logger = get_run_logger()
    logger.info("INFO : Begin copying data to redshift.")
    database_block = DatabaseCredentials.load("redshift-credentials")
    redshift_secret = Secret.load("redshift-password")
    
    logger.info("INFO : Connecting to Redshift.")
    conn = redshift_connector.connect(
        host=database_block.host,
        database=database_block.database,
        port=int(database_block.port),
        user=database_block.username,
        password=redshift_secret.get()
    )
    
    cursor = conn.cursor()
    conn.autocommit = True
    logger.info("INFO : Connected to Redshift.")
    logger.info("INFO : Copy to TEMP_Table.")
    cursor.execute("copy TEMP_AWS_ON_DEMAND_PRICES from 's3://my-zoomcamp-capstone-bucket-zharec/aws_data/on_demand_prices' iam_role 'arn:aws:iam::229947305276:role/redshift_copy_unload' parquet;")
    logger.info("INFO : Finished copying data.")
 
    
@task(name="copy aws spec data file to redshift")
def copy_aws_spec_info_to_redshift():
    logger = get_run_logger()
    logger.info("INFO : Begin copying data to redshift.")
    database_block = DatabaseCredentials.load("redshift-credentials")
    redshift_secret = Secret.load("redshift-password")
    
    logger.info("INFO : Connecting to Redshift.")
    conn = redshift_connector.connect(
        host=database_block.host,
        database=database_block.database,
        port=int(database_block.port),
        user=database_block.username,
        password=redshift_secret.get()
    )
    
    cursor = conn.cursor()
    conn.autocommit = True
    logger.info("INFO : Connected to Redshift.")
    logger.info("INFO : Copy to TEMP_Table.")
    cursor.execute("copy TEMP_AWS_SPEC_INFO from 's3://my-zoomcamp-capstone-bucket-zharec/aws_data/aws_spec_info.parquet' iam_role 'arn:aws:iam::229947305276:role/redshift_copy_unload' parquet;")
    logger.info("INFO : Finished copying data.")
 
@task(name="copy azure spec data file to redshift")
def copy_azure_spec_info_to_redshift():
    logger = get_run_logger()
    logger.info("INFO : Begin copying data to redshift.")
    database_block = DatabaseCredentials.load("redshift-credentials")
    redshift_secret = Secret.load("redshift-password")
    
    logger.info("INFO : Connecting to Redshift.")
    conn = redshift_connector.connect(
        host=database_block.host,
        database=database_block.database,
        port=int(database_block.port),
        user=database_block.username,
        password=redshift_secret.get()
    )
    
    cursor = conn.cursor()
    conn.autocommit = True
    logger.info("INFO : Connected to Redshift.")
    logger.info("INFO : Copy to TEMP_Table.")
    cursor.execute("copy TEMP_AZURE_SPEC_INFO from 's3://my-zoomcamp-capstone-bucket-zharec/azure_data/azure_spec_info.parquet' iam_role 'arn:aws:iam::229947305276:role/redshift_copy_unload' parquet;")
    logger.info("INFO : Finished copying data.")
 
@task(name="clean aws spot price data.")
def clean_aws_spot_price_data():
    logger = get_run_logger()
    logger.info("INFO : Begin cleaning spot data in redshift.")
    database_block = DatabaseCredentials.load("redshift-credentials")
    redshift_secret = Secret.load("redshift-password")
    
    logger.info("INFO : Connecting to Redshift.")
    conn = redshift_connector.connect(
        host=database_block.host,
        database=database_block.database,
        port=int(database_block.port),
        user=database_block.username,
        password=redshift_secret.get()
    )
    
    cursor = conn.cursor()
    conn.autocommit = False
    logger.info("INFO : Connected to Redshift.")
    logger.info("INFO : Copy to TEMP_Table.")
    cursor.execute("CREATE TABLE IF NOT EXISTS RAW_AWS_SPOT_PRICES( az varchar(100) NOT NULL, instance_type varchar(100) NOT NULL, prod_desc varchar(100) NOT NULL, spot_price REAL NOT NULL, time_stamp varchar(100) NOT NULL, provider varchar(100) NOT NULL);")
    conn.commit()
    cursor.execute("INSERT INTO RAW_AWS_SPOT_PRICES (SELECT * FROM TEMP_AWS_SPOT_PRICES as A WHERE time_stamp NOT IN (SELECT time_stamp FROM RAW_AWS_SPOT_PRICES));")
    conn.commit()
    cursor.execute("DROP TABLE TEMP_AWS_SPOT_PRICES")
    conn.commit()
    logger.info("INFO : Finished copying data.")
    
@task(name="clean aws spot price data.")
def clean_azure_spot_price_data():
    logger = get_run_logger()
    logger.info("INFO : Begin cleaning spot data in redshift.")
    database_block = DatabaseCredentials.load("redshift-credentials")
    redshift_secret = Secret.load("redshift-password")
    
    logger.info("INFO : Connecting to Redshift.")
    conn = redshift_connector.connect(
        host=database_block.host,
        database=database_block.database,
        port=int(database_block.port),
        user=database_block.username,
        password=redshift_secret.get()
    )
    
    cursor = conn.cursor()
    conn.autocommit = False
    logger.info("INFO : Connected to Redshift.")
    logger.info("INFO : Copy to TEMP_Table.")
    cursor.execute("CREATE TABLE IF NOT EXISTS RAW_AZURE_SPOT_PRICES( az varchar(100) NOT NULL, instance_type varchar(100) NOT NULL, prod_desc varchar(100) NOT NULL, spot_price REAL NOT NULL, time_stamp varchar(100) NOT NULL, provider varchar(100) NOT NULL);")
    conn.commit()
    cursor.execute("INSERT INTO RAW_AZURE_SPOT_PRICES (SELECT * FROM TEMP_AZURE_SPOT_PRICES as A WHERE time_stamp NOT IN (SELECT time_stamp FROM RAW_AZURE_SPOT_PRICES));")
    conn.commit()
    cursor.execute("DROP TABLE TEMP_AZURE_SPOT_PRICES")
    conn.commit()
    logger.info("INFO : Finished copying data.")
        
@task(name="clean aws on-demand data")
def clean_aws_on_demand_data():
    logger = get_run_logger()
    logger.info("INFO : Begin cleaning on-demand data in redshift.")
    database_block = DatabaseCredentials.load("redshift-credentials")
    redshift_secret = Secret.load("redshift-password")
    
    logger.info("INFO : Connecting to Redshift.")
    conn = redshift_connector.connect(
        host=database_block.host,
        database=database_block.database,
        port=int(database_block.port),
        user=database_block.username,
        password=redshift_secret.get()
    )
    
    cursor = conn.cursor()
    conn.autocommit = False
    logger.info("INFO : Connected to Redshift.")
    logger.info("INFO : Copy to TEMP_Table.")
    cursor.execute("CREATE TABLE IF NOT EXISTS RAW_AWS_ON_DEMAND_PRICES( instance_type varchar(100) NOT NULL, on_demand_price REAL NOT NULL, provider varchar(100) NOT NULL);")
    cursor.execute("INSERT INTO RAW_AWS_ON_DEMAND_PRICES (SELECT * FROM TEMP_AWS_ON_DEMAND_PRICES as A WHERE instance_type NOT IN (SELECT instance_type FROM RAW_AWS_ON_DEMAND_PRICES));")
    conn.commit()
    cursor.execute("DROP TABLE TEMP_AWS_ON_DEMAND_PRICES")
    conn.commit()
    logger.info("INFO : Finished copying data.")
    
@task(name="clean aws spec info data")
def clean_aws_spec_info_data():
    logger = get_run_logger()
    logger.info("INFO : Begin cleaning spec-info data in redshift.")
    database_block = DatabaseCredentials.load("redshift-credentials")
    redshift_secret = Secret.load("redshift-password")
    
    logger.info("INFO : Connecting to Redshift.")
    conn = redshift_connector.connect(
        host=database_block.host,
        database=database_block.database,
        port=int(database_block.port),
        user=database_block.username,
        password=redshift_secret.get()
    )
    
    cursor = conn.cursor()
    conn.autocommit = False
    logger.info("INFO : Connected to Redshift.")
    logger.info("INFO : Copy to TEMP_Table.")
    cursor.execute("CREATE TABLE IF NOT EXISTS RAW_AWS_SPEC_INFO( instance_type varchar(100) NOT NULL, free_tier BOOL NOT NULL, architecture varchar(100), cpu_speed REAL NOT NULL, vpc REAL NOT NULL, memory REAL NOT NULL, provider varchar(100) NOT NULL);")
    cursor.execute("INSERT INTO RAW_AWS_SPEC_INFO (SELECT * FROM TEMP_AWS_SPEC_INFO as A WHERE instance_type NOT IN (SELECT instance_type FROM RAW_AWS_SPEC_INFO));")
    conn.commit()
    cursor.execute("DROP TABLE TEMP_AWS_SPEC_INFO")
    conn.commit()
    logger.info("INFO : Finished copying data.")
 
        
@task(name="clean azure spec info data")
def clean_azure_spec_info_data():
    logger = get_run_logger()
    logger.info("INFO : Begin cleaning azure spec-info data in redshift.")
    database_block = DatabaseCredentials.load("redshift-credentials")
    redshift_secret = Secret.load("redshift-password")
    
    logger.info("INFO : Connecting to Redshift.")
    conn = redshift_connector.connect(
        host=database_block.host,
        database=database_block.database,
        port=int(database_block.port),
        user=database_block.username,
        password=redshift_secret.get()
    )
    
    cursor = conn.cursor()
    conn.autocommit = False
    logger.info("INFO : Connected to Redshift.")
    logger.info("INFO : Copy to TEMP_Table.")
    cursor.execute("CREATE TABLE IF NOT EXISTS RAW_AZURE_SPEC_INFO( instance_type varchar(100) NOT NULL, vpc REAL NOT NULL, memory REAL NOT NULL, provider varchar(100) NOT NULL);")
    cursor.execute("INSERT INTO RAW_AZURE_SPEC_INFO (SELECT * FROM TEMP_AZURE_SPEC_INFO as A WHERE instance_type NOT IN (SELECT instance_type FROM RAW_AZURE_SPEC_INFO));")
    conn.commit()
    cursor.execute("DROP TABLE TEMP_AZURE_SPEC_INFO")
    conn.commit()
    logger.info("INFO : Finished copying data.")
 
    
@flow(name="aws_to_redshift_etl") 
def copy_to_redshift():
    logger = get_run_logger()
    logger.info("INFO : Begin copying data to redshift.")
    redshift_setup()
    copy_aws_spot_prices_to_redshift()
    copy_aws_on_demand_to_redshift()
    copy_aws_spec_info_to_redshift()
    copy_azure_spot_prices_to_redshift()
    copy_azure_spec_info_to_redshift()
    clean_aws_spot_price_data()
    clean_aws_on_demand_data()
    clean_aws_spec_info_data()
    clean_azure_spot_price_data()
    clean_azure_spec_info_data()
    logger.info("INFO : Finished copying data to redshift.")
 
if __name__ == "__main__":

    copy_to_redshift()
