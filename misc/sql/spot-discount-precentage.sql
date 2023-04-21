with average as (SELECT "capstone_db"."prod_aws_spot_catalog"."instance_type" AS "instance_type", AVG("capstone_db"."prod_aws_spot_catalog"."spot_price") AS "avg"
FROM "capstone_db"."prod_aws_spot_catalog"
GROUP BY "capstone_db"."prod_aws_spot_catalog"."instance_type"
ORDER BY "capstone_db"."prod_aws_spot_catalog"."instance_type" ASC)

SELECT average.instance_type, (1-(avg/on_demand_price))*100 as "Discount %"
FROM average
LEFT JOIN "capstone_db"."staging_aws_on_demand_prices" as on_demand ON on_demand.instance_type = average.instance_type
ORDER BY "Discount %" DESC