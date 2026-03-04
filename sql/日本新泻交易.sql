SELECT
baswi.card_no AS `交易银行卡卡号`,
baswi.trade_date AS `交易时间`,
baswi.trade_money AS `交易金额`,
baswi.trade_balance AS `交易余额`,
baswi.dict_trade_tag AS `交易对手方向`,
baswi.rival_card_no AS `交易对手卡号`,
baswi.rival_card_name AS `交易对手姓名`,
baswi.summary_description AS `摘要`,
baswi.remark AS `备注`,
baswi.ip_loc AS `交易IP`,
baswi.mac_loc AS `交易MAC`
FROM
bank_all_statements_with_info baswi

INNER JOIN(
SELECT
DISTINCT
`卡号` AS card_no
FROM
`跑分人员总表`
UNION
SELECT
DISTINCT
card_no
FROM
`预冻结卡境外ip`
)t1 ON t1.card_no=baswi.card_no

WHERE
baswi.ip_loc='118.0.193.36'
AND
baswi.mac_loc='00:50:56:BF:57:04'