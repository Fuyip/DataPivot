# 数据库迁移说明

## 迁移目的

将权限系统从两级（admin/user）升级为三级（admin/write/read），实现真正的读写权限区分。

## 迁移前准备

### 1. 确保 MySQL 服务正在运行

请先启动 MySQL 服务，然后再执行迁移脚本。

### 2. 备份数据库（可选）

虽然这是测试环境，但建议备份：

```bash
mysqldump -u root -p datapivot > backup_$(date +%Y%m%d_%H%M%S).sql
```

## 执行迁移

### 方法1：使用 Python 脚本（推荐）

```bash
# 在项目根目录执行
backend/venv/bin/python sql/migrations/run_migration.py
```

### 方法2：使用 MySQL 命令行

```bash
mysql -u root -p < sql/migrations/004_migrate_to_three_level_permissions.sql
```

## 迁移内容

1. **字段重命名**：将 `user_case_permissions.role` 改为 `permission_level`
2. **数据更新**：将所有 `user` 值改为 `write`
3. **验证结果**：显示当前权限分布

## 预期结果

迁移成功后，权限值应该只有：
- `admin` - 管理员权限
- `write` - 读写权限
- `read` - 只读权限

不应该再有 `user` 值。

## 回滚方案

如果迁移后发现问题，可以执行回滚脚本：

```bash
backend/venv/bin/python sql/migrations/run_rollback.py
```

或使用 MySQL 命令行：

```bash
mysql -u root -p < sql/migrations/004_rollback_three_level_permissions.sql
```

## 迁移后步骤

1. 重启后端服务
2. 刷新前端页面
3. 测试权限功能：
   - 分配只读权限
   - 分配读写权限
   - 分配管理员权限
   - 验证权限显示正确
   - 验证权限控制生效

## 故障排查

### 问题1：MySQL 连接被拒绝

**错误信息**：`Connection refused`

**解决方案**：
- 检查 MySQL 服务是否运行
- 检查端口是否正确（默认 3306）
- 检查防火墙设置

### 问题2：字段已存在

**错误信息**：`Duplicate column name 'permission_level'`

**解决方案**：
- 迁移脚本会自动检测字段名
- 如果字段已经是 `permission_level`，会跳过重命名步骤

### 问题3：权限值未更新

**解决方案**：
- 检查 UPDATE 语句是否执行成功
- 手动执行：`UPDATE user_case_permissions SET permission_level = 'write' WHERE permission_level = 'user';`

## 联系支持

如有问题，请查看：
- [权限控制文档](../../docs/权限控制文档.md)
- [权限问题修复总结](../../docs/权限问题修复总结.md)
