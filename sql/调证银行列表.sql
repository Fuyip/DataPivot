SELECT
bank_name,
count(id) AS `card_cnt`
FROM
case_card_dz
GROUP BY bank_name