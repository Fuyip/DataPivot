ALTER TABLE `bank_all_statements`
  MODIFY COLUMN `rival_card_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '对手户名';

ALTER TABLE `bank_all_statements_lastest`
  MODIFY COLUMN `rival_card_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '对方卡名';

ALTER TABLE `bank_all_statements_tmp`
  MODIFY COLUMN `rival_card_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '对手户名';

ALTER TABLE `bank_all_statements_turn`
  MODIFY COLUMN `rival_card_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '对方卡名';

ALTER TABLE `bank_all_statements_with_info`
  MODIFY COLUMN `rival_card_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '对手户名';

ALTER TABLE `bank_statements`
  MODIFY COLUMN `rival_card_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '对方卡名';

ALTER TABLE `bank_statements_turn`
  MODIFY COLUMN `rival_card_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '对方卡名';
