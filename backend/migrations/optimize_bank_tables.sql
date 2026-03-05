-- 银行流水表优化迁移脚本
-- 用于优化现有案件数据库的银行流水表结构
-- 执行前请确保已备份数据库
--
-- 使用方法:
-- mysql -u用户名 -p 案件数据库名 < optimize_bank_tables.sql
--
-- 优化内容:
-- 1. 金额字段: FLOAT/DOUBLE → DECIMAL(15,2) (25处)
-- 2. VARCHAR字段长度优化 (23处)
--
-- 创建时间: 2026-03-05

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ============================================
-- 1. bank_account_info (账户信息表)
-- ============================================

ALTER TABLE `bank_account_info`
  MODIFY COLUMN `accountBalance` decimal(15,2) DEFAULT NULL COMMENT '账户余额',
  MODIFY COLUMN `availableBalance` decimal(15,2) DEFAULT NULL COMMENT '可用余额',
  MODIFY COLUMN `currency` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '币种',
  MODIFY COLUMN `accountOpeningOutlets` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '开户网点',
  MODIFY COLUMN `agentId` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '代理人ID';

-- ============================================
-- 2. bank_account_info_tmp (账户信息临时表)
-- ============================================

ALTER TABLE `bank_account_info_tmp`
  MODIFY COLUMN `accountBalance` decimal(15,2) DEFAULT NULL COMMENT '账户余额',
  MODIFY COLUMN `availableBalance` decimal(15,2) DEFAULT NULL COMMENT '可用余额',
  MODIFY COLUMN `currency` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '币种',
  MODIFY COLUMN `accountOpeningOutlets` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '开户网点',
  MODIFY COLUMN `agentId` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '代理人ID';

-- ============================================
-- 3. bank_account_info_lastest (最新账户信息表)
-- ============================================

ALTER TABLE `bank_account_info_lastest`
  MODIFY COLUMN `accountBalance` decimal(15,2) DEFAULT NULL COMMENT '账户余额',
  MODIFY COLUMN `availableBalance` decimal(15,2) DEFAULT NULL COMMENT '可用余额',
  MODIFY COLUMN `currency` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '币种',
  MODIFY COLUMN `accountOpeningOutlets` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '开户网点',
  MODIFY COLUMN `agentId` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '代理人ID';

-- ============================================
-- 4. bank_all_statements (交易明细表)
-- ============================================

ALTER TABLE `bank_all_statements`
  MODIFY COLUMN `trade_money` decimal(15,2) DEFAULT NULL COMMENT '交易金额',
  MODIFY COLUMN `trade_balance` decimal(15,2) DEFAULT NULL COMMENT '交易余额',
  MODIFY COLUMN `rival_trade_balance` decimal(15,2) DEFAULT NULL COMMENT '对手交易余额',
  MODIFY COLUMN `transaction_loc` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '交易发生地';

-- ============================================
-- 5. bank_all_statements_tmp (交易明细临时表)
-- ============================================

ALTER TABLE `bank_all_statements_tmp`
  MODIFY COLUMN `trade_money` decimal(15,2) DEFAULT NULL COMMENT '交易金额',
  MODIFY COLUMN `trade_balance` decimal(15,2) DEFAULT NULL COMMENT '交易余额',
  MODIFY COLUMN `rival_trade_balance` decimal(15,2) DEFAULT NULL COMMENT '对手交易余额',
  MODIFY COLUMN `transaction_loc` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '交易发���地';

-- ============================================
-- 6. bank_all_statements_lastest (最新交易明细表)
-- ============================================

ALTER TABLE `bank_all_statements_lastest`
  MODIFY COLUMN `trade_money` decimal(15,2) DEFAULT NULL COMMENT '交易金额',
  MODIFY COLUMN `trade_balance` decimal(15,2) DEFAULT NULL COMMENT '交易余额',
  MODIFY COLUMN `rival_trade_balance` decimal(15,2) DEFAULT NULL COMMENT '对手交易余额',
  MODIFY COLUMN `transaction_loc` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '交易发生地';

-- ============================================
-- 7. bank_all_statements_turn (交易明细转账表)
-- ============================================

ALTER TABLE `bank_all_statements_turn`
  MODIFY COLUMN `trade_money` decimal(15,2) DEFAULT NULL COMMENT '交易金额',
  MODIFY COLUMN `trade_balance` decimal(15,2) DEFAULT NULL COMMENT '交易余额',
  MODIFY COLUMN `rival_trade_balance` decimal(15,2) DEFAULT NULL COMMENT '对手交易余额',
  MODIFY COLUMN `transaction_loc` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '交易发生地';

-- ============================================
-- 8. bank_all_statements_with_info (交易明细关联信息表)
-- ============================================

ALTER TABLE `bank_all_statements_with_info`
  MODIFY COLUMN `trade_money` decimal(15,2) DEFAULT NULL COMMENT '交易金额',
  MODIFY COLUMN `trade_balance` decimal(15,2) DEFAULT NULL COMMENT '交易余额',
  MODIFY COLUMN `transaction_loc` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '交易发生地';

-- ============================================
-- 9. bank_people_info (人员信息表)
-- ============================================

ALTER TABLE `bank_people_info`
  MODIFY COLUMN `agentId` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '代理人证件号码';

-- ============================================
-- 10. bank_people_info_tmp (人员信息临时表)
-- ============================================

ALTER TABLE `bank_people_info_tmp`
  MODIFY COLUMN `agentId` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '代理人证件号码';

-- ============================================
-- 11. bank_sub_account_info (关联子账户信息表)
-- ============================================

ALTER TABLE `bank_sub_account_info`
  MODIFY COLUMN `balance` decimal(15,2) DEFAULT NULL COMMENT '余额',
  MODIFY COLUMN `availableBalance` decimal(15,2) DEFAULT NULL COMMENT '可用余额',
  MODIFY COLUMN `subAccountAccounts` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '子账户账号',
  MODIFY COLUMN `subAccountSerialNum` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '子账户序列号';

-- ============================================
-- 12. bank_sub_account_info_tmp (关联子账户信息临时表)
-- ============================================

ALTER TABLE `bank_sub_account_info_tmp`
  MODIFY COLUMN `balance` decimal(15,2) DEFAULT NULL COMMENT '余额',
  MODIFY COLUMN `availableBalance` decimal(15,2) DEFAULT NULL COMMENT '可用余额',
  MODIFY COLUMN `subAccountAccounts` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '子账户账号',
  MODIFY COLUMN `subAccountSerialNum` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '子账户序列号';

-- ============================================
-- 13. bank_coercive_action_info (强制措施信息表)
-- ============================================

ALTER TABLE `bank_coercive_action_info`
  MODIFY COLUMN `freezeAmount` decimal(15,2) DEFAULT NULL COMMENT '冻结金额';

-- ============================================
-- 14. bank_coercive_action_info_tmp (强制措施信息临时表)
-- ============================================

ALTER TABLE `bank_coercive_action_info_tmp`
  MODIFY COLUMN `freezeAmount` decimal(15,2) DEFAULT NULL COMMENT '冻结金额';

SET FOREIGN_KEY_CHECKS = 1;

-- 优化完成
-- 建议执行以下验证SQL:
-- SELECT MAX(LENGTH(currency)) as max_currency_len FROM bank_account_info;
-- SELECT MAX(LENGTH(transaction_loc)) as max_loc_len FROM bank_all_statements;
-- SELECT SUM(accountBalance) FROM bank_account_info;
-- SELECT SUM(trade_money) FROM bank_all_statements;
