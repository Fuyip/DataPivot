SELECT
t1.*
 FROM `freeze_card` fc
 INNER JOIN(
 SELECT
 *
 FROM
 `3003xpj银行卡整体情况_0403`
 )t1 ON fc.card_no=t1.`卡号`