-- 数据库迁移：统一使用 permission_level 字段，支持三级权限
-- 执行日期：2026-03-04
-- 说明：将 role 字段改为 permission_level，将 user 值改为 write

USE datapivot;

-- 步骤1：检查当前表结构，确定字段名
SET @column_exists = (
    SELECT COUNT(*)
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = 'datapivot'
    AND TABLE_NAME = 'user_case_permissions'
    AND COLUMN_NAME = 'role'
);

-- 步骤2：如果是 role 字段，重命名为 permission_level
SET @sql = IF(@column_exists > 0,
    'ALTER TABLE user_case_permissions CHANGE COLUMN role permission_level VARCHAR(20) DEFAULT ''read'' COMMENT ''权限级别: read/write/admin''',
    'SELECT ''Field already named permission_level'' AS message'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 步骤3：更新现有数据（将 user 映射为 write）
UPDATE user_case_permissions
SET permission_level = 'write'
WHERE permission_level = 'user';

-- 步骤4：验证迁移结果
SELECT
    '迁移完成，当前权限分布：' AS message;

SELECT
    permission_level,
    COUNT(*) as count
FROM user_case_permissions
GROUP BY permission_level;
