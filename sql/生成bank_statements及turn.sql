TRUNCATE TABLE bank_statements;
INSERT INTO bank_statements(id,case_no,card_no,card_name,dict_trade_tag,rival_card_no,rival_card_name,merchant_name,trade_money,trade_count,min_trade_date,max_trade_date)
SELECT
0 AS `id`,
'6151' AS `case_no`,
bas.card_no AS `card_no`,
MAX(t_bai.accountOpeningName) AS `card_name`,
bas.dict_trade_tag AS `dict_trade_tag`,
bas.rival_card_no AS `rival_card_no`,
MAX(bas.rival_card_name) AS `rival_card_name`,
MAX(bas.merchant_name) AS `merchant_name`,
SUM(trade_money) AS `trade_money`,
COUNT(id) AS `trade_count`,
MIN(trade_date) AS `min_trade_date`,
MAX(trade_date) AS `max_trade_date`
FROM bank_all_statements bas
LEFT JOIN(
SELECT
transactionCardNum,
MAX(accountOpeningName) AS accountOpeningName
FROM
bank_account_info
GROUP BY transactionCardNum
)t_bai ON t_bai.transactionCardNum=bas.card_no
GROUP BY card_no,dict_trade_tag,rival_card_no;
TRUNCATE TABLE bank_statements_turn;
INSERT INTO
bank_statements_turn
SELECT
bs.*,
'正' AS `situation`
FROM
bank_statements bs;

INSERT INTO bank_statements_turn           
SELECT
0 AS id,
'6151' AS case_no,
bs.rival_card_no AS card_no,
bs.rival_card_name AS card_name,
CASE bs.dict_trade_tag WHEN 'in' THEN 'out'
WHEN 'out' THEN 'in'
ELSE bs.dict_trade_tag END AS `dict_trade_tag`,
bs.card_no AS rival_card_no,
bs.card_name AS rival_card_name,
bs.merchant_name AS `merchant_name`,
bs.trade_money,
bs.trade_count,
bs.min_trade_date,
bs.max_trade_date,
'反' AS `situation`
FROM
bank_statements bs

INNER JOIN(
SELECT
card_no
FROM
case_card
)ttmp ON ttmp.card_no=bs.rival_card_no

WHERE NOT EXISTS(
SELECT
id,
card_no,
dict_trade_tag,
rival_card_no
FROM
bank_statements tbs
WHERE tbs.card_no=bs.rival_card_no
AND tbs.rival_card_no=bs.card_no
AND (CASE bs.dict_trade_tag WHEN 'in' THEN 'out'
WHEN 'out' THEN 'in'
ELSE bs.dict_trade_tag END)=tbs.dict_trade_tag
);