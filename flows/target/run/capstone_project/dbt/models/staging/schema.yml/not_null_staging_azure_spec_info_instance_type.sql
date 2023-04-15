select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select instance_type
from "capstone_db"."dbt_zesky665"."staging_azure_spec_info"
where instance_type is null



      
    ) dbt_internal_test