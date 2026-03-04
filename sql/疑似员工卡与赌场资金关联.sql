SELECT
t3.card_no AS `卡号`,
t3.source AS `卡名`,
sd2.d_label AS `卡类型`,
t2.trade_date AS `交易时间`,
t2.trade_money AS `交易金额`,
t2.trade_balance AS `交易余额`,
t2.dict_trade_tag AS `交易方向`,
t1.card_no AS `对手卡号`,
t1.source AS `对手卡名`,
sd1.d_label AS `对手卡标签`,
t1.bank_name AS `对手卡归属`,
t2.transaction_outlet_name AS `交易网点`,
t2.remark AS `交易备注`
FROM(
SELECT
*
FROM
case_card
WHERE
card_type='c15q'
)t1
INNER JOIN(
SELECT
*
FROM
bank_all_statements
)t2 ON t2.rival_card_no=t1.card_no
LEFT JOIN(
SELECT
*
FROM
case_card
)t3 ON t3.card_no=t2.card_no
LEFT JOIN xinglian.sys_dict sd1 ON sd1.d_value=t1.card_type
LEFT JOIN xinglian.sys_dict sd2 ON sd2.d_value=t3.card_type