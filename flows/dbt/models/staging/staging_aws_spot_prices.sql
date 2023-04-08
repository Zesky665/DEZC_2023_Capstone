
/*
    Welcome to your first dbt model!
    Did you know that you can also configure models directly within SQL files?
    This will override configurations stated in dbt_project.yml

    Try changing "table" to "view" below
*/

{{ config(materialized='table') }}

WITH source_data AS (

    SELECT * FROM {{ source('capstone_db', 'raw_aws_spot_prices') }}

)

SELECT DISTINCT *
FROM source_data

/*
    Uncomment the line below to remove records with null `id` values
*/

-- where id is not null
