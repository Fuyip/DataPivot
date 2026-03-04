TRUNCATE TABLE bank_card_loc_info;
INSERT IGNORE INTO bank_card_loc_info
SELECT
0 AS id,
card_no,
ip_loc,
mac_loc
FROM
bank_all_statements_with_info
WHERE
dict_trade_tag='out'