SELECT
出口路由地址,
MIN(最后记录时间),
MAX(最后记录时间),
COUNT(DISTINCT ert.机器码),
COUNT(DISTINCT CASE WHEN t1.is_important=1 THEN t1.机器码 ELSE NULL END)
FROM
export_routes_table ert
LEFT JOIN(
SELECT
*
FROM
fengren
)t1 ON t1.机器码=ert.`机器码`
WHERE
ert.`最后记录时间` IS NOT NULL
GROUP BY
出口路由地址
ORDER BY
COUNT(DISTINCT ert.机器码) DESC