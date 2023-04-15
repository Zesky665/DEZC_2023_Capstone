# Collecting data on the cost of spot instances across the major Cloud Providers (AWS, Azure)


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

![Data diagram](https://github.com/Zesky665/DEZC_2023_Capstone/blob/final/misc/data_diagram.png)

## Data Sources: 

 - [AWS historical pricing](https://docs.aws.amazon.com/cli/latest/reference/ec2/describe-spot-price-history.html).

 - Azure price list [API](https://learn.microsoft.com/en-us/rest/api/cost-management/retail-prices/azure-retail-prices).

## Tech Diagram


## Dashboard
 ** insert pictures of the diashboars **
## Insights 
- AWS spot instances are often as costly as on-demand. Even when available the savings are much less. 
- Azure spot instances (Preemptible) seem to be much more available, since the prices are much close to the -90% that is advertised. 
## To-Do
** Work on this last**
