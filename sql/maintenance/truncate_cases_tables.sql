-- 清空案件相关表的脚本
-- 警告：此操作将删除所有案件和权限数据，且不可恢复！
-- 执行前请确保已备份重要数据

USE datapivot;

-- 1. 禁用外键检查（避免外键约束导致的删除失败）
SET FOREIGN_KEY_CHECKS = 0;

-- 2. 清空用户案件权限表
TRUNCATE TABLE user_case_permissions;

-- 3. 清空案件表
TRUNCATE TABLE cases;

-- 4. 重新启用外键检查
SET FOREIGN_KEY_CHECKS = 1;

-- 完成提示
SELECT '✓ 表清空完成' AS status;
SELECT
    '已清空 user_case_permissions 和 cases 表' AS message,
    '注意：案件对应的独立数据库未被删除' AS warning;
