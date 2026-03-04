DROP VIEW IF EXISTS `3003xpj银行卡整体情况`;
CREATE VIEW `3003xpj银行卡整体情况` AS
SELECT
cc.card_no AS `卡号`,
cc.bank_name AS `银行名称`,
sd1.d_label AS `涉案银行卡类型`,
CASE WHEN cc.is_in_bg=1 THEN '是' ELSE '否' END AS `是否从后台中直接得到`,
CASE WHEN cc.is_main=1 THEN '是' ELSE '否' END AS `是否为核心收款私账`,
t4.bank_name AS `申调银行`,
REPLACE(t1.source,'账户信息','') AS `实际开户行`,
cc.source AS `后台登记户名`,
cc.user_id AS `后台uid`,
t1.accountOpeningName AS `账户信息户名`,
t1.idNum AS `身份证号码`,
t13.idType AS `证照类型`,
t13.workPhone AS `工作电话`,
CASE WHEN t1.idNUM  IS NOT NULL THEN CASE WHEN (LEFT(RIGHT(t1.idNUM,2),1)+0)&1=1 THEN '男' ELSE '女' END ELSE '未知' END AS `性别`,
t1.accountBalance AS `账户信息余额`,
t2.trade_balance AS `真实余额`,

t5.`涉案金额` AS `涉案入金金额`,
t6.`in_flow` AS `总入金金额`,
t5.`涉案金额`/t6.`in_flow` AS `涉案入金百分比`,
CASE WHEN  t2.trade_balance <t5.`涉案金额` THEN  t2.trade_balance ELSE t5.`涉案金额` END AS `冻结金额`,
t5.`涉案笔数` AS `涉案入金笔数`,
t6.`sum_count` AS `交易总笔数`,
t6.`flow` AS `交易总流水`,

t16.cnt_id AS `近三个月交易次数`,
t16.sum_money AS `近三个月交易金额`,

t6.`merchant_percentage` AS `微信/支付宝交易占比`,
t2.trade_date AS `最后交易时间`,
t5.`最早涉案时间` AS `最早入金涉案时间`,
t5.`最晚涉案时间` AS `最晚入金涉案时间`,
t5.`与入款卡关联张数` AS `与入款卡入金关联张数`,
t5.`与出款卡关联张数` AS `与出款卡入金关联张数`,
t5.`与赌客卡关联张数` AS `与赌客卡入金关联张数`,
t5.`与金主卡关联张数` AS `与金主卡入金关联张数`,
t5.`与金主卡转出方关联张数` AS `与金主卡转出方入金关联张数`,
t52.`涉案金额`AS `涉案出金金额`,
t52.`涉案笔数` AS `涉案出金笔数`,
t52.`最早涉案时间` AS `最早出金涉案时间`,
t52.`最晚涉案时间` AS `最晚出金涉案时间`,
t52.`与入款卡关联张数` AS `与入款卡出金关联张数`,
t52.`与出款卡关联张数` AS `与出款卡出金关联张数`,
t52.`与赌客卡关联张数` AS `与赌客卡出金关联张数`,
t52.`与金主卡关联张数` AS `与金主卡出金关联张数`,
t52.`与金主卡转出方关联张数` AS `与金主卡转出方出金关联张数`,

t1.accountStatus AS `账户信息状态`,
t3.freezing_info AS `强制信息状态`,
CASE WHEN t1.idNum IS NOT NULL THEN '已反馈' ELSE '未反馈' END AS `账户信息申调状态`,
CASE WHEN t2.card_no IS NOT NULL THEN '已反馈' ELSE '未反馈' END AS `流水申调状态`,
t4.source AS `申调原因`,
t4.min_date AS `最早申调时间`,
t4.max_date AS `最晚申调时间`,
t8.freeze_batch AS `冻结批次`,
t15.bank_name AS `冻结银行名称`,
t15.result AS `冻结结果`,
t15.fail_reason AS `冻结失败原因`,
t15.apply_freeze_limit AS `申请冻结限额`,
t15.execute_frozen_amount AS `执行冻结金额`,
t15.prior_freezing_authority AS `先冻机关`,
t15.prior_frozen_amount AS `在先冻结金额`,
t15.balance AS `余额`,
t15.available_account_Balance AS `可用账户余额`,
t15.execution_start_time AS `开始冻结时间`,
t15.freeze_end_time AS `冻结到期时间`,
t14.phone AS `联系电话`,
t14.loc AS `联系地址`
FROM (
SELECT
*
FROM
case_card
WHERE card_type NOT IN ('c30')
) cc

LEFT JOIN xinglian.sys_dict sd1 ON sd1.d_value=cc.card_type

LEFT JOIN(
SELECT
accountBalance,
transactionCardNum,
tradingAccountNum,
source,
idNum,
accountOpeningName,
GROUP_CONCAT(DISTINCT accountStatus) AS accountStatus
FROM
bank_account_info
WHERE idNum IS NOT NULL
GROUP BY transactionCardNum
)t1 ON t1.transactionCardNum=cc.card_no

LEFT JOIN(
SELECT
card_no,
trade_date,
trade_balance
FROM
bank_all_statements_lastest
GROUP BY
card_no
)t2 ON t2.card_no=cc.card_no

LEFT JOIN(
SELECT
account,
GROUP_CONCAT(DISTINCT CONCAT('冻结类型:',CASE WHEN TypeOfFreezingAction IS NULL THEN '0' ELSE TypeOfFreezingAction END,'-冻结机关:',CASE WHEN freezeTheAuthorities IS NULL THEN '0' ELSE freezeTheAuthorities END,'-备注:',CASE WHEN remark IS NULL THEN '0' ELSE remark END,'-冻结时间:',CASE WHEN freezeStartDate IS NULL THEN 'unKown' ELSE freezeStartDate END,' TO ',CASE WHEN freezeDeadline IS NULL THEN 'unKown' ELSE freezeDeadline END)) AS `freezing_info`
FROM
bank_coercive_action_info
GROUP BY account
)t3 ON t3.account=t1.tradingAccountNum

LEFT JOIN(

SELECT
card_no,
bank_name,
GROUP_CONCAT(source) AS source,
MIN(apply_date) AS min_date,
MAX(apply_date) AS max_date
FROM
apply_card_inner
GROUP BY card_no
)t4 ON t4.card_no=cc.card_no

LEFT JOIN(
SELECT
*
FROM
`银行卡涉案情况`
WHERE `关联方向`='入金'
)t5 ON t5.`涉案银行卡`=cc.card_no

LEFT JOIN(
SELECT
*
FROM
`银行卡涉案情况`
WHERE `关联方向`='出金'
)t52 ON t52.`涉案银行卡`=cc.card_no

LEFT JOIN(
SELECT
card_no,
-- SUM(CASE WHEN LENGTH(rival_card_name)>3 THEN trade_count ELSE 0 END)/SUM(trade_count) AS `merchant_percentage`
SUM(CASE WHEN rival_card_name REGEXP '(支付宝)|(微信)|(财付通)|(合众易宝)|(微众银行)|(拼多多)|(天弘基金)' THEN trade_count ELSE 0 END)/SUM(trade_count) AS `merchant_percentage`,
SUM(CASE WHEN situation='正' THEN trade_count ELSE 0 END) AS `sum_count`,
SUM(trade_money) AS `flow`,
SUM(CASE WHEN dict_trade_tag='in' THEN trade_money ELSE 0 END) AS `in_flow`
FROM
bank_statements_turn
GROUP BY card_no
)t6 ON t6.card_no=cc.card_no

LEFT JOIN(
SELECT
card_no
FROM
bank_card_exg
GROUP BY card_no
)t7 ON t7.card_no=cc.card_no

LEFT JOIN(
SELECT
*
FROM
freeze_card
)t8 ON t8.card_no=cc.card_no

LEFT JOIN(
SELECT
*
FROM
bank_people_info
GROUP BY idNum
)t13 ON t13.idNum=t1.idNum

LEFT JOIN(
SELECT
*
FROM
gz_tz_info
GROUP BY card_no
)t14 ON t14.card_no=cc.card_no

LEFT JOIN(
SELECT
*
FROM
freeze_back
WHERE account<>'' OR card_no<>''
GROUP BY account,card_no
)t15 ON t15.account=cc.card_no OR cc.card_no=t15.card_no

LEFT JOIN(
SELECT
card_no,
COUNT(id) AS `cnt_id`,
SUM(trade_money) AS `sum_money`
FROM
bank_all_statements
WHERE
rival_card_no IS NOT NULL
AND
(
(
YEAR(trade_date)=2024
AND MONTH(trade_date) IN (12)
)OR(
YEAR(trade_date)=2025
AND MONTH(trade_date) IN (1,2,3)
)
)
GROUP BY card_no
)t16 ON t16.card_no=cc.card_no