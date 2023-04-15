/*
    Welcome to your first dbt model!
    Did you know that you can also configure models directly within SQL files?
    This will override configurations stated in dbt_project.yml

    Try changing "table" to "view" below
*/



WITH source_data AS (

    SELECT * FROM "capstone_db"."public"."raw_azure_spec_info"

)

SELECT DISTINCT *
FROM source_data

/*
    Uncomment the line below to remove records with null `id` values
*/

-- where id is not null