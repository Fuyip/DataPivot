TRUNCATE bank_all_statements_turn;
INSERT IGNORE INTO `bank_all_statements_turn`
SELECT
bas.*
FROM
bank_all_statements bas

INNER JOIN(
SELECT
id
FROM
involved_bankcard_details
)t1 ON t1.id=bas.id;

INSERT IGNORE INTO `bank_all_statements_turn`(card_no,account_name,dict_trade_tag,trade_money,rival_card_no,rival_card_name,trade_date)
SELECT
rival_card_no AS `card_no`,
rival_card_name AS `account_name`,
CASE WHEN dict_trade_tag='in' THEN 'out' ELSE CASE WHEN dict_trade_tag='out' THEN 'in' ELSE '' END END AS dict_trade_tag,
trade_money,
card_no AS rival_card_no,
account_name AS rival_card_name,
trade_date
FROM
bank_all_statements bas

INNER JOIN(
SELECT
id
FROM
involved_bankcard_details
)t1 ON t1.id=bas.id