SELECT
t1.ip,
t1.country,
t1.city,
COUNT(DISTINCT bcli.card_no)
FROM
bank_card_loc_info bcli

INNER JOIN(
SELECT
*
FROM
ali_ip_loc

)t1 ON t1.ip=bcli.ip_loc

INNER JOIN(
SELECT
DISTINCT
card_no
FROM
`预冻结卡境外ip`
)t2 ON t2.card_no=bcli.card_no

WHERE
bcli.ip_loc NOT IN('0.0.0.0','0.0.0.1')
GROUP BY t1.ip