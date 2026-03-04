SELECT
cc.*,
CASE WHEN t1.id IS NULL THEN '未回' ELSE '已回' END AS `是否回单`
FROM
case_card cc
LEFT JOIN(
SELECT
*
FROM
bank_all_statements_lastest
GROUP BY card_no
)t1 ON t1.card_no=cc.card_no