
/*
    Welcome to your first dbt model!
    Did you know that you can also configure models directly within SQL files?
    This will override configurations stated in dbt_project.yml

    Try changing "table" to "view" below
*/

{{ 
    config(
        materialized='incremental',
        unique_key=['instance_type', 'az', 'time_stamp', 'architecture'],
        dist='instance_type',
        sort='time_stamp' 
        ) 
    
}}


with aws_spot_prices as (

    SELECT DISTINCT * FROM {{ ref('staging_aws_spot_prices') }}

),

aws_spec_info as (

    SELECT DISTINCT * FROM {{ ref('staging_aws_spec_info') }}

),

source_data as (

    SELECT p.instance_type, 
       p.provider,
       s.vpc,
       s.cpu_speed,
       s.memory,
       p.spot_price,
       p.time_stamp,
       p.az,
       p.prod_desc,
       s.architecture
    FROM aws_spot_prices as p
    LEFT OUTER JOIN aws_spec_info as s 
    ON s.instance_type = p.instance_type 
)

select *
from source_data

/*
    Uncomment the line below to remove records with null `id` values
*/

-- where id is not null
