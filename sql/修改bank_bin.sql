UPDATE
xinglian.bank_bin
SET
bank_name='河北省农村信用社联合社'
WHERE
bank_name_code='HBRCU';
UPDATE
xinglian.bank_bin
SET
bank_name='广西壮族自治区农村信用社联合社'
WHERE
bank_name_code='GXRCU';

UPDATE
xinglian.bank_bin
SET
bank_name='湖南省农村信用社联合社'
WHERE
bin IN ('621458','621539','622169','622906','623090');

UPDATE
xinglian.bank_bin
SET
bank_name='吉林农信联合社'
WHERE
bin IN ('621531','622935');

UPDATE
xinglian.bank_bin
SET
bank_name='江西农信联合社'
WHERE
bin IN ('622682');

UPDATE
xinglian.bank_bin
SET
bank_name='新疆维吾尔自治区农村信用社联合社'
WHERE
bin IN ('621008','621287');

UPDATE
xinglian.bank_bin
SET
bank_name='泰隆城市信用社'
WHERE
bin IN ('621480','622141');

UPDATE
xinglian.bank_bin
SET
bank_name='山东省农村信用社联合社'
WHERE
bin IN ('622319');

INSERT INTO xinglian.sy_bank
SELECT
0 AS id,
'新疆维吾尔自治区农村信用社联合社' AS from_bank,
'新疆自治区农村信用联社' AS `to_bank`,
'jz' AS sys,
0 AS is_delete;

UPDATE
xinglian.bank_bin
SET
bank_name='招商银行'
WHERE
bank_name_code='CMB';

UPDATE
xinglian.bank_bin
SET
bank_name='上饶银行'
WHERE
bank_name_code='SRBANK';

UPDATE
xinglian.bank_bin
SET
bank_name='成都银行'
WHERE
bank_name_code='CDCB';

UPDATE
xinglian.bank_bin
SET
bank_name='东莞银行'
WHERE
bank_name_code='BOD';

UPDATE
xinglian.bank_bin
SET
bank_name='富滇银行'
WHERE
bank_name_code='FDB';

UPDATE
xinglian.bank_bin
SET
bank_name='张家口银行'
WHERE
bank_name_code='ZJKCCB';

UPDATE
xinglian.bank_bin
SET
bank_name='四川天府银行'
WHERE
bank_name_code='CGNB';

UPDATE
xinglian.bank_bin
SET
bank_name='桂林银行'
WHERE
bank_name_code='GLBANK';

UPDATE
xinglian.bank_bin
SET
bank_name='浙商银行'
WHERE
bank_name_code='CZBANK';

INSERT INTO xinglian.sy_bank
SELECT
0 AS id,
'成都商业银行' AS from_bank,
'成都银行' AS `to_bank`,
'jz' AS sys,
0 AS is_delete;

INSERT INTO xinglian.sy_bank
SELECT
0 AS id,
'东莞银行' AS from_bank,
'东莞银行股份有限公司' AS `to_bank`,
'jz' AS sys,
0 AS is_delete;

INSERT INTO xinglian.sy_bank
SELECT
0 AS id,
'张家口银行' AS from_bank,
'张家口银行股份有限公司' AS `to_bank`,
'jz' AS sys,
0 AS is_delete;

INSERT INTO xinglian.sy_bank
SELECT
0 AS id,
'四川天府银行' AS from_bank,
'四川天府银行股份有限公司' AS `to_bank`,
'jz' AS sys,
0 AS is_delete;









