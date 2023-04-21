
/*
    Welcome to your first dbt model!
    Did you know that you can also configure models directly within SQL files?
    This will override configurations stated in dbt_project.yml

    Try changing "table" to "view" below
*/

{{ 
    config(
        materialized='incremental',
        unique_key=['instance_type', 'architecture']
        ) 
    
}}

WITH source_data AS (

    SELECT * FROM {{ source('capstone_db', 'raw_aws_spec_info') }}

)

SELECT DISTINCT *
FROM source_data

/*
    Uncomment the line below to remove records with null `id` values
*/

-- where id is not null
