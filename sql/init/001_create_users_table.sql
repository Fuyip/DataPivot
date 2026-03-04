-- 创建用户表
-- 用于存储系统用户信息和认证数据

CREATE TABLE IF NOT EXISTS `users` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '用户ID',
  `username` VARCHAR(50) NOT NULL COMMENT '用户名',
  `hashed_password` VARCHAR(255) NOT NULL COMMENT '加密密码',
  `full_name` VARCHAR(100) DEFAULT NULL COMMENT '真实姓名',
  `email` VARCHAR(100) DEFAULT NULL COMMENT '邮箱',
  `role` VARCHAR(20) NOT NULL DEFAULT 'user' COMMENT '角色: admin/user',
  `is_active` TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否激活',
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_username` (`username`),
  UNIQUE KEY `uk_email` (`email`),
  KEY `idx_username` (`username`),
  KEY `idx_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- 插入默认管理员账户
-- 用户名: admin
-- 密码: admin123 (BCrypt加密后的哈希值)
INSERT INTO `users` (`username`, `hashed_password`, `full_name`, `role`, `is_active`)
VALUES (
  'admin',
  '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqVqN5Uj8S',
  '系统管理员',
  'admin',
  1
) ON DUPLICATE KEY UPDATE `username` = `username`;

-- 说明：
-- 1. 密码哈希值是使用 bcrypt 算法生成的 "admin123" 的哈希
-- 2. 生产环境部署后请立即修改默认密码
-- 3. 使用 ON DUPLICATE KEY UPDATE 避免重复插入
