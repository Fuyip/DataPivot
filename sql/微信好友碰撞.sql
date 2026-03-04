SELECT
w.`好友微信号`,
GROUP_CONCAT(DISTINCT CONCAT(t1.`姓名`,'-',w.`好友备注`)),
COUNT(DISTINCT w.`主体微信号`)
FROM
`29-微信好友` w
LEFT JOIN(
SELECT
*
FROM
`人员总体归纳`
)t1 ON t1.`账号`=w.`主体微信号`
WHERE w.`好友微信号` NOT LIKE 'gh_%'
GROUP BY
w.`好友微信号`
ORDER BY COUNT(DISTINCT w.`主体微信号`) DESC