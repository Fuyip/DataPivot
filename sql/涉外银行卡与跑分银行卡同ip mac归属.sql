SELECT
a.card_no AS `涉外人员卡号`,
t3.`银行名称` AS `涉外银行名称`,
t3.`账户信息户名` AS `涉外账户信息户名`,
t3.`身份证号码` AS `涉外身份证号码`,
t3.`涉案银行卡类型` AS `涉外涉案银行卡类型`,

t2.card_no AS `跑分银行卡账号`,
t4.`银行名称` AS `跑分银行名称`,
t4.`账户信息户名` AS `跑分账户信息户名`,
t4.`身份证号码` AS `跑分身份证号码`,
t4.`涉案银行卡类型` AS `跑分涉案银行卡类型`,
t2.ip_loc AS `同ip归属`,
t2.mac_loc AS `同mac归属`,
t5.country AS `ip归属国家`,
t5.city AS `ip归属城市`
FROM(
SELECT DISTINCT card_no FROM `预冻结卡境外ip`) a
INNER JOIN(
SELECT
*
FROM
bank_card_loc_info)t1 ON t1.card_no=a.card_no


INNER JOIN(
SELECT
t2.*
FROM
`跑分团伙身份证` sfz

INNER JOIN(
SELECT
*
FROM
`3003xpj银行卡整体情况_0812`
)t1 ON t1.`身份证号码`=sfz.`身份证号码`
INNER JOIN(
SELECT
*
FROM
bank_card_loc_info
WHERE mac_loc NOT IN('','02:00:00:00:00:00','0'))t2 ON t2.card_no=t1.`卡号`
)t2 ON t2.ip_loc=t1.ip_loc AND t2.mac_loc=t1.mac_loc
LEFT JOIN(
SELECT
*
FROM
`3003xpj银行卡整体情况_0812`
)t3 ON t3.卡号=a.card_no
LEFT JOIN(
SELECT
*
FROM
`3003xpj银行卡整体情况_0812`
)t4 ON t4.卡号=t2.card_no
LEFT JOIN(
SELECT
*
FROM
ali_ip_loc
)t5 ON t5.ip=t2.ip_loc
WHERE
a.card_no<>t2.card_no