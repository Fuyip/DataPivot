SELECT
bas.card_no AS `卡号`,
t2.`银行名称`,
t2.`账户信息户名`,
t2.`身份证号码`,
t2.`涉案银行卡类型`,
bas.trade_money AS `交易金额`,
bas.trade_balance AS `交易余额`,
bas.trade_date AS `交易时间`,
bas.dict_trade_tag AS `交易标识`,
bas.rival_card_no AS `交易对手账号`,
t3.source AS `对手卡姓名`,
sd.d_label AS `对手卡标识`,
bas.ip_loc AS `交易ip地址`,
bas.mac_loc AS `交易mac地址`,
t1.`国家`,
t1.`省`,
t1.`城市`
FROM
bank_all_statements bas
INNER JOIN(
SELECT
COUNT(DISTINCT a.card_no) AS `卡数量`,
t1.ip_loc,
t1.mac_loc,
a.`国家`,
a.`省`,
a.`城市`
FROM `预冻结卡境外ip` a

LEFT JOIN(
SELECT
*
FROM
bank_card_loc_info
WHERE
mac_loc NOT IN('0','|N','DISGRCUPSDI','DISGRCUPS','','00-00-00-00-00-00')
)t1 ON t1.card_no=a.card_no

WHERE
t1.ip_loc IS NOT NULL
GROUP BY
t1.ip_loc,t1.mac_loc
HAVING
COUNT(DISTINCT a.card_no)>2
)t1 ON t1.ip_loc=bas.ip_loc AND t1.mac_loc=bas.mac_loc
LEFT JOIN(
SELECT
*
FROM
`3003xpj银行卡整体情况_0812`
)t2 ON t2.`卡号`=bas.card_no
LEFT JOIN(
SELECT
*
FROM
case_card
)t3 ON t3.card_no=bas.rival_card_no
LEFT JOIN xinglian.sys_dict sd ON sd.d_value=t3.card_type
WHERE
bas.dict_trade_tag='out'