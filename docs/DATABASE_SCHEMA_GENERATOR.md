# 数据库结构生成工具使用指南

## 快速开始

### 1. 确保环境配置正确

确保 `.env` 文件中的数据库配置正确：

```bash
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DB=datapivot
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 运行生成脚本

```bash
python generate_db_schema.py
```

## 生成的文件

脚本会自动生成以下文件：

### SQL 结构文件

1. **sql/schema/database_schema.sql**
   - 完整的数据库结构（包含所有表和视图）
   - 可直接用于初始化新数据库

2. **sql/schema/tables.sql**
   - 仅包含表结构
   - 用于快速创建数据表

3. **sql/schema/views.sql**
   - 仅包含视图结构
   - 用于在已有表的基础上创建视图

### 文档文件

4. **docs/DATABASE_SCHEMA.md**
   - Markdown 格式的数据库结构文档
   - 包含所有表的字段说明、索引信息
   - 便于团队查阅和维护

## 使用场景

### 场景 1: 初始化新数据库

```bash
# 创建数据库
mysql -uroot -p -e "CREATE DATABASE datapivot CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 导入完整结构
mysql -uroot -p datapivot < sql/schema/database_schema.sql
```

### 场景 2: 仅创建表结构

```bash
mysql -uroot -p datapivot < sql/schema/tables.sql
```

### 场景 3: 仅创建视图

```bash
mysql -uroot -p datapivot < sql/schema/views.sql
```

### 场景 4: 备份数据库结构

定期运行脚本，将生成的 SQL 文件提交到版本控制系统：

```bash
python generate_db_schema.py
git add sql/schema/
git commit -m "更新数据库结构"
```

## 脚本功能说明

### 核心功能

1. **自动连接数据库**
   - 从 `config.py` 读取配置
   - 支持密码特殊字符处理

2. **导出表结构**
   - 获取所有表的 CREATE TABLE 语句
   - 包含字段定义、索引、约束等完整信息

3. **导出视图结构**
   - 获取所有视图的 CREATE VIEW 语句
   - 自动清理 DEFINER 信息，便于跨环境使用

4. **生成文档**
   - 自动生成 Markdown 格式文档
   - 包含表结构、字段说明、索引信息

### 输出格式

生成的 SQL 文件包含：

```sql
-- 文件头信息
-- 数据库名称、生成时间、使用说明

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- 表结构
DROP TABLE IF EXISTS `table_name`;
CREATE TABLE `table_name` (...);

-- 视图结构
DROP VIEW IF EXISTS `view_name`;
CREATE VIEW `view_name` AS ...;

SET FOREIGN_KEY_CHECKS = 1;
```

## 注意事项

1. **权限要求**
   - 需要数据库用户具有 SELECT 权限
   - 需要能够执行 SHOW CREATE TABLE/VIEW

2. **字符编码**
   - 所有文件使用 UTF-8 编码
   - 数据库连接使用 utf8mb4 字符集

3. **视图依赖**
   - 视图可能依赖其他表或视图
   - 导入时注意依赖顺序

4. **大型数据库**
   - 对于表数量较多的数据库，生成过程可能需要一些时间
   - 脚本会显示进度信息

## 自定义配置

如需修改输出路径或格式，可编辑 `generate_db_schema.py`：

```python
# 修改输出路径
generator.generate_schema_file(
    'custom/path/schema.sql',  # 自定义路径
    include_tables=True,
    include_views=True
)

# 修改文档路径
generator.generate_markdown_documentation(
    'custom/path/schema.md'
)
```

## 故障排除

### 问题 1: 连接数据库失败

**错误信息**: `✗ 数据库连接失败: ...`

**解决方法**:
- 检查 `.env` 文件配置是否正确
- 确认数据库服务是否运行
- 验证用户名和密码是否正确

### 问题 2: 权限不足

**错误信息**: `✗ 获取表 xxx 结构失败: ...`

**解决方法**:
```sql
-- 授予必要权限
GRANT SELECT, SHOW VIEW ON datapivot.* TO 'username'@'localhost';
FLUSH PRIVILEGES;
```

### 问题 3: 模块未找到

**错误信息**: `ModuleNotFoundError: No module named 'pymysql'`

**解决方法**:
```bash
pip install pymysql
# 或安装所有依赖
pip install -r requirements.txt
```

## 相关文档

- [数据库开发规范](DATABASE_DEVELOPMENT.md) - 数据库连接和开发规范
- [数据库结构文档](DATABASE_SCHEMA.md) - 自动生成的数据库结构文档

## 维护建议

1. **定期更新**
   - 每次修改数据库结构后运行脚本
   - 将生成的文件提交到版本控制

2. **版本管理**
   - 使用 Git 跟踪结构变化
   - 便于回溯历史版本

3. **团队协作**
   - 共享生成的文档文件
   - 保持团队对数据库结构的一致理解

4. **环境同步**
   - 使用生成的 SQL 文件同步开发、测试、生产环境
   - 确保各环境结构一致
