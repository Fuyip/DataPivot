TRUNCATE TABLE bank_all_statements_lastest;
INSERT INTO bank_all_statements_lastest
SELECT
t2.*
FROM(
SELECT
card_no,
max(trade_date) AS max_trade_date
FROM
bank_all_statements
GROUP BY card_no)t1
INNER JOIN(
SELECT
*
FROM
bank_all_statements
)t2 ON t1.card_no=t2.card_no AND t1.max_trade_date=t2.trade_date;

DELETE 
FROM  bank_all_statements_lastest  where trade_date not in (
	SELECT trade_date from (SELECT MAX(trade_date) trade_date FROM bank_all_statements_lastest WHERE trade_date IS NOT NULL GROUP BY card_no) a
);

INSERT IGNORE INTO card_to_sys_logs
SELECT
DISTINCT
0 AS id,
card_no,
now() AS add_date
FROM
bank_all_statements_lastest
