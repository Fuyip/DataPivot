-- 创建案件表和用户案件权限表
-- 在 datapivot 数据库中执行

USE datapivot;

-- 创建案件表
CREATE TABLE IF NOT EXISTS `cases` (
    `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '案件ID',
    `case_name` VARCHAR(200) NOT NULL UNIQUE COMMENT '案件名称',
    `case_code` VARCHAR(100) NOT NULL UNIQUE COMMENT '案件编号',
    `database_name` VARCHAR(100) NOT NULL UNIQUE COMMENT '案件数据库名称',
    `description` TEXT COMMENT '案件描述',
    `status` VARCHAR(20) DEFAULT 'active' COMMENT '状态: active/archived/closed',
    `is_active` BOOLEAN DEFAULT TRUE COMMENT '是否激活',
    `created_by` INT COMMENT '创建人ID',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (`created_by`) REFERENCES `users`(`id`) ON DELETE SET NULL,
    INDEX `idx_case_name` (`case_name`),
    INDEX `idx_case_code` (`case_code`),
    INDEX `idx_status` (`status`),
    INDEX `idx_created_by` (`created_by`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='案件表';

-- 创建用户案件权限表
CREATE TABLE IF NOT EXISTS `user_case_permissions` (
    `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '权限ID',
    `user_id` INT NOT NULL COMMENT '用户ID',
    `case_id` INT NOT NULL COMMENT '案件ID',
    `permission_level` VARCHAR(20) DEFAULT 'read' COMMENT '权限级别: read/write/admin',
    `granted_by` INT COMMENT '授权人ID',
    `granted_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '授权时间',
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`case_id`) REFERENCES `cases`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`granted_by`) REFERENCES `users`(`id`) ON DELETE SET NULL,
    UNIQUE KEY `unique_user_case` (`user_id`, `case_id`),
    INDEX `idx_user_id` (`user_id`),
    INDEX `idx_case_id` (`case_id`),
    INDEX `idx_permission_level` (`permission_level`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户案件权限表';
