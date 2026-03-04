UPDATE
case_card cc


LEFT JOIN(
SELECT
*
FROM
xinglian.bank_bin
)t1 ON t1.bin=LEFT(cc.card_no,t1.bin_len) AND t1.card_len=LENGTH(cc.card_no)

LEFT JOIN(
SELECT
*
FROM
xinglian.sy_bank
WHERE
sys='jz'
)t3 ON t3.from_bank=t1.bank_name
INNER JOIN(
SELECT
*
FROM
xinglian.sys_dict
WHERE
d_type='sys_name'
)t2 ON t2.d_value=t3.`sys`

SET
cc.bank_name=t3.to_bank