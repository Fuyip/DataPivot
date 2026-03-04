SET @card_no="6228482690852149612";#此处填入主体卡号
SELECT
bs.card_no AS `主体卡号`,
t_cc1.source AS `主体卡来源`,
t_cc1.d_label AS `主体卡类型`,
bs.dict_trade_tag AS `资金流向标识`,
bs.rival_card_no AS `对手卡号`,
bs.rival_card_name AS `对手卡名称`,
t_cc2.source AS `对手卡来源`,
t_cc2.d_label AS `对手卡类型`,
bs.trade_money AS `总金额`,
bs.trade_count AS `总笔数`,
bs.min_trade_date AS `最早交易时间`,
bs.max_trade_date AS `最晚交易时间`,
bs.`situation` AS `关联方向`
FROM
bank_statements_turn bs
LEFT JOIN
(
SELECT
card_no,
source,
card_type,
sd.d_label
FROM
case_card cc
LEFT JOIN xinglian.sys_dict sd ON sd.d_value=cc.card_type
)t_cc1 ON t_cc1.card_no=bs.card_no


LEFT JOIN
(
SELECT
card_no,
source,
card_type, 
sd.d_label
FROM
case_card cc
LEFT JOIN xinglian.sys_dict sd ON sd.d_value=cc.card_type
)t_cc2 ON t_cc2.card_no=bs.rival_card_no
WHERE
bs.card_no=@card_no

ORDER BY
t_cc2.d_label DESC


#LIMIT 100 #运行速度慢时启用这条
