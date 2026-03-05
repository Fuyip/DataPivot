# 快速开始：创建案件

## 现在创建案件非常简单！

### 方式一：通过前端界面（推荐）

1. 登录系统
2. 进入"案件管理"
3. 点击"创建案件"
4. 填写信息并提交

**系统自动完成**：
- ✅ 创建案件数据库
- ✅ 初始化 76 个表
- ✅ 分配管理权限
- ✅ 所有表ID从1开始
- ✅ 所有表自动添加案件名称字段

### 方式二：通过 API

```bash
curl -X POST http://localhost:8000/api/v1/cases \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "case_name": "新案件",
    "case_code": "CASE001",
    "description": "案件描述"
  }'
```

## 就这么简单！

创建完成后，案件数据库已包含所有 76 个表，可以立即使用。

## 新功能特性

### 1. ID从1开始
所有表的自增ID（AUTO_INCREMENT）从1开始，确保数据整洁。

### 2. 自动添加案件名称
所有表都包含 `case_name` 字段，默认值为案件名称，方便数据追溯。

示例：
```sql
CREATE TABLE `bank_account_info` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  ...
  `case_name` varchar(255) DEFAULT '张三诈骗案' COMMENT '案件名称'
) ENGINE=InnoDB AUTO_INCREMENT=1;
```

## 表结构包括

- 银行流水相关表（16个）
- 人员档案表（15个）
- 设备分析表（8个）
- 社交通讯表（4个）
- 其他分析表（33个）

## 验证

```bash
# 查看创建的数据库
mysql -uroot -p -e "SHOW DATABASES LIKE '%案件名%';"

# 查看表结构
mysql -uroot -p 案件数据库名 -e "SHOW TABLES;"
```

## 更多信息

详细文档请查看：
- [案件数据库创建指南](docs/案件数据库创建指南.md)
- [案件数据库自动初始化功能-最终总结](案件数据库自动初始化功能-最终总结.md)
