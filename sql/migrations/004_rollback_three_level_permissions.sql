-- 回滚脚本：将三级权限改回两级
-- 执行日期：2026-03-04
-- 说明：如果迁移后发现问题，使用此脚本回滚

USE datapivot;

-- 将 write 和 read 都改回 user
UPDATE user_case_permissions
SET permission_level = 'user'
WHERE permission_level IN ('write', 'read');

-- 验证回滚结果
SELECT
    '回滚完成，当前权限分布：' AS message;

SELECT
    permission_level,
    COUNT(*) as count
FROM user_case_permissions
GROUP BY permission_level;

-- 可选：如果需要将字段名改回 role，取消下面的注释
-- ALTER TABLE user_case_permissions
-- CHANGE COLUMN permission_level role VARCHAR(20) DEFAULT 'user' COMMENT '案件内角色: admin/user';
