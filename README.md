# Collecting data on the cost of spot instances across the three major Cloud Providers (AWS, Azure, GCP)


## Objectives 

- Create a DWH for staring pricing data from various cloud providers.
- Create orchestration that will pull data from the sources periodicaly. 
- Create a dashboard that will show relevant metrics. 
- Create a workflow to automaticaly deploy all of this. 

## Technology used

- Cloud: AWS
- Containerization: Docker with Docker-Compose
- Infrastructure: Terraform
- DWH: Redshift
- Orchestration: Prefect
- Data Transformation: Pandas
- Data Visualization: Metabase

## Setup instructions

If you want to run it locally. 
[Local setup](https://github.com/Zesky665/DEZC_2023_Capstone/blob/final/misc/Local_Setup.md)

If you want to run it with GitHub Actions
[GitHub Setup](https://github.com/Zesky665/DEZC_2023_Capstone/blob/final/misc/GitHub_Setup.md)

## DWH Database Schema

** Insert picture here **

## Data Sources: 
 - [AWS historical pricing](https://docs.aws.amazon.com/cli/latest/reference/ec2/describe-spot-price-history.html).
 - Azure price list [API](https://learn.microsoft.com/en-us/rest/api/cost-management/retail-prices/azure-retail-prices).
 - GCP Pricing data. 

## Tech Diagram


## Dashboard
 ** insert pictures of the diashboars **
## Insights 
** insert insights in bullet points **
## To-Do
** Work on this last**
