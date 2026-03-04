SET
@source='3c846a35fe28';
SELECT
*
FROM
export_routes_table
WHERE
REPLACE(`出口路由地址`,'-','')=@source