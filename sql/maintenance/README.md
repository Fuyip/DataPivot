# 数据库维护脚本

## truncate_cases_tables.sql

### 功能
清空案件相关的两个表：
- `user_case_permissions` - 用户案件权限
- `cases` - 案件信息

### 使用方法

#### 方法 1: 使用 MySQL 命令行
```bash
mysql -u root -p < sql/maintenance/truncate_cases_tables.sql
```

#### 方法 2: 使用 MySQL 客户端
```bash
mysql -u root -p
source /path/to/DataPivot/sql/maintenance/truncate_cases_tables.sql;
```

#### 方法 3: 在 MySQL Workbench 中执行
1. 打开 MySQL Workbench
2. 连接到数据库
3. 打开 `truncate_cases_tables.sql` 文件
4. 点击执行按钮

### 注意事项

⚠️ **重要警告**:
- 此操作将永久删除所有案件和权限数据
- 执行前请务必备份数据库
- 案件对应的独立数据库不会被删除（可能产生孤立数据库）
- 用户账户信息不受影响

### 影响范围
- ✓ 清空所有案件记录
- ✓ 清空所有用户案件权限
- ✓ 重置表的自增 ID
- ✗ 不影响用户账户（users 表）
- ✗ 不删除案件数据库（需手动清理）

### 数据恢复
TRUNCATE 操作无法回滚，如需恢复数据，只能从备份中恢复。
