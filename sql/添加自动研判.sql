INSERT ignore INTO xinglian.`auto_card_analysis`(card_no,card_type)
SELECT
card_no,
card_type
FROM
case_card
WHERE card_type IN('c02','c06');
INSERT INTO xinglian.card_belong_case(card_no,card_type,case_no)
SELECT
card_no,
card_type,
'hbjt' AS case_no
FROM
case_card
WHERE card_type IN('c02','c06')