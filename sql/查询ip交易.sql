SELECT
baswi.card_no AS `银行卡号`,
account_name AS `户主`,
trade_date AS `交易时间`,
trade_money AS `交易金额`,
dict_trade_tag AS `交易方向`,
rival_card_no AS `交易对手卡号`,
rival_card_name AS `交易对手户名`,
transaction_outlet_name AS `交易网点`,
ip_loc AS `IP地址`,
mac_loc AS `MAC地址`

FROM
bank_all_statements_with_info baswi
INNER JOIN(
SELECT
*
FROM
case_card
WHERE
card_type = 'c02'
)t1 ON t1.card_no=baswi.card_no