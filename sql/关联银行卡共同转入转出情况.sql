SELECT
COUNT(DISTINCT CASE WHEN `身份证号码` LIKE '41132%' THEN `身份证号码` ELSE NULL END) AS `与桐柏关联数量`,
SUM(CASE WHEN `身份证号码` LIKE '41132%' THEN 1 ELSE 0 END) AS `与桐柏关联笔数`,

COUNT(DISTINCT card_no) AS `关联数量`,
GROUP_CONCAT(DISTINCT concat(`账户信息户名`,'-',card_no)) AS `关联银行卡`,

dict_trade_tag AS `交易标识`,
SUM(trade_money) AS `总交易金额`,
COUNT(id) AS `交易笔数`,
rival_card_no AS `交易对手方`,
rival_card_name AS `交易对手方姓名`,
MIN(trade_date) AS `最早交易时间`,
MAX(trade_date) AS `最晚交易时间`
FROM
bank_all_statements bas
INNER JOIN(
SELECT
`卡号`,
`账户信息户名`,
`身份证号码`
from(
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
`卡号`='6228480727108641877'
AND `关联类型`='ip'
AND 关联数量>=5 AND info NOT IN('|N','0')
)ttt1 ON ttt1.info=tt1.ip_loc

LEFT JOIN(
SELECT
*
FROM
`3003xpj跑分卡需求`
WHERE
`卡号`='6228480727108641877'
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
)a3 ON a3.idNum=a1.`身份证号码`)a)t1 ON t1.`卡号`=bas.card_no
WHERE rival_card_no IS NOT NULL
GROUP BY rival_card_no,dict_trade_tag
ORDER BY COUNT(DISTINCT card_no) DESC