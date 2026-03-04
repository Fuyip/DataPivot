SELECT
MIN(min_trade_date) AS `最早交易时间`,
MAX(max_trade_date) AS `最晚交易时间`,
SUM(trade_money) AS `总交易资金`,
COUNT(trade_count) AS `总交易笔数`,
COUNT(DISTINCT bs.card_no) AS `总交易银行卡张数`,
SUM(CASE WHEN t2.card_type='c02' THEN 1 ELSE 0 END) AS `入款卡关联张数`,
SUM(CASE WHEN t2.card_type='c11' AND t3.card_no IS NULL THEN 1 ELSE 0 END) AS `洗钱卡关联张数`,
COUNT(DISTINCT t4.card_no) AS `与境外交易洗钱卡关联数量`,
bs.rival_card_no AS `对手交易银行卡`,
bs.rival_card_name AS `对手交易银行卡名称`,
t1.card_type
FROM
bank_statements_turn bs

INNER JOIN(
SELECT
*
FROM
case_card
WHERE
card_type IN('c02','c11')
)tt ON tt.card_no=bs.card_no


LEFT JOIN(
SELECT
DISTINCT
a.card_no,
a.rival_card_no
FROM(
SELECT
bst.card_no,
bst.rival_card_no
FROM
bank_statements_turn bst
INNER JOIN(
SELECT
*
FROM
case_card
WHERE
card_type='c11'
)tt ON tt.card_no=bst.card_no
WHERE
dict_trade_tag='in')a
)t3 ON t3.card_no=bs.card_no AND t3.rival_card_no=bs.rival_card_no


LEFT JOIN(
SELECT
*
FROM
case_card
)t1 ON t1.card_no=bs.rival_card_no

LEFT JOIN(
SELECT
*
FROM
case_card
)t2 ON t2.card_no=bs.card_no

LEFT JOIN(
SELECT
*
FROM
`预冻结卡境外ip`
GROUP BY card_no
)t4 ON t4.card_no=bs.card_no


WHERE
dict_trade_tag='out'

GROUP BY bs.rival_card_no
HAVING `总交易笔数`>=5
