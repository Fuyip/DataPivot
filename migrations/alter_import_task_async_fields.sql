-- 迁移脚本：为案件银行卡导入任务增加异步处理状态字段
-- 执行时间：2026-03-10

USE datapivot;

ALTER TABLE `import_task`
  ADD COLUMN IF NOT EXISTS `status` VARCHAR(20) DEFAULT 'pending' COMMENT '任务状态: pending/processing/completed/failed' AFTER `file_name`,
  ADD COLUMN IF NOT EXISTS `progress` FLOAT DEFAULT 0 COMMENT '任务进度 0-100' AFTER `status`,
  ADD COLUMN IF NOT EXISTS `current_step` VARCHAR(100) NULL COMMENT '当前步骤' AFTER `progress`,
  ADD COLUMN IF NOT EXISTS `error_message` TEXT NULL COMMENT '任务错误信息' AFTER `error_details`,
  ADD COLUMN IF NOT EXISTS `task_ref` VARCHAR(100) NULL COMMENT '异步任务引用ID' AFTER `error_message`,
  ADD COLUMN IF NOT EXISTS `storage_path` VARCHAR(500) NULL COMMENT '导入文件存储路径' AFTER `task_ref`,
  ADD COLUMN IF NOT EXISTS `started_at` DATETIME NULL COMMENT '开始处理时间' AFTER `created_at`,
  ADD COLUMN IF NOT EXISTS `completed_at` DATETIME NULL COMMENT '完成时间' AFTER `started_at`;

CREATE INDEX IF NOT EXISTS `idx_import_task_status` ON `import_task` (`status`);
