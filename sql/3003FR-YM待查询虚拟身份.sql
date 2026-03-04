SELECT
GROUP_CONCAT(DISTINCT 机器码) AS `来源`,
账号类型,
账号,
'' AS `账号信息`
FROM
`锋刃虚拟身份`
GROUP BY 账号
UNION
SELECT
GROUP_CONCAT(DISTINCT `查询ID`) AS `来源`,
'手机号码' AS 账号类型,
`PN/IMSI` AS `账号`,
t1.info AS `账号信息`
FROM
`ym-本机历史汇报情况` lshb
LEFT JOIN(
SELECT
`PN/IMSI` AS `账号`,
CONCAT(归属省,'-',归属市,'-',运营商) AS info
FROM
`手机号匹配归属`
)t1 ON t1.`账号`=lshb.`PN/IMSI`
WHERE
t1.info IS NOT NULL
GROUP BY lshb.`PN/IMSI`