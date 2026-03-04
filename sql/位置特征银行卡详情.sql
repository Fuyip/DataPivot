SELECT
t1.ip_loc AS `IP地址`,
t1.mac_loc AS `MAC地址`,
tt.*

FROM
case_card cc
INNER JOIN(
SELECT
*
FROM
`3003xpj银行卡整体情况_0410`
)tt ON tt.`卡号`=cc.card_no
INNER JOIN(
SELECT
*
FROM
bank_card_loc_info
)t1 ON t1.card_no=cc.card_no

WHERE
cc.card_type='c02'