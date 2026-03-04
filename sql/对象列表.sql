SELECT
a1.*,
a2.card_cnt AS `同身份证入款卡数量`,
a3.concatPhone AS `联系方式`
FROM(
SELECT
ztqk.卡号,
ztqk.`银行名称`,
ztqk.`账户信息户名`,
ztqk.`身份证号码`,
ztqk.`最早入金涉案时间`,
ztqk.`最晚入金涉案时间`,
ztqk.`与赌客卡入金关联张数`,
ztqk.`涉案入金金额`,
ztqk.`交易总流水`
FROM
`3003xpj银行卡整体情况_0410` ztqk
INNER JOIN(
SELECT
tt1.*,
CASE WHEN ttt1.`卡号` IS NOT NULL THEN '命中' ELSE '未命中' END AS `ip命中情况`,
CASE WHEN ttt2.`卡号` IS NOT NULL THEN '命中' ELSE '未命中' END AS `mac命中情况`
FROM
bank_card_loc_info tt1
LEFT JOIN(
SELECT
*
FROM
`3003xpj跑分卡需求`
WHERE
`卡号`='{card_no}'
AND `关联类型`='ip'
AND 关联数量>=5 AND info NOT IN('|N','0')
)ttt1 ON ttt1.info=tt1.ip_loc

LEFT JOIN(
SELECT
*
FROM
`3003xpj跑分卡需求`
WHERE
`卡号`='{card_no}'
AND `关联类型`='mac'
AND 关联数量>=5 AND info NOT IN('|N','0')
)ttt2 ON ttt2.info=tt1.mac_loc

WHERE ttt1.`卡号` IS NOT NULL OR ttt2.`卡号` IS NOT NULL
)t1 ON t1.card_no=ztqk.`卡号`

WHERE
ztqk.`涉案银行卡类型`='四方(跑分)入款卡'
GROUP BY `卡号`)a1
LEFT JOIN(
SELECT
`身份证号码`,

COUNT(`卡号`) AS card_cnt
FROM
`3003xpj银行卡整体情况_0410`
WHERE
`涉案银行卡类型`='四方(跑分)入款卡'
GROUP BY `身份证号码`
)a2 ON a2.`身份证号码`=a1.`身份证号码`
LEFT JOIN(
SELECT
*
FROM
bank_people_info
GROUP BY
idNum
)a3 ON a3.idNum=a1.`身份证号码`