SELECT
fc.card_no,
t1.ip_loc,
concat(t2.country,'-',t2.city)
FROM
freeze_card fc

INNER JOIN(
SELECT
*
FROM
bank_all_statements_with_info
WHERE
dict_trade_tag='out'
GROUP BY card_no,ip_loc
)t1 ON t1.card_no=fc.card_no

LEFT JOIN(
SELECT
*
FROM
ali_ip_loc
GROUP BY ip
)t2 ON t2.ip=t1.ip_loc
