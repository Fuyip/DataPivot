SELECT
cc.*,
CASE WHEN t1.card_no IS NULL THEN '未回' ELSE '已回' END AS `流水反馈状态`
FROM
case_card cc
LEFT JOIN(
SELECT
*
FROM
bank_all_statements_lastest
GROUP BY card_no
)t1 ON t1.card_no=cc.card_no