select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select time_stamp
from "capstone_db"."dbt_zesky665"."staging_azure_spot_prices"
where time_stamp is null



      
    ) dbt_internal_test