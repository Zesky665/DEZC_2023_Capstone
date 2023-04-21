SELECT "capstone_db"."staging_aws_on_demand_prices"."instance_type" AS "instance_type", "capstone_db"."staging_aws_on_demand_prices"."on_demand_price" AS "on_demand_price", "capstone_db"."staging_aws_on_demand_prices"."provider" AS "provider"
FROM "capstone_db"."staging_aws_on_demand_prices"
LIMIT 1048575