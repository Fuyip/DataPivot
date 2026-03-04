SELECT
yhk.`卡号` AS `跑分人员卡号`,
yhk.银行名称,
yhk.`账户信息户名`,
yhk.`身份证号码`,
t2.dict_trade_tag AS `交易方向`,
t2.trade_money AS `交易金额`,
t2.trade_balance AS `交易余额`,
t2.trade_date AS `交易时间`,
t2.rival_card_no AS `交易对手账号`,
t2.ip_loc,
t2.mac_loc
FROM
`3003xpj银行卡整体情况_0812` yhk
INNER JOIN(
SELECT
*
FROM
`跑分团伙身份证`
)t1 ON t1.`身份证号码`=yhk.`身份证号码`
INNER JOIN(
SELECT
*
FROM
bank_all_statements_with_info
WHERE
dict_trade_tag='out'
)t2 ON t2.card_no=yhk.卡号
