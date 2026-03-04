TRUNCATE TABLE involved_bankcard_details;

INSERT INTO involved_bankcard_details
SELECT
DISTINCT
0 AS `uid`,
bas.id AS `id`,
t2.card_type AS `card_type`,
bas.dict_trade_tag AS `dict_trade_tag`,
'c31' AS `dict_card_type`,
'赌客交易' AS `type`
FROM 
bank_all_statements bas

INNER JOIN(
SELECT
DISTINCT
card_no AS cardNo

FROM
case_card
WHERE
card_type IN('c30','c31')
)t1 ON t1.cardNo=bas.rival_card_no

LEFT JOIN(
SELECT
card_no,
card_type
FROM
case_card
)t2 ON t2.card_no=bas.card_no;

INSERT INTO involved_bankcard_details
SELECT
DISTINCT
0 AS `uid`,
bas.id AS `id`,
t2.card_type AS `card_type`,
bas.dict_trade_tag AS `dict_trade_tag`,
'c02' AS `dict_card_type`,
'入款卡交易' AS `type`
FROM 
bank_all_statements bas
INNER JOIN(
SELECT
DISTINCT
card_no AS cardNo

FROM
case_card
WHERE
card_type='c02'
)t1 ON t1.cardNo=bas.rival_card_no

LEFT JOIN(
SELECT
card_no,
card_type
FROM
case_card
)t2 ON t2.card_no=bas.card_no;

INSERT INTO involved_bankcard_details
SELECT
DISTINCT
0 AS `uid`,
bas.id AS `id`,
t2.card_type AS `card_type`,
bas.dict_trade_tag AS `dict_trade_tag`,
'c15q' AS `dict_card_type`,
'疑似员工卡交易' AS `type`
FROM 
bank_all_statements bas
INNER JOIN(
SELECT
DISTINCT
card_no AS cardNo

FROM
case_card
WHERE
card_type='c15q'
)t1 ON t1.cardNo=bas.rival_card_no

LEFT JOIN(
SELECT
card_no,
card_type
FROM
case_card
)t2 ON t2.card_no=bas.card_no;

INSERT INTO involved_bankcard_details
SELECT
DISTINCT
0 AS `uid`,
bas.id AS `id`,
t2.card_type AS `card_type`,
bas.dict_trade_tag AS `dict_trade_tag`,
'c15' AS `dict_card_type`,
'员工卡交易' AS `type`
FROM 
bank_all_statements bas
INNER JOIN(
SELECT
DISTINCT
card_no AS cardNo

FROM
case_card
WHERE
card_type='c15'
)t1 ON t1.cardNo=bas.rival_card_no
LEFT JOIN(
SELECT
card_no,
card_type
FROM
case_card
)t2 ON t2.card_no=bas.card_no;

INSERT INTO involved_bankcard_details
SELECT
DISTINCT
0 AS `uid`,
bas.id AS `id`,
t2.card_type AS `card_type`,
bas.dict_trade_tag AS `dict_trade_tag`,
'c06' AS `dict_card_type`,
'出款卡交易' AS `type`
FROM
bank_all_statements bas
INNER JOIN(
SELECT
DISTINCT
card_no AS cardNo

FROM
case_card
WHERE
card_type='c06'
)t1 ON t1.cardNo=bas.rival_card_no
LEFT JOIN(
SELECT
card_no,
card_type
FROM
case_card
)t2 ON t2.card_no=bas.card_no;

INSERT INTO involved_bankcard_details
SELECT
DISTINCT
0 AS `uid`,
bas.id AS `id`,
t2.card_type AS `card_type`,
bas.dict_trade_tag AS `dict_trade_tag`,
'c11' AS `dict_card_type`,
'一级洗钱卡交易' AS `type`
FROM
bank_all_statements bas
INNER JOIN(
SELECT
DISTINCT
card_no AS cardNo
FROM
case_card
WHERE
card_type='c11'
)t1 ON t1.cardNo=bas.rival_card_no

LEFT JOIN(
SELECT
card_no,
card_type
FROM
case_card
)t2 ON t2.card_no=bas.card_no;

INSERT INTO involved_bankcard_details
SELECT
DISTINCT
0 AS `uid`,
bas.id AS `id`,
t2.card_type AS `card_type`,
bas.dict_trade_tag AS `dict_trade_tag`,
'c09' AS `dict_card_type`,
'金主卡交易' AS `type`
FROM
bank_all_statements bas
INNER JOIN(
SELECT
DISTINCT
card_no AS cardNo
FROM
case_card
WHERE
card_type='c09'
)t1 ON t1.cardNo=bas.rival_card_no

LEFT JOIN(
SELECT
card_no,
card_type
FROM
case_card
)t2 ON t2.card_no=bas.card_no;
INSERT INTO involved_bankcard_details
SELECT
DISTINCT
0 AS `uid`,
bas.id AS `id`,
t2.card_type AS `card_type`,
bas.dict_trade_tag AS `dict_trade_tag`,
'c09out' AS `dict_card_type`,
'金主卡转出方交易' AS `type`
FROM
bank_all_statements bas
INNER JOIN(
SELECT
DISTINCT
card_no AS cardNo
FROM
case_card
WHERE
card_type='c09'
)t1 ON t1.cardNo=bas.rival_card_no

LEFT JOIN(
SELECT
card_no,
card_type
FROM
case_card
)t2 ON t2.card_no=bas.card_no;