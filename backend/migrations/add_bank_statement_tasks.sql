-- 银行流水任务表迁移脚本
-- 在 datapivot 数据库中执行

USE datapivot;

CREATE TABLE IF NOT EXISTS `bank_statement_tasks` (
  `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '任务ID',
  `case_id` INT NOT NULL COMMENT '案件ID',
  `task_id` VARCHAR(100) NOT NULL UNIQUE COMMENT 'Celery任务ID',

  -- 任务信息
  `status` VARCHAR(20) DEFAULT 'pending' COMMENT '任务状态: pending/processing/completed/failed/cancelled',
  `task_type` VARCHAR(20) DEFAULT 'upload' COMMENT '任务类型: upload/reprocess',

  -- 文件信息
  `file_count` INT DEFAULT 0 COMMENT '上传的文件数量',
  `file_names` JSON COMMENT '文件名列表',
  `file_size_total` FLOAT DEFAULT 0 COMMENT '总文件大小（MB）',

  -- 进度信息
  `progress` FLOAT DEFAULT 0 COMMENT '进度 0-100',
  `current_step` VARCHAR(100) COMMENT '当前步骤描述',
  `processed_files` INT DEFAULT 0 COMMENT '已处理文件数',

  -- 处理结果统计
  `total_records` INT DEFAULT 0 COMMENT '总记录数',
  `success_records` INT DEFAULT 0 COMMENT '成功记录数',
  `error_records` INT DEFAULT 0 COMMENT '错误记录数',
  `error_files` JSON COMMENT '错误文件列表',

  -- 详细统计（按数据类型）
  `statistics` JSON COMMENT '统计信息: {人员信息: 100, 账户信息: 200, ...}',

  -- 错误信息
  `error_message` TEXT COMMENT '错误详情',

  -- 时间戳
  `created_by` INT COMMENT '创建人ID',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `started_at` DATETIME COMMENT '开始处理时间',
  `completed_at` DATETIME COMMENT '完成时间',

  -- 文件路径（用于清理）
  `storage_path` VARCHAR(500) COMMENT '文件存储路径',

  -- 索引
  INDEX `idx_case_id` (`case_id`),
  INDEX `idx_task_id` (`task_id`),
  INDEX `idx_status` (`status`),
  INDEX `idx_created_at` (`created_at`),

  -- 外键
  FOREIGN KEY (`case_id`) REFERENCES `cases`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`created_by`) REFERENCES `users`(`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='银行流水处理任务表';
