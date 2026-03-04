UPDATE
case_card cc INNER JOIN
(
SELECT
*
FROM
bank_card_exg
WHERE id IN(
SELECT
MAX(id)
FROM
bank_card_exg
GROUP BY
card_no
)
)bce
ON cc.card_no=bce.card_no
SET
cc.card_type=bce.to_type_tag
WHERE
date=20250312