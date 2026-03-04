SET @card="6235182145201776555";
SELECT
DISTINCT
b_s.card_no AS `已申调主体卡`,

cc.source AS `主体卡来源`,
#(case WHEN cc.source IS NOT NULL THEN cc.source ELSE concat(t_bai.accountOpeningName,t_bai.idNum) END),
sd.d_label AS `主体卡类型`,
b_s.dict_trade_tag AS `资金流向`,
b_s.rival_card_no AS `对手卡号`,
tbt.source AS `对手卡来源`,
tbt.d_label AS `对手卡类型`,
b_s.rival_card_name AS `对手卡名称`,
b_s.trade_money AS `总金额`,
b_s.trade_count AS `总笔数`,
b_s.min_trade_date AS `最早交易时间`,
b_s.max_trade_date AS `最晚交易时间`
FROM
bank_statements_turn AS b_s
LEFT JOIN case_card cc ON cc.card_no=b_s.card_no
LEFT JOIN xinglian.sys_dict sd ON cc.card_type=sd.d_value
LEFT JOIN(
SELECT
#@card,
cc.source,
sd.d_label,
cc.card_no
FROM case_card cc
LEFT JOIN xinglian.sys_dict sd on cc.card_type=sd.d_value
) tbt
ON tbt.card_no=rival_card_no
WHERE
rival_card_no=@card
ORDER BY max_trade_date DESC