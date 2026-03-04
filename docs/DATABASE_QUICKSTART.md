# 数据库结构生成工具 - 快速开始

## 一分钟快速使用

### 1. 运行生成脚本

```bash
python generate_db_schema.py
```

### 2. 查看生成的文件

```bash
# 查看生成的 SQL 文件
ls -lh sql/schema/

# 查看生成的文档
cat docs/DATABASE_SCHEMA.md
```

### 3. 使用生成的结构文件

```bash
# 初始化新数据库
mysql -uroot -p datapivot < sql/schema/database_schema.sql
```

## 输出示例

运行脚本后，你会看到类似以下的输出：

```
============================================================
DataPivot 数据库结构生成工具
============================================================

✓ 成功连接到数据库: datapivot
✓ 找到 25 个表
✓ 找到 3 个视图

[1/4] 生成完整数据库结构...
  [1/25] 导出表: bank_statements
  [2/25] 导出表: bank_all_statements
  [3/25] 导出表: case_card
  ...
  [1/3] 导出视图: 银行卡涉案情况
  [2/3] 导出视图: 3003xpj银行卡整体情况
  ...
✓ 数据库结构已导出到: sql/schema/database_schema.sql

[2/4] 生成表结构文件...
✓ 数据库结构已导出到: sql/schema/tables.sql

[3/4] 生成视图结构文件...
✓ 数据库结构已导出到: sql/schema/views.sql

[4/4] 生成数据库文档...
✓ 数据库文档已生成: docs/DATABASE_SCHEMA.md

============================================================
✓ 所有文件生成完成！
============================================================

生成的文件:
  - sql/schema/database_schema.sql  (完整数据库结构)
  - sql/schema/tables.sql           (仅表结构)
  - sql/schema/views.sql            (仅视图结构)
  - docs/DATABASE_SCHEMA.md         (数据库文档)
```

## 常见使用场景

### 场景 1: 新成员加入团队

```bash
# 1. 克隆项目
git clone <repository>

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件

# 3. 创建数据库
mysql -uroot -p -e "CREATE DATABASE datapivot CHARACTER SET utf8mb4;"

# 4. 导入数据库结构
mysql -uroot -p datapivot < sql/schema/database_schema.sql

# 5. 安装依赖
pip install -r requirements.txt

# 6. 启动项目
python main.py
```

### 场景 2: 数据库结构变更

```bash
# 1. 修改数据库结构（通过 SQL 或 ORM）
# ...

# 2. 重新生成结构文件
python generate_db_schema.py

# 3. 提交到版本控制
git add sql/schema/ docs/DATABASE_SCHEMA.md
git commit -m "更新数据库结构：添加 xxx 表"
git push
```

### 场景 3: 环境同步

```bash
# 开发环境 -> 测试环境
# 1. 在开发环境生成结构
python generate_db_schema.py

# 2. 复制到测试服务器
scp sql/schema/database_schema.sql user@test-server:/tmp/

# 3. 在测试服务器导入
ssh user@test-server
mysql -uroot -p test_datapivot < /tmp/database_schema.sql
```

### 场景 4: 数据库备份与恢复

```bash
# 备份结构
python generate_db_schema.py
cp sql/schema/database_schema.sql backups/schema_$(date +%Y%m%d).sql

# 备份数据
mysqldump -uroot -p datapivot > backups/data_$(date +%Y%m%d).sql

# 恢复
mysql -uroot -p datapivot < backups/schema_20260304.sql
mysql -uroot -p datapivot < backups/data_20260304.sql
```

## 脚本参数说明

目前脚本不接受命令行参数，所有配置通过 `.env` 文件管理。

如需自定义，可以修改 `generate_db_schema.py` 中的路径：

```python
# 自定义输出路径
generator.generate_schema_file(
    'custom/path/schema.sql',
    include_tables=True,
    include_views=True
)
```

## 故障排除

### 问题：连接失败

```bash
# 检查数据库是否运行
mysql -uroot -p -e "SELECT 1"

# 检查配置
cat .env | grep MYSQL
```

### 问题：权限不足

```sql
-- 授予权限
GRANT SELECT, SHOW VIEW ON datapivot.* TO 'your_user'@'localhost';
FLUSH PRIVILEGES;
```

### 问题：模块未安装

```bash
# 安装依赖
pip install -r requirements.txt

# 或单独安装
pip install pymysql
```

## 下一步

- 阅读 [数据库开发规范](DATABASE_DEVELOPMENT.md)
- 查看 [完整使用指南](DATABASE_SCHEMA_GENERATOR.md)
- 浏览 [生成的数据库文档](DATABASE_SCHEMA.md)

## 技术支持

如遇到问题，请查看：
1. 项目文档目录
2. 错误日志输出
3. 数据库连接配置
