SELECT
group_concat(DISTINCT baswi.card_no) AS `卡号`,

CONCAT(YEAR(trade_date),'-',MONTH(trade_date),'-',DAY(trade_date)) AS `交易日期`,
ip_loc AS `IP地址`,
COUNT(DISTINCT baswi.card_no) AS `关联银行卡张数`
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
)t1 ON t1.info=baswi.ip_loc

LEFT JOIN(
SELECT
*
FROM
`3003xpj银行卡整体情况_0410`
)t2 ON t2.`卡号`=baswi.card_no

WHERE
baswi.dict_trade_tag='out'
GROUP BY ip_loc,YEAR(trade_date),MONTH(trade_date),DAY(trade_date)
ORDER BY ip_loc,baswi.trade_date DESC