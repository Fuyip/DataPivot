# DataPivot 数据库表结构文档

## 数据库信息

- **数据库名称**: `datapivot`
- **字符集**: `utf8mb4`
- **排序规则**: `utf8mb4_unicode_ci`
- **用途**: 存储系统配置和用户管理相关数据

## 表结构

### 1. users - 用户表

**用途**: 存储系统用户账户信息和认证数据

**表结构**:
```sql
CREATE TABLE `users` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '用户ID',
  `username` VARCHAR(50) NOT NULL COMMENT '用户名',
  `hashed_password` VARCHAR(255) NOT NULL COMMENT '加密密码(bcrypt)',
  `full_name` VARCHAR(100) DEFAULT NULL COMMENT '真实姓名',
  `email` VARCHAR(100) DEFAULT NULL COMMENT '邮箱',
  `role` VARCHAR(20) NOT NULL DEFAULT 'user' COMMENT '角色: admin/user',
  `is_active` TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否激活: 1-激活, 0-禁用',
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_username` (`username`),
  UNIQUE KEY `uk_email` (`email`),
  KEY `idx_username` (`username`),
  KEY `idx_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';
```

**字段说明**:

| 字段名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| id | INT | 是 | AUTO_INCREMENT | 用户唯一标识 |
| username | VARCHAR(50) | 是 | - | 用户名，唯一，用于登录 |
| hashed_password | VARCHAR(255) | 是 | - | bcrypt 加密的密码哈希值 |
| full_name | VARCHAR(100) | 否 | NULL | 用户真实姓名 |
| email | VARCHAR(100) | 否 | NULL | 邮箱地址，唯一 |
| role | VARCHAR(20) | 是 | 'user' | 用户角色：admin(管理员)/user(普通用户) |
| is_active | TINYINT(1) | 是 | 1 | 账户状态：1-激活，0-禁用 |
| created_at | TIMESTAMP | 是 | CURRENT_TIMESTAMP | 账户创建时间 |
| updated_at | TIMESTAMP | 否 | NULL | 最后更新时间，自动更新 |

**索引说明**:
- `PRIMARY KEY (id)`: 主键索引
- `UNIQUE KEY uk_username (username)`: 用户名唯一索引
- `UNIQUE KEY uk_email (email)`: 邮箱唯一索引
- `KEY idx_username (username)`: 用户名查询索引
- `KEY idx_email (email)`: 邮箱查询索引

**约束说明**:
- 用户名必须唯一，长度 3-50 字符
- 邮箱必须唯一（如果提供）
- 密码使用 bcrypt 加密，最少 6 位明文
- 角色只能是 'admin' 或 'user'

**默认数据**:
```sql
-- 默认管理员账户
INSERT INTO `users` (`username`, `hashed_password`, `full_name`, `role`, `is_active`)
VALUES (
  'admin',
  '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqVqN5Uj8S',
  '系统管理员',
  'admin',
  1
);
-- 默认密码: admin123
```

## 数据库连接配置

**配置文件**: `.env`

```env
MYSQL_HOST=10.8.0.5
MYSQL_PORT=3306
MYSQL_USER=fuyip_net_gk
MYSQL_PASSWORD=Fuyip@235813
MYSQL_DB=datapivot
```

**连接方式**:
- 使用 `database.py` 中的 SQLAlchemy 连接
- 连接字符串: `mysql+pymysql://user:password@host:port/datapivot?charset=utf8mb4`
- 连接池配置: `pool_pre_ping=True`

## ORM 模型

**文件位置**: `backend/models/user.py`

```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    email = Column(String(100), unique=True, index=True)
    role = Column(String(20), default="user")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

## 数据库初始化

### 方法 1: 使用 Python 脚本（推荐）

```bash
# 激活虚拟环境
source venv/bin/activate

# 运行初始化脚本
python backend/utils/init_db.py
```

### 方法 2: 使用 SQL 脚本

```bash
# 执行 SQL 初始化脚本
mysql -h 10.8.0.5 -u fuyip_net_gk -p datapivot < sql/init/001_create_users_table.sql
```

## 数据备份

### 备份 users 表

```bash
# 备份表结构和数据
mysqldump -h 10.8.0.5 -u fuyip_net_gk -p datapivot users > backup/users_$(date +%Y%m%d).sql

# 仅备份表结构
mysqldump -h 10.8.0.5 -u fuyip_net_gk -p --no-data datapivot users > backup/users_schema.sql

# 仅备份数据
mysqldump -h 10.8.0.5 -u fuyip_net_gk -p --no-create-info datapivot users > backup/users_data.sql
```

### 恢复数据

```bash
# 恢复备份
mysql -h 10.8.0.5 -u fuyip_net_gk -p datapivot < backup/users_20260304.sql
```

## 数据查询示例

### 查看所有用户

```sql
SELECT id, username, full_name, email, role, is_active, created_at
FROM users
ORDER BY created_at DESC;
```

### 查看管理员用户

```sql
SELECT id, username, full_name, role
FROM users
WHERE role = 'admin' AND is_active = 1;
```

### 查看最近创建的用户

```sql
SELECT id, username, full_name, created_at
FROM users
ORDER BY created_at DESC
LIMIT 10;
```

### 统计用户数量

```sql
SELECT
  role,
  COUNT(*) as count,
  SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) as active_count
FROM users
GROUP BY role;
```

## 安全注意事项

1. **密码安全**
   - 密码使用 bcrypt 算法加密
   - 存储的是哈希值，不可逆
   - 默认密码仅用于开发测试

2. **数据库访问**
   - 生产环境使用独立的数据库用户
   - 限制数据库用户权限
   - 启用 SSL 连接

3. **备份策略**
   - 每日自动备份
   - 保留最近 30 天的备份
   - 定期测试恢复流程

4. **审计日志**
   - 记录所有用户管理操作
   - 记录登录失败尝试
   - 定期审查异常访问

## 相关文档

- [数据库开发规范](DATABASE_DEVELOPMENT.md)
- [用户管理指南](../USER_MANAGEMENT_GUIDE.md)
- [登录认证快速开始](../QUICKSTART_AUTH.md)

---

**更新日期**: 2026-03-04
**数据库版本**: 1.0
**维护人员**: 系统管理员
