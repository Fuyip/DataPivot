# 案件表结构优化说明

## 功能说明

创建新案件时，自动生成的表结构具有以下特性：

### ✅ ID从1开始
所有表的自增ID（AUTO_INCREMENT）从1开始，而不是从之前模板的大数字开始。

### ✅ 自动添加案件名称
所有76个表都包含 `case_name` 字段，默认值自动设置为案件名称。

## 快速使用

### 创建案件
```python
from backend.services.case_service import create_case_database

database_name = create_case_database(
    case_id=1,
    case_name="张三诈骗案",
    case_code="ABC123"
)
```

### 结果
- 数据库名：`张三诈骗案_ABC123`
- 所有表的 `case_name` 字段默认值：`张三诈骗案`
- 所有表的 `AUTO_INCREMENT` 起始值：`1`

## 表结构示例

```sql
CREATE TABLE `bank_account_info` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键，自增',
  `accountOpeningName` varchar(50) DEFAULT NULL COMMENT '账户开户名称',
  `idNum` varchar(50) DEFAULT NULL COMMENT '开户人证件号码',
  ...
  PRIMARY KEY (`id`) USING BTREE,
  KEY `IDX_bank_account_info_transactionCardNum` (`transactionCardNum`) USING BTREE,
  `case_name` varchar(255) DEFAULT '张三诈骗案' COMMENT '案件名称'
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;
```

## 测试验证

```bash
# 运行测试
python3 test_case_creation.py

# 测试会验证：
# - 数据库创建成功
# - 76个表全部创建
# - case_name字段存在且默认值正确
# - AUTO_INCREMENT从1开始
```

## 技术实现

1. **模板文件**：`sql/schema/case_template.sql`
   - 使用 `{{CASE_NAME}}` 作为占位符

2. **服务层**：`backend/services/case_service.py`
   - 创建数据库时替换占位符为实际案件名称

3. **修复脚本**：`scripts/fix_case_template.py`
   - 自动修复模板文件的AUTO_INCREMENT和case_name字段

## 相关文档

- [快速开始](QUICKSTART_案件创建.md)
- [完成总结](案件表结构优化完成.md)

---
更新时间：2026-03-05
