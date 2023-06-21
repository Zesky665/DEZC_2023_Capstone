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

![Tech diagram](https://github.com/Zesky665/DEZC_2023_Capstone/blob/final/misc/tech_diagram.png)

## Dashboard
[Link to dashboard](http://3.78.56.233:3000/public/dashboard/f2950c78-683a-4302-87e7-6d321980fda6)

![Tech diagram](https://github.com/Zesky665/DEZC_2023_Capstone/blob/main/misc/final_dashboard.png)
## Insights 
- Lower powered AWS spot instances are often as costly as on-demand. Even when available the savings are much less than typically advertized.
- Bigger instances come with bigger discounts. For example: m5a.large spot instances are 44% cheapter than on-demand. a1.medium spot instances are the same price as on-demand. 
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
