# Local setup

1. Install [docker for desktop](https://www.docker.com/products/docker-desktop/). 

2. Create an .prefect_env file in the root directory. 

The contents of the file should look like this: 
```
PREFECT_KEY: 

PREFECT_WORKSPACE:

AWS_ACCESS_KEY_ID: 

AWS_SECRET_ACCESS_KEY: 

AWS_REGION:

DBT_API_KEY: 

DBT_ACCOUNT:

HOST: 

DATABASE: 

PORT:

USERNAME:

PASSWORD:

AZ_SUB_ID: 

AZURE_CLIENT_ID: 

AZURE_CLIENT_SECRET: 

AZURE_TENANT_ID: 

```
How to get prefect values:
- Login to prefect cloud. 
 - Go the this url: https://app.prefect.cloud/my/api-keys
- Press the `+` next to `API KEYS`
- Add a name and press `Create`
- Copy the secret value and the name.  

How to get the aws values: 
- Login to aws console.
- Go to IAM.
- Create a new user.
- Give him appropriate permissions. 
- Go to the `Security Credentials` tab.
- In the `Access Keys` section press `Create Keys`
- Copy secret value and key id. 

How to get dbt values:
- Login to cloud dbt
- Go to : https://cloud.getdbt.com/settings/profile
- Copy API key. 
- On the same page, press `Projects` in the sidebar. 
- The url will change to: `cloud.getdbt.com/settings/accounts/YOUR ACCOUNT ID`
- Copy account id

How to get Azure values:
- Login to azure console
- Navigate to Active Directory > App Registration.
- Create new app. 
- Copy application id, this the aazure_client_id. 
- Copy tenant id, this is the azure_tennant_id. 
- Click `add certificate or secret`
- Add secret.
- Copy value, this is the azure_client_secret.

How to get DB values:
- Login to AWS console. 
- Navigate to redshift. 
- Select exisitng redshift dwh. 
- Copy endpoint, remove the :5439/schema_name. This is the host value. 
- Everything else copy from the terraform secrets file. 

3. Setup terraform

Navigate to the /infra directory. 

This is where the terraform script lives. 

Add a secrets.tfvars file here. 

To it add the following. 

```
my_ip_address     = "123.45.67.89" // use 'curl https://checkip.amazonaws.com' to find it, use your local pc's ip address
redshift_password = ""
redshift_user     = ""
prefect_env = <<EOT
PREFECT_KEY = 
PREFECT_WORKSPACE = 
AWS_ACCESS_KEY_ID = 
AWS_SECRET_ACCESS_KEY = 
AWS_REGION = 
DBT_API_KEY = 
DBT_ACCOUNT =
HOST = 
DATABASE = 
PORT = 
USERNAME = 
PASSWORD = 
AZ_SUB_ID = 
AZURE_CLIENT_ID = 
AZURE_CLIENT_SECRET = 
AZURE_TENANT_ID = 
EOT
```

In the prefect_env variables add the same values that are in the prefect_env file, just using this formatting. 

4. Generate keys. 
Run the following command: 
```ssh-keygen -t rsa -b 4096 -m pem -f metabase_kp && openssl rsa -in metabase_kp -outform pem && mv metabase_kp metabase_kp.pem && chmod 400 metabase_kp.pem```

5. Run the terraform script
Navigate to the infra directory and run the following.

`terraform init`
`terraform plan -var-file=secrets.tfvars`
`terraform apply -var-file=secrets.tfvars --auto-approve`

6. Run docker-compose
You can run the prefect agent and the metabase instance locally, simply navigate to the root of the project and run the following.
`docker-compose up`

You can afterwards open the containers in interactive mode via the docker-desktop GUI or via the following command. 
`docker ps` - to get the id of the container
`docker exec -it <container name/id> /bin/bash` - to start an interactive session.

