
    
    

select
    (time_stamp || '-' || prod_desc || '-' || az) as unique_field,
    count(*) as n_records

from "capstone_db"."dbt_zesky665"."staging_azure_spot_prices"
where (time_stamp || '-' || prod_desc || '-' || az) is not null
group by (time_stamp || '-' || prod_desc || '-' || az)
having count(*) > 1


