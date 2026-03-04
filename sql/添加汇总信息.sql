UPDATE
`29-微信好友` w
LEFT JOIN(
SELECT
*
FROM
`zh-汇总查询`
WHERE `账号类型`='wx'
)t1 ON t1.`账号`=w.`主体微信号`
SET
w.`主体`=t1.`姓名`,
w.`主体来源`=t1.`来源`,
w.`主体来源账号类型`=t1.`账号类型`,
w.`身份证`=t1.`身份证号`