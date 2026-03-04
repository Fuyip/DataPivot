SELECT
baswi.card_no AS `卡号`,
trade_date AS `交易时间`,
trade_money AS `交易金额`,
trade_balance AS `交易余额`,
'出' AS `交易方向`,
rival_card_no AS `交易对手卡号`,
rival_card_name AS `交易对手名称`,
ip_loc AS `IP地址`,
mac_loc AS `MAC地址`,
CASE WHEN baswi.trade_date BETWEEN t2.`最早入金涉案时间` AND t2.`最晚入金涉案时间` THEN '是' ELSE '否' END AS `是否涉案时间内`
FROM
bank_all_statements_with_info baswi
INNER JOIN(
SELECT
*
FROM
case_card cc
WHERE
cc.card_type='c02'
)t3 ON t3.card_no=baswi.card_no

INNER JOIN(
SELECT
*
FROM
`3003xpj跑分卡需求`
WHERE
`卡号`='{card_no}'
AND 关联数量>=5 AND info NOT IN('|N','0')
)t1 ON t1.info=baswi.ip_loc OR t1.info=baswi.mac_loc
LEFT JOIN(
SELECT
*
FROM
`3003xpj银行卡整体情况_0410`
)t2 ON t2.`卡号`=baswi.card_no
WHERE
baswi.dict_trade_tag='out'
ORDER BY baswi.card_no