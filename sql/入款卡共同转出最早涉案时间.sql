SET @card_type = "c02";
SET @card_direction = "out";

SELECT
bs.rival_card_no AS `卡号`,
GROUP_CONCAT(DISTINCT bs.rival_card_name) AS `卡名`,
SUM(trade_money) AS `总资金`,
SUM(trade_count) AS `入款方转出笔数`,
COUNT(DISTINCT bs.card_no) AS `关联卡张数`,
CASE WHEN sd1.d_label IS NOT NULL THEN sd1.d_label ELSE (
CASE WHEN(
(CHAR_LENGTH(SUBSTRING_INDEX(bs.rival_card_name,',',1))>4 AND bs.rival_card_name NOT LIKE "%・%")
OR SUBSTRING_INDEX(bs.rival_card_name,',',1)="0" 
OR SUBSTRING_INDEX(bs.rival_card_name,',',2)="0" 
OR SUBSTRING_INDEX(bs.rival_card_name,',',1) LIKE "%财付%" 
OR SUBSTRING_INDEX(bs.rival_card_name,',',1) = "\\N" 
OR SUBSTRING_INDEX(bs.rival_card_name,',',1) LIKE "%百付%"
OR SUBSTRING_INDEX(bs.rival_card_name,',',1) LIKE "%支付%"
OR SUBSTRING_INDEX(bs.rival_card_name,',',1) LIKE "%微信%"
OR SUBSTRING_INDEX(bs.rival_card_name,',',1) LIKE "%还款%"
OR SUBSTRING_INDEX(bs.rival_card_name,',',1) LIKE "%出行%"
OR SUBSTRING_INDEX(bs.rival_card_name,',',1) LIKE "%充值%"
)
THEN '三方' ELSE NULL END)  END AS `卡类型`,
MIN(min_trade_date) AS `最早交易时间`,
MAX(max_trade_date) AS `最后交易时间`
FROM
bank_statements bs
INNER JOIN(
SELECT
card_no
FROM
case_card
WHERE
card_type=@card_type
)t1 ON t1.card_no=bs.card_no
LEFT JOIN(
SELECT
card_no,
card_type
FROM
case_card
)t2 ON t2.card_no=bs.rival_card_no
LEFT JOIN xinglian.sys_dict sd1 ON sd1.d_value=t2.card_type
LEFT JOIN(
SELECT
*
FROM
`银行卡涉案情况`
)t3 ON t3.`涉案银行卡`=t1.card_no
WHERE
dict_trade_tag=@card_direction
AND date(min_trade_date)>date(t3.`最早涉案时间`)
GROUP BY bs.dict_trade_tag,bs.rival_card_no
ORDER BY SUM(trade_money) DESC