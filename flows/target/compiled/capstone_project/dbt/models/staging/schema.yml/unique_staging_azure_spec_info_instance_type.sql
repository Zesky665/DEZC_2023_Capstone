
    
    

select
    instance_type as unique_field,
    count(*) as n_records

from "capstone_db"."dbt_zesky665"."staging_azure_spec_info"
where instance_type is not null
group by instance_type
having count(*) > 1


