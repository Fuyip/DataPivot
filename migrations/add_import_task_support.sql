-- 迁移脚本：添加导入任务支持
-- 执行时间：2026-03-09

-- 1. 在系统数据库(datapivot)创建导入任务表
USE datapivot;

CREATE TABLE IF NOT EXISTS `import_task` (
  `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '任务ID',
  `case_id` INT NOT NULL COMMENT '案件ID',
  `task_type` VARCHAR(50) NOT NULL COMMENT '任务类型：case_card/bank_statement',
  `file_name` VARCHAR(255) COMMENT '导入文件名',
  `total_count` INT DEFAULT 0 COMMENT '总记录数',
  `success_count` INT DEFAULT 0 COMMENT '成功数',
  `error_count` INT DEFAULT 0 COMMENT '失败数',
  `error_details` TEXT COMMENT '错误详情JSON',
  `created_by` INT NOT NULL COMMENT '创建人ID',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  INDEX idx_case_id (case_id),
  INDEX idx_task_type (task_type),
  INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='导入任务记录表';

-- 2. 为所有案件数据库的 case_card 表添加 import_task_id 字段
-- 注意：这个需要针对每个案件数据库执行
-- ALTER TABLE case_card ADD COLUMN `import_task_id` INT DEFAULT NULL COMMENT '导入任务ID' AFTER `is_main`;
-- ALTER TABLE case_card ADD INDEX idx_import_task_id (import_task_id);

-- 示例：为特定案件数据库添加字段（需要根据实际情况修改数据库名）
-- USE case_69OWB;
-- ALTER TABLE case_card ADD COLUMN `import_task_id` INT DEFAULT NULL COMMENT '导入任务ID' AFTER `is_main`;
-- ALTER TABLE case_card ADD INDEX idx_import_task_id (import_task_id);
