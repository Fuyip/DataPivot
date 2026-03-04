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
t4.`银行名称` AS `对手银行名称`,
t4.`账户信息户名` AS `对手账户信息户名`,
t4.`身份证号码` AS `对手身份证号码`,
t3.mac_loc AS `同MAC`
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
DISTINCT
mac_loc
FROM(
SELECT
DISTINCT
card_no,
ip_loc,
mac_loc,
t1.country,
t1.city
FROM
bank_card_loc_info bcli

INNER JOIN(
SELECT
*
FROM
ali_ip_loc
WHERE
country<>''
AND
(
country<>'中国'
OR
(country='中国' AND city IN ('台湾','香港')))
)t1 ON t1.ip=bcli.ip_loc)a)t3 ON t3.mac_loc=t2.mac_loc

LEFT JOIN(
SELECT
*
FROM
`3003xpj银行卡整体情况_0812`
)t4 ON t4.卡号=t2.card_no
WHERE
t3.mac_loc NOT IN('','02:00:00:00:00:00','0')
