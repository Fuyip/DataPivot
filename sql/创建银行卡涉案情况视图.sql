DROP VIEW IF EXISTS `银行卡涉案情况`;
CREATE VIEW `银行卡涉案情况` AS
SELECT
cc.card_no `涉案银行卡`,
sd1.d_label AS `涉案银行卡类型`,
ROUND(SUM(trade_money),2) AS `涉案金额`,
SUM(trade_count) AS `涉案笔数`,
SUM(CASE WHEN sd2.`d_value` IN('c02') THEN 1 ELSE 0 END) AS `与入款卡关联张数`,
SUM(CASE WHEN sd2.`d_value` IN('c06') THEN 1 ELSE 0 END) AS `与出款卡关联张数`,
SUM(CASE WHEN sd2.`d_value` IN('c30','c31') THEN 1 ELSE 0 END) AS `与赌客卡关联张数`,
SUM(CASE WHEN sd2.`d_value` IN('c09') THEN 1 ELSE 0 END) AS `与金主卡关联张数`,
SUM(CASE WHEN sd2.`d_value` IN('c09out') THEN 1 ELSE 0 END) AS `与金主卡转出方关联张数`,

MIN(min_trade_date) AS `最早涉案时间`,
MAX(max_trade_date) AS `最晚涉案时间`,
'入金' AS `关联方向`
FROM
case_card cc
INNER JOIN(
SELECT
*
FROM
bank_statements_turn
WHERE
dict_trade_tag='in'
AND card_no<>rival_card_no
)t1 ON t1.card_no=cc.card_no

LEFT JOIN(
SELECT
*
FROM
xinglian.sys_dict
)sd1 ON sd1.`d_value`=cc.card_type

INNER JOIN(
SELECT
*
FROM
case_card
)t3 ON t3.card_no=t1.rival_card_no

LEFT JOIN(
SELECT
*
FROM
xinglian.sys_dict
)sd2 ON sd2.`d_value`=t3.card_type
WHERE

-- (sd1.`d_value`='c02' AND sd2.`d_value` IN('c30','c31','c02'))-- 入款卡收赌客及其他入款卡
-- OR (sd1.`d_value` IN ('c31','c30') AND sd2.`d_value` IN('c02','c06','c30','c31'))-- 赌客收入款卡出款卡及其他赌客卡
-- OR (sd1.`d_value`='c02q' AND sd2.`d_value` IN('c30','c31','c02'))-- 未研判入款卡收赌客及其他入款卡
-- OR (sd1.`d_value`='c99' AND sd2.`d_value` IN('c30','c31','c02','c06'))-- 待研判卡
-- OR (sd1.`d_value`='c11' AND sd2.`d_value` IN('c30','c31','c02'))-- 一级洗钱
-- OR (sd1.`d_value`='c06' AND sd2.`d_value` IN('c30','c31','c02','c06'))-- 出款卡
-- OR (sd1.`d_value`='c06q' AND sd2.`d_value` IN('c30','c31','c02','c06'))-- 出款卡
-- OR (sd1.`d_value`='c04' AND sd2.`d_value` IN('c30','c31','c02'))-- 出款卡
-- OR (sd1.`d_value`='c09' AND sd2.`d_value` IN('c30','c31','c02','c06'))-- 金主卡
-- OR (sd1.`d_value`='c02in' AND sd2.`d_value` IN('c30','c31','c02','c06'))-- 核心公司卡入金来源
-- OR (sd1.`d_value`='c09out' AND sd2.`d_value` IN('c30','c31','c02','c06','c09'))-- 金主卡转出
-- OR (sd1.`d_value`='c09out2' AND sd2.`d_value` IN('c30','c31','c02','c06','c09','c09out' ))
is_sa(sd1.`d_value`,sd2.`d_value`)='是'
GROUP BY cc.card_no

UNION

SELECT
cc.card_no `涉案银行卡`,
sd1.d_label AS `涉案银行卡类型`,
ROUND(SUM(trade_money),2) AS `涉案金额`,
SUM(trade_count) AS `涉案笔数`,
SUM(CASE WHEN sd2.`d_value` IN('c02') THEN 1 ELSE 0 END) AS `与入款卡关联张数`,
SUM(CASE WHEN sd2.`d_value` IN('c06') THEN 1 ELSE 0 END) AS `与出款卡关联张数`,
SUM(CASE WHEN sd2.`d_value` IN('c30','c31') THEN 1 ELSE 0 END) AS `与赌客卡关联张数`,
SUM(CASE WHEN sd2.`d_value` IN('c09') THEN 1 ELSE 0 END) AS `与金主卡关联张数`,
SUM(CASE WHEN sd2.`d_value` IN('c09out') THEN 1 ELSE 0 END) AS `与金主卡转出方关联张数`,
MIN(min_trade_date) AS `最早涉案时间`,
MAX(max_trade_date) AS `最晚涉案时间`,
'出金' AS `关联方向`
FROM
case_card cc
INNER JOIN(
SELECT
*
FROM
bank_statements_turn
WHERE
dict_trade_tag='out'
AND card_no<>rival_card_no
)t1 ON t1.card_no=cc.card_no

LEFT JOIN(
SELECT
*
FROM
xinglian.sys_dict
)sd1 ON sd1.`d_value`=cc.card_type

INNER JOIN(
SELECT
*
FROM
case_card
)t3 ON t3.card_no=t1.rival_card_no

LEFT JOIN(
SELECT
*
FROM
xinglian.sys_dict
)sd2 ON sd2.`d_value`=t3.card_type
WHERE

-- (sd1.`d_value`='c02' AND sd2.`d_value` IN('c30','c31','c02'))-- 入款卡收赌客及其他入款卡
-- OR (sd1.`d_value` IN ('c31','c30') AND sd2.`d_value` IN('c02','c06','c30','c31'))-- 赌客收入款卡出款卡及其他赌客卡
-- OR (sd1.`d_value`='c02q' AND sd2.`d_value` IN('c30','c31','c02'))-- 未研判入款卡收赌客及其他入款卡
-- OR (sd1.`d_value`='c99' AND sd2.`d_value` IN('c30','c31','c02','c06'))-- 待研判卡
-- OR (sd1.`d_value`='c11' AND sd2.`d_value` IN('c30','c31','c02'))-- 一级洗钱
-- OR (sd1.`d_value`='c06' AND sd2.`d_value` IN('c30','c31','c02','c06'))-- 出款卡
-- OR (sd1.`d_value`='c06q' AND sd2.`d_value` IN('c30','c31','c02','c06'))-- 出款卡
-- OR (sd1.`d_value`='c04' AND sd2.`d_value` IN('c30','c31','c02'))-- 出款卡
-- OR (sd1.`d_value`='c09' AND sd2.`d_value` IN('c30','c31','c02','c06'))-- 金主卡
-- OR (sd1.`d_value`='c02in' AND sd2.`d_value` IN('c30','c31','c02','c06'))-- 核心公司卡入金来源
-- OR (sd1.`d_value`='c09out' AND sd2.`d_value` IN('c30','c31','c02','c06','c09'))-- 金主卡转出
-- OR (sd1.`d_value`='c09out2' AND sd2.`d_value` IN('c30','c31','c02','c06','c09','c09out' ))
is_sa(sd1.`d_value`,sd2.`d_value`)='是'
GROUP BY cc.card_no