# DataPivot 数据库工具

## 📋 概述

本工具为 DataPivot 项目提供数据库开发规范和自动化结构生成功能。

## 🚀 快速开始

### 1. 生成数据库结构

```bash
python generate_db_schema.py
```

### 2. 初始化数据库

```bash
# 创建数据库
mysql -uroot -p -e "CREATE DATABASE datapivot CHARACTER SET utf8mb4;"

# 导入结构
mysql -uroot -p datapivot < sql/schema/database_schema.sql
```

### 3. 查看文档

```bash
# 查看数据库结构文档
cat docs/DATABASE_SCHEMA.md

# 查看开发规范
cat docs/DATABASE_DEVELOPMENT.md
```

## 📚 文档

- **[快速开始](docs/DATABASE_QUICKSTART.md)** - 一分钟上手指南 ⭐
- **[开发规范](docs/DATABASE_DEVELOPMENT.md)** - 数据库连接和开发规范
- **[工具指南](docs/DATABASE_SCHEMA_GENERATOR.md)** - 结构生成工具详细说明
- **[数据库结构](docs/DATABASE_SCHEMA.md)** - 自动生成的结构文档

## 🛠️ 核心功能

### 数据库连接管理
- 基于 SQLAlchemy ORM
- 连接池自动管理
- 支持密码特殊字符
- UTF-8MB4 字符集

### 结构自动生成
- 导出所有表结构
- 导出所有视图结构
- 生成 Markdown 文档
- 支持分别导出

### 开发规范
- 模型定义规范
- 会话使用规范
- 事务处理规范
- 查询优化建议

## 📁 文件结构

```
DataPivot/
├── generate_db_schema.py          # 结构生成脚本
├── database.py                     # 数据库连接配置
├── config.py                       # 配置管理
├── docs/
│   ├── DATABASE_QUICKSTART.md      # 快速开始
│   ├── DATABASE_DEVELOPMENT.md     # 开发规范
│   ├── DATABASE_SCHEMA_GENERATOR.md # 工具指南
│   └── DATABASE_SCHEMA.md          # 结构文档（自动生成）
└── sql/
    └── schema/
        ├── database_schema.sql     # 完整结构（自动生成）
        ├── tables.sql              # 表结构（自动生成）
        └── views.sql               # 视图结构（自动生成）
```

## 💡 使用场景

### 新成员入职
```bash
# 1. 克隆项目
git clone <repository>

# 2. 初始化数据库
mysql -uroot -p datapivot < sql/schema/database_schema.sql

# 3. 配置环境
cp .env.example .env
```

### 数据库变更
```bash
# 1. 修改数据库结构
# ...

# 2. 重新生成文档
python generate_db_schema.py

# 3. 提交变更
git add sql/schema/ docs/DATABASE_SCHEMA.md
git commit -m "更新数据库结构"
```

### 环境同步
```bash
# 开发 -> 测试
python generate_db_schema.py
scp sql/schema/database_schema.sql user@test:/tmp/
ssh user@test "mysql -uroot -p test_db < /tmp/database_schema.sql"
```

## 🔧 配置

在 `.env` 文件中配置数据库连接：

```bash
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DB=datapivot
```

## 📖 开发规范示例

### FastAPI 路由中使用

```python
from fastapi import Depends
from sqlalchemy.orm import Session
from database import get_db

@app.get("/data")
def get_data(db: Session = Depends(get_db)):
    return db.query(Model).all()
```

### 独立脚本中使用

```python
from database import SessionLocal

db = SessionLocal()
try:
    result = db.query(Model).all()
    db.commit()
except Exception as e:
    db.rollback()
    raise e
finally:
    db.close()
```

## ⚠️ 注意事项

1. **权限要求**: 需要数据库 SELECT 和 SHOW VIEW 权限
2. **字符编码**: 使用 UTF-8MB4 字符集
3. **定期更新**: 数据库结构变更后及时运行生成脚本
4. **版本控制**: 将生成的文件提交到 Git

## 🐛 故障排除

### 连接失败
```bash
# 检查配置
cat .env | grep MYSQL

# 测试连接
mysql -h$MYSQL_HOST -u$MYSQL_USER -p$MYSQL_PASSWORD
```

### 权限不足
```sql
GRANT SELECT, SHOW VIEW ON datapivot.* TO 'user'@'localhost';
FLUSH PRIVILEGES;
```

### 模块未安装
```bash
pip install -r requirements.txt
```

## 📊 生成的文件

运行 `generate_db_schema.py` 后会生成：

1. **sql/schema/database_schema.sql** - 完整数据库结构（表+视图）
2. **sql/schema/tables.sql** - 仅表结构
3. **sql/schema/views.sql** - 仅视图结构
4. **docs/DATABASE_SCHEMA.md** - Markdown 格式文档

## 🎯 最佳实践

1. ✅ 每次数据库结构变更后运行生成脚本
2. ✅ 将生成的文件提交到版本控制
3. ✅ 使用参数化查询防止 SQL 注入
4. ✅ 合理使用索引提升性能
5. ✅ 正确处理事务确保数据一致性
6. ✅ 不在代码中硬编码密码

## 📞 获取帮助

- 查看 [快速开始文档](docs/DATABASE_QUICKSTART.md)
- 查看 [详细指南](docs/DATABASE_SCHEMA_GENERATOR.md)
- 查看 [开发规范](docs/DATABASE_DEVELOPMENT.md)

## 📝 更新日志

### 2026-03-04
- ✅ 创建数据库开发规范文档
- ✅ 实现数据库结构生成脚本
- ✅ 编写完整使用文档
- ✅ 更新项目文档索引

---

**DataPivot** - 数据情报分析系统
