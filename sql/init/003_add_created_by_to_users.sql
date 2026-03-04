-- 为用户表添加 created_by 字段
-- 用于记录用户的创建者，实现管理员权限隔离

-- 添加 created_by 字段
ALTER TABLE `users`
ADD COLUMN `created_by` INT DEFAULT NULL COMMENT '创建人ID' AFTER `is_active`,
ADD CONSTRAINT `fk_users_created_by` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE SET NULL;

-- 说明：
-- 1. created_by 字段用于记录哪个用户创建了当前用户
-- 2. 管理员只能查看和管理自己创建的用户
-- 3. 超级管理员不受此限制
-- 4. 外键约束设置为 ON DELETE SET NULL，删除创建者时不影响被创建的用户
