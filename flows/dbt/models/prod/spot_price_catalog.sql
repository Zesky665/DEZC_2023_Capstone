
/*
    Welcome to your first dbt model!
    Did you know that you can also configure models directly within SQL files?
    This will override configurations stated in dbt_project.yml

    Try changing "table" to "view" below
*/

{{ config(materialized='table') }}

with aws_spot_catalog as (
    SELECT  
        instance_type,
        spot_price,
        provider,
        prod_desc,
        vpc,
        memory,
        az,
        time_stamp
    FROM
    {{ ref('prod_aws_spot_catalog') }}
),

azure_spot_catalog as (
    SELECT  
        instance_type,
        spot_price,
        provider,
        prod_desc,
        vpc,
        memory,
        az,
        time_stamp
    FROM
    {{ ref('prod_azure_spot_catalog') }}
),

catalog as (

    SELECT * FROM aws_spot_catalog
    UNION
    SELECT * FROM azure_spot_catalog
)

select *
from catalog