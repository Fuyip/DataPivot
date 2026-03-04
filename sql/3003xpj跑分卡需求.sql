SELECT
`卡号`,
`银行名称`,
`账户信息户名`,
ztqk.`身份证号码`,
t5.concatPhone AS `联系电话`,
t5.workPhone AS `工作电话`,
`最早入金涉案时间`,
`最晚入金涉案时间`,
`与赌客卡入金关联张数`,
`涉案入金金额`,
`交易总流水`,
t1.cnt_id AS `同身份证入款卡数量`,
'ip' AS `关联类型`,
t3.ip_loc AS `info`,
t3.ip_cnt AS `关联数量`,
t4.min_trade_date AS `最早涉案时间`,
t4.max_trade_date AS `最晚涉案时间`
FROM `3003xpj银行卡整体情况_0410` ztqk
LEFT JOIN(
SELECT
`身份证号码`,
COUNT(`身份证号码`) AS cnt_id
FROM
`3003xpj银行卡整体情况_0410`
WHERE `涉案银行卡类型`='四方(跑分)入款卡'
GROUP BY `身份证号码`
)t1 ON t1.`身份证号码`=ztqk.`身份证号码`
LEFT JOIN(
SELECT
*
FROM
bank_card_loc_info
)t2 ON t2.card_no=ztqk.`卡号`

LEFT JOIN(
SELECT
ip_loc,
COUNT(DISTINCT tt1.card_no) AS ip_cnt
FROM
bank_card_loc_info tt1

INNER JOIN(
SELECT
*
FROM
case_card
WHERE card_type='c02'
)tt2 ON tt2.card_no=tt1.card_no

WHERE tt1.ip_loc NOT IN('127.0.0.1','','-')
GROUP BY ip_loc
)t3 ON t3.ip_loc=t2.ip_loc

LEFT JOIN(
SELECT
ip_loc,
MIN(trade_date) AS min_trade_date,
MAX(trade_date) AS max_trade_date
FROM
bank_all_statements_with_info
WHERE dict_trade_tag='out'
GROUP BY ip_loc
)t4 ON t4.ip_loc=t2.ip_loc

LEFT JOIN(
SELECT
*
FROM
bank_people_info
WHERE concatPhone IS NOT NULL
GROUP BY idNum
)t5 ON t5.idNum=ztqk.`身份证号码`
WHERE
(
ztqk.`涉案银行卡类型`='四方(跑分)入款卡'
AND
YEAR(ztqk.`最晚入金涉案时间`)=2025
AND
ztqk.`交易总流水`>=1000000)OR 
ztqk.卡号 IN ('6212261709004835349',"621278283000169086","6230361213007812513","6230361213007812497","6230361213007813552","6235160006900083394","6228603800045271","6228230755264188360","6213363299982976179","6235160001900695032")

UNION

SELECT
`卡号`,
`银行名称`,
`账户信息户名`,
ztqk.`身份证号码`,
t5.concatPhone AS `联系电话`,
t5.workPhone AS `工作电话`,
`最早入金涉案时间`,
`最晚入金涉案时间`,
`与赌客卡入金关联张数`,
`涉案入金金额`,
`交易总流水`,
t1.cnt_id AS `同身份证入款卡数量`,
'mac' AS `关联类型`,
t3.mac_loc AS `info`,
t3.mac_cnt AS `关联数量`,
t4.min_trade_date AS `最早涉案时间`,
t4.max_trade_date AS `最晚涉案时间`
FROM `3003xpj银行卡整体情况_0410` ztqk
LEFT JOIN(
SELECT
`身份证号码`,
COUNT(`身份证号码`) AS cnt_id
FROM
`3003xpj银行卡整体情况_0410`
WHERE `涉案银行卡类型`='四方(跑分)入款卡'
GROUP BY `身份证号码`
)t1 ON t1.`身份证号码`=ztqk.`身份证号码`
LEFT JOIN(
SELECT
*
FROM
bank_card_loc_info
)t2 ON t2.card_no=ztqk.`卡号`

LEFT JOIN(
SELECT
mac_loc,
COUNT(DISTINCT tt1.card_no) AS mac_cnt
FROM
bank_card_loc_info tt1

INNER JOIN(
SELECT
*
FROM
case_card
WHERE card_type='c02'
)tt2 ON tt2.card_no=tt1.card_no

WHERE tt1.mac_loc NOT IN('','-','02:00:00:00:00:00')
GROUP BY mac_loc
)t3 ON t3.mac_loc=t2.mac_loc

LEFT JOIN(
SELECT
mac_loc,
MIN(trade_date) AS min_trade_date,
MAX(trade_date) AS max_trade_date
FROM
bank_all_statements_with_info
WHERE dict_trade_tag='out'
GROUP BY mac_loc
)t4 ON t4.mac_loc=t2.mac_loc

LEFT JOIN(
SELECT
*
FROM
bank_people_info
WHERE concatPhone IS NOT NULL
GROUP BY idNum
)t5 ON t5.idNum=ztqk.`身份证号码`


WHERE
(
ztqk.`涉案银行卡类型`='四方(跑分)入款卡'
AND
YEAR(ztqk.`最晚入金涉案时间`)=2025
AND
ztqk.`交易总流水`>=1000000)OR
ztqk.卡号 IN ('6212261709004835349',"621278283000169086","6230361213007812513","6230361213007812497","6230361213007813552","6235160006900083394","6228603800045271","6228230755264188360","6213363299982976179","6235160001900695032")
