SET
@source='e2dd93d89738';
SELECT
*
FROM
`ym-设备信息`
WHERE
MAC LIKE CONCAT('%',@source,'%')
OR
PN LIKE CONCAT('%',@source,'%');
SELECT
*
FROM
`ym-查询路径`
WHERE
`附近wifimac` LIKE CONCAT('%',@source,'%');

SELECT
*
FROM
`ym-路由设备`
WHERE
`MAC` LIKE CONCAT('%',@source,'%');
