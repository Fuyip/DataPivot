-- 导入规则管理系统数据库迁移脚本
-- 创建日期: 2026-03-05

-- 1. 规则模板表
CREATE TABLE IF NOT EXISTS `import_rule_templates` (
  `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
  `template_name` VARCHAR(200) NOT NULL UNIQUE COMMENT '模板名称',
  `description` TEXT COMMENT '模板描述',
  `is_default` BOOLEAN DEFAULT FALSE COMMENT '是否默认模板',
  `is_active` BOOLEAN DEFAULT TRUE COMMENT '是否启用',
  `created_by` INT NOT NULL COMMENT '创建人ID',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  INDEX `idx_template_name` (`template_name`),
  INDEX `idx_is_default` (`is_default`),
  INDEX `idx_is_active` (`is_active`),
  INDEX `idx_created_by` (`created_by`),
  FOREIGN KEY (`created_by`) REFERENCES `users`(`id`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='导入规则模板表';

-- 2. 字段映射规则表
CREATE TABLE IF NOT EXISTS `import_field_mappings` (
  `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
  `template_id` INT NOT NULL COMMENT '所属模板ID',
  `data_type` VARCHAR(50) NOT NULL COMMENT '数据类型（人员信息/账户信息/交易明细等）',
  `db_field_name` VARCHAR(100) NOT NULL COMMENT '数据库字段名',
  `csv_column_name` VARCHAR(200) NOT NULL COMMENT 'CSV列名',
  `field_type` VARCHAR(50) NOT NULL COMMENT '字段类型（str/float/datetime/card_no/tag/none）',
  `sort_order` INT DEFAULT 0 COMMENT '排序顺序',
  `is_required` BOOLEAN DEFAULT FALSE COMMENT '是否必填',
  `default_value` VARCHAR(200) COMMENT '默认值',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  INDEX `idx_template_id` (`template_id`),
  INDEX `idx_data_type` (`data_type`),
  INDEX `idx_sort_order` (`sort_order`),
  UNIQUE KEY `uk_template_datatype_field` (`template_id`, `data_type`, `db_field_name`),
  FOREIGN KEY (`template_id`) REFERENCES `import_rule_templates`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='字段映射规则表';

-- 3. 数据清洗规则表
CREATE TABLE IF NOT EXISTS `import_cleaning_rules` (
  `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
  `template_id` INT NOT NULL COMMENT '所属模板ID',
  `rule_name` VARCHAR(100) NOT NULL COMMENT '规则名称',
  `rule_type` VARCHAR(50) NOT NULL COMMENT '规则类型（general/datetime）',
  `regex_pattern` VARCHAR(500) NOT NULL COMMENT '正则表达式',
  `description` TEXT COMMENT '规则说明',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  INDEX `idx_template_id` (`template_id`),
  INDEX `idx_rule_type` (`rule_type`),
  FOREIGN KEY (`template_id`) REFERENCES `import_rule_templates`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='数据清洗规则表';

-- 4. 规则使用记录表
CREATE TABLE IF NOT EXISTS `import_rule_usage_logs` (
  `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
  `template_id` INT NOT NULL COMMENT '使用的模板ID',
  `case_id` INT NOT NULL COMMENT '案件ID',
  `task_id` VARCHAR(100) NOT NULL COMMENT '任务ID',
  `used_by` INT NOT NULL COMMENT '使用人ID',
  `used_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '使用时间',
  INDEX `idx_template_id` (`template_id`),
  INDEX `idx_case_id` (`case_id`),
  INDEX `idx_task_id` (`task_id`),
  INDEX `idx_used_by` (`used_by`),
  INDEX `idx_used_at` (`used_at`),
  FOREIGN KEY (`template_id`) REFERENCES `import_rule_templates`(`id`) ON DELETE RESTRICT,
  FOREIGN KEY (`case_id`) REFERENCES `cases`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`used_by`) REFERENCES `users`(`id`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='规则使用记录表';

-- 5. 修改银行流水任务表，添加template_id字段
ALTER TABLE `bank_statement_tasks`
ADD COLUMN `template_id` INT DEFAULT NULL COMMENT '使用的规则模板ID' AFTER `case_id`,
ADD INDEX `idx_template_id` (`template_id`);
