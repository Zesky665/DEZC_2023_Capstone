# Collecting data on the cost of spot instances across the major Cloud Providers (AWS, Azure)


## Problem
When deciding on a cloud provider for a project we as data engineers have to consider lot of different variables. One of the most important ones is cost. Thanks to the way that most of the pricing is communicated by their respective providers it's difficult to get a simple comparison without manually looking for it across many different websites/screens/tabs/consoles.
This project aims to make these types of questions answerable at a glance.

(For the sake of simplicity I've stuck to one region and 3 tiers of a single service, although the project can easily be extended to include other offerings.)

## Objectives 

- Create a DWH for staring pricing data from various cloud providers.
- Create orchestration that will pull data from the sources periodicaly. 
- Create a dashboard that will show relevant metrics. 
- Create a workflow to automaticaly deploy all of this. 

## Technology used

- Cloud: AWS (EC2, S3, Redshift)
- Containerization: Docker with Docker-Compose
- Infrastructure: Terraform
- DWH: Redshift
- Orchestration: Prefect
- Data Transformation: Pandas
- Data Visualization: Metabase

## Setup instructions

If you want to run it locally. 
[Local setup](https://github.com/Zesky665/DEZC_2023_Capstone/blob/main/misc/Local_Setup.md)

If you want to run it with GitHub Actions
[GitHub Setup](https://github.com/Zesky665/DEZC_2023_Capstone/blob/main/misc/GitHub_Setup.md)

## DWH Database Schema

![Data diagram](https://github.com/Zesky665/DEZC_2023_Capstone/blob/main/misc/data_diagram.png)

## Data Sources: 

 - [AWS historical pricing](https://docs.aws.amazon.com/cli/latest/reference/ec2/describe-spot-price-history.html).

 - Azure price list [API](https://learn.microsoft.com/en-us/rest/api/cost-management/retail-prices/azure-retail-prices).

## Tech Diagram

![Tech diagram](https://github.com/Zesky665/DEZC_2023_Capstone/blob/main/misc/tech_diagram.png)

## Dashboard
[Link to dashboard](http://3.78.56.233:3000/public/dashboard/f2950c78-683a-4302-87e7-6d321980fda6)

![Tech diagram](https://github.com/Zesky665/DEZC_2023_Capstone/blob/main/misc/final_dashboard.png)
## Insights 
- Lower powered AWS spot instances are often as costly as on-demand. Even when available the savings are much less than typically advertized.
- Bigger instances come with bigger discounts. For example: m5a.large spot instances are 44% cheapter than on-demand. a1.medium spot instances are the same price as on-demand. 
- Azure has much bigger discounts for spot instances as well as a lot more availability of spot instances. 
## To-Do

- Add GCP Data.
- Add persistance for metabase. 
- Add data quality tests to dbt flow. 


## Acknowledgements

Thanks to the instructors: 

- [Ankush Khanna](https://www.linkedin.com/in/ankushkhanna2/)
- [Sejal Vaidya](https://www.linkedin.com/in/vaidyasejal/)
- [Victoria Perez Mola](https://www.linkedin.com/in/victoriaperezmola/)
- [Kalise Richmond](https://www.linkedin.com/in/kaliserichmond/)
- [Jeff Hale](https://www.linkedin.com/in/-jeffhale/)
- [Alexey Grigorev](https://www.linkedin.com/in/agrigorev/)

Thanks to collegues: 

- [Anna Geller](https://annageller.com/), her articles on Prefect DataOps have been a huge infuence. 
- [Andy Nelson](https://www.linkedin.com/in/andynelson1982/), for telling me about ZoomCamp and generaly being a great mentor. 
- [Matt Little](https://medium.com/strategio/using-terraform-to-create-aws-vpc-ec2-and-rds-instances-c7f3aa416133), his articles on Terraform and AWS were what made this entire project possible.  

## Contact information

- [LinkedIn](https://www.linkedin.com/in/zharko-cekovski/)
