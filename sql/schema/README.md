# 数据库结构文件目录

本目录存放自动生成的数据库结构文件。

## 文件说明

- **database_schema.sql** - 完整的数据库结构（表 + 视图）
- **tables.sql** - 仅包含表结构
- **views.sql** - 仅包含视图结构

## 生成方法

在项目根目录运行：

```bash
python generate_db_schema.py
```

## 使用方法

### 初始化新数据库

```bash
# 1. 创建数据库
mysql -uroot -p -e "CREATE DATABASE datapivot CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 2. 导入完整结构
mysql -uroot -p datapivot < database_schema.sql
```

### 仅导入表结构

```bash
mysql -uroot -p datapivot < tables.sql
```

### 仅导入视图结构

```bash
mysql -uroot -p datapivot < views.sql
```

## 注意事项

1. 这些文件由脚本自动生成，请勿手动编辑
2. 每次数据库结构变更后，应重新生成这些文件
3. 建议将生成的文件提交到版本控制系统
4. 导入前请确保数据库已创建且字符集为 utf8mb4

## 相关文档

- [数据库开发规范](../../docs/DATABASE_DEVELOPMENT.md)
- [数据库结构生成工具使用指南](../../docs/DATABASE_SCHEMA_GENERATOR.md)
