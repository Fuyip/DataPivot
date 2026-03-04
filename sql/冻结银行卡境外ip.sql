SELECT
*
FROM
freeze_card fc
INNER JOIN(
SELECT
*
FROM
bank_card_loc_info
)t1 ON t1.card_no=fc.card_no
INNER JOIN(
SELECT
*
FROM
ali_ip_loc
)t2 ON t2.ip=t1.ip_loc
WHERE
t2.isp<>'Cloudflare, Inc.'
AND t2.country<>''
AND
(
t2.country<>'中国'
OR
(t2.country='中国' AND city IN ('台湾','香港')))