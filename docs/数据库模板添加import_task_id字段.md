# 数据库模板添加 import_task_id 字段

## 修改日期
2026-03-09

## 修改目的

确保新创建的案件数据库自动包含 `import_task_id` 字段，避免后续需要手动迁移。

---

## 修改的文件

### 1. case_template.sql

**文件路径**：`sql/schema/case_template.sql`

**修改位置**：第 720-736 行

**修改内容**：

在 `case_card` 表定义中添加：
- 字段：`import_task_id` int DEFAULT NULL COMMENT '导入任务ID'
- 索引：`KEY IDX_case_card_import_task_id (import_task_id)`

**修改后的表结构**：

```sql
CREATE TABLE `case_card` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键，自增',
  `case_no` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT '{{CASE_CODE}}' COMMENT '案件编号',
  `source` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '来源信息',
  `user_id` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '来源信息',
  `card_no` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '卡号',
  `bank_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '银行名称',
  `card_type` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '卡类型',
  `add_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '添加日期',
  `batch` int DEFAULT NULL COMMENT '第几批次',
  `is_in_bg` int DEFAULT NULL COMMENT '是否在后台',
  `is_main` int DEFAULT NULL COMMENT '是否为主卡',
  `import_task_id` int DEFAULT NULL COMMENT '导入任务ID',  -- ✅ 新增
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `UQE_case_card_card_no` (`card_no`) USING BTREE,
  KEY `IDX_case_card_bank_name` (`bank_name`) USING BTREE,
  KEY `IDX_case_card_card_type` (`card_type`) USING BTREE,
  KEY `IDX_case_card_case_no` (`case_no`) USING BTREE,
  KEY `IDX_case_card_import_task_id` (`import_task_id`) USING BTREE  -- ✅ 新增
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;
```

---

### 2. fx_test_schema.sql

**文件路径**：`sql/schema/fx_test_schema.sql`

**修改位置**：第 820-837 行

**修改内容**：

同样在 `case_card` 表定义中添加 `import_task_id` 字段和索引。

---

## 影响范围

### 新创建的案件

✅ 从现在开始，所有新创建的案件数据库都会自动包含 `import_task_id` 字段
✅ 导入功能可以正常记录导入任务 ID
✅ 删除导入任务功能可以正常工作

### 已存在的案件

⚠️ 已存在的案件数据库不会自动更新
⚠️ 需要手动执行迁移脚本为旧案件添加字段

---

## 旧案件数据库迁移

### 方法1：单个案件迁移

```sql
-- 1. 查询案件数据库名称
SELECT id, case_code, database_name
FROM datapivot.cases
WHERE id = {case_id};

-- 2. 为该数据库添加字段
USE {database_name};

ALTER TABLE case_card
ADD COLUMN import_task_id INT DEFAULT NULL COMMENT '导入任务ID'
AFTER is_main;

ALTER TABLE case_card
ADD INDEX idx_import_task_id (import_task_id);
```

### 方法2：批量迁移所有案件

使用迁移脚本：`migrations/add_import_task_support.sql`

或使用批量脚本（参考 `docs/导入任务删除功能修复说明.md` 中的批量迁移脚本）

---

## 验证方法

### 验证新创建的案件

1. 创建一个新案件
2. 查看案件数据库的 `case_card` 表结构
3. 确认 `import_task_id` 字段存在

```sql
USE {new_case_database};
SHOW COLUMNS FROM case_card LIKE 'import_task_id';
```

预期结果：
```
Field          Type    Null    Key     Default    Extra
import_task_id int     YES     MUL     NULL
```

### 验证导入功能

1. 在新案件中导入银行卡数据
2. 查询 `case_card` 表
3. 确认 `import_task_id` 字段有值

```sql
SELECT id, card_no, import_task_id
FROM case_card
WHERE import_task_id IS NOT NULL
LIMIT 5;
```

---

## 相关文档

- `migrations/add_import_task_support.sql` - 导入任务支持迁移脚本
- `docs/导入任务删除功能修复说明.md` - 删除功能修复和批量迁移说明
- `docs/导入任务查询NaN序列化修复说明.md` - 查询功能修复说明

---

## 总结

✅ 数据库模板已更新，包含 `import_task_id` 字段
✅ 新创建的案件将自动支持导入任务功能
✅ 旧案件需要手动迁移
✅ 代码已支持字段不存在的情况（向后兼容）

**修改完成日期**: 2026-03-09
**修改文件数量**: 2个 SQL 模板文件
**影响范围**: 所有新创建的案件数据库

---

**🎯 数据库模板已更新，新案件将自动支持导入任务功能！**
