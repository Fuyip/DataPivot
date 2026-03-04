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
t3.source AS `对手姓名`,
sd.d_label AS `对手银行卡性质`

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
bank_all_statements
)t2 ON t2.card_no=yhk.卡号

INNER JOIN(
SELECT
*
FROM
case_card
)t3 ON t3.card_no=t2.rival_card_no

LEFT JOIN xinglian.sys_dict sd ON sd.d_value=t3.card_type