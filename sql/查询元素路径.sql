SET @object='';
SELECT
fr.机器码,
fr.特征,
fr.身份,
t1.mac AS '路由器出口路由',
t2.设备名称,
t2.mac,
t2.PN

FROM
fengren fr
LEFT JOIN(
SELECT
机器码,
出口路由地址 AS mac
FROM
export_routes_table
UNION
SELECT
NULL AS 机器码,
附近wifimac AS mac
FROM
`ym-查询路径`
)t1 ON t1.机器码=fr.机器码
LEFT JOIN(
SELECT
*
FROM
`ym-路由设备`
)t2 ON t2.设备MAC=replace(t1.mac,'-','')