SELECT
t1.ip_loc AS `ip地址`,
t1.`ip命中情况`,
t1.mac_loc AS `mac地址`,
t1.`mac命中情况`,
ztqk.`卡号`,
ztqk.`银行名称`,
ztqk.`涉案银行卡类型`,
ztqk.`账户信息户名`,
ztqk.`身份证号码`
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