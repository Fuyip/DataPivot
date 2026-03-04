SELECT
DISTINCT
yhk.`卡号` AS `跑分人员卡号`,
yhk.`账户信息户名`,
yhk.`总入金金额`,
yhk.`最早入金涉案时间`,
yhk.`最晚入金涉案时间`
-- yhk.`卡号` AS `跑分人员卡号`,
-- yhk.银行名称,
-- yhk.`账户信息户名`,
-- yhk.`身份证号码`,
-- t2.dict_trade_tag AS `交易方向`,
-- t2.trade_money AS `交易金额`,
-- t2.trade_balance AS `交易余额`,
-- t2.trade_date AS `交易时间`,
-- t2.rival_card_no AS `交易对手账号`
FROM
`3003xpj银行卡整体情况_0410` yhk
INNER JOIN(
SELECT
*
FROM
bank_all_statements
)t2 ON t2.card_no=yhk.卡号
INNER JOIN(
SELECT
DISTINCT
card_no
FROM
`预冻结卡境外ip`
)t3 ON t3.card_no=t2.rival_card_no
WHERE
yhk.`涉案银行卡类型`='四方(跑分)入款卡'
AND
YEAR(`最晚入金涉案时间`)>=2024
AND yhk.`总入金金额`>=1000000