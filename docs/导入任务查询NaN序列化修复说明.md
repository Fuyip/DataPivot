# 导入任务查询 NaN 序列化修复说明

## 修复日期
2026-03-09

## 问题描述

用户反馈：**path.card_id: Input should be a valid integer, unable to parse string as an integer 获取导入任务失败。**

实际错误：访问 `/api/v1/cases/22/case-cards/import-tasks` 时返回 **500 Internal Server Error**

后端日志显示：
```
ValueError: Out of range float values are not JSON compliant: nan
when serializing dict item 'card_no'
when serializing list item 7
when serializing dict item 'error_details'
```

---

## 问题原因

### 根本原因：历史数据中的 NaN 值

1. **历史遗留问题**：在之前的导入操作中，`error_details` 字段存储了包含 `nan` 值的 JSON 数据
2. **JSON 解析问题**：`json.loads()` 将数据库中的 JSON 字符串解析为 Python 对象时，`nan` 被转换为 `float('nan')`
3. **序列化失败**：FastAPI 返回响应时，尝试将包含 `float('nan')` 的对象序列化为 JSON，导致 `ValueError`

### 为什么会有历史 NaN 数据？

在之前的导入逻辑中（已修复），当卡号为空时：
- pandas 读取为 `nan`
- 错误处理代码使用 `row.get('卡号', 'N/A')` 返回了 `nan` 而不是默认值
- 这个 `nan` 值被存储到数据库的 `error_details` JSON 字段中

虽然导入逻辑已经修复（不再产生新的 NaN 值），但**数据库中已存在的历史记录仍然包含 NaN 值**。

---

## 解决方案

### 修复：在查询时清理 NaN 值

**文件**：`backend/services/import_task_service.py`

**修改内容**：

#### 1. 添加 NaN 清理方法（第 15-27 行）

```python
@staticmethod
def _clean_nan_values(obj):
    """递归清理对象中的 NaN 值，替换为字符串"""
    import math

    if isinstance(obj, dict):
        return {k: ImportTaskService._clean_nan_values(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [ImportTaskService._clean_nan_values(item) for item in obj]
    elif isinstance(obj, float) and math.isnan(obj):
        return "未知"
    else:
        return obj
```

**说明**：
- 递归遍历字典和列表
- 检测到 `float('nan')` 时替换为字符串 `"未知"`
- 保持其他数据类型不变

#### 2. 在 get_import_tasks 中使用清理方法（第 46-52 行）

```python
items = []
for row in result:
    item = dict(row._mapping)
    # 解析错误详情JSON
    if item['error_details']:
        try:
            error_details = json.loads(item['error_details'])
            # 清理 NaN 值，确保可以序列化
            item['error_details'] = ImportTaskService._clean_nan_values(error_details)
        except:
            item['error_details'] = []
    items.append(item)
```

#### 3. 在 get_import_task 中使用清理方法（第 82-90 行）

```python
if result:
    item = dict(result._mapping)
    # 解析错误详情JSON
    if item['error_details']:
        try:
            error_details = json.loads(item['error_details'])
            # 清理 NaN 值，确保可以序列化
            item['error_details'] = ImportTaskService._clean_nan_values(error_details)
        except:
            item['error_details'] = []
    return item
```

---

## 验证方法

### 测试场景1：查询导入任务列表

```bash
GET /api/v1/cases/22/case-cards/import-tasks?page=1&page_size=20

预期结果：
- 返回 200 OK
- 返回导入任务列表
- error_details 中的 NaN 值被替换为 "未知"
- 不会出现 JSON 序列化错误
```

### 测试场景2：查询单个导入任务

```bash
GET /api/v1/cases/22/case-cards/import-tasks/15

预期结果：
- 返回 200 OK
- 返回单个导入任务详情
- error_details 正确序列化
```

### 测试场景3：包含历史 NaN 数据的记录

```
数据库中存在包含 NaN 的 error_details 记录

预期结果：
- 查询时自动清理 NaN 值
- 前端正常显示 "未知" 而不是报错
```

---

## 修改的文件

1. ✅ `backend/services/import_task_service.py` - 添加 NaN 清理逻辑
2. ✅ `docs/导入任务查询NaN序列化修复说明.md` - 本文档

---

## 相关问题

### 为什么不直接修复数据库中的数据？

1. **数据量可能很大**：如果有大量历史记录，批量更新会影响性能
2. **风险较高**：直接修改 JSON 字段可能导致数据损坏
3. **查询时清理更安全**：在读取时清理，不影响原始数据，且性能开销很小

### 为什么 json.loads() 会产生 NaN？

Python 的 `json` 模块在解析 JSON 时：
- 遇到 `NaN`、`Infinity`、`-Infinity` 这些 JavaScript 值时，会转换为 Python 的 `float('nan')`、`float('inf')`
- 但在序列化时，这些值不符合 JSON 标准，会抛出 `ValueError`

### 如何避免将来产生 NaN 数据？

已在之前的修复中实现：
1. 导入时检查卡号是否为空（使用 `pd.isna()`）
2. 异常处理时安全获取卡号（避免 `row.get()` 返回 NaN）
3. 确保所有错误信息中的字段都是字符串类型

---

## 总结

✅ 添加了 NaN 值清理方法
✅ 在查询导入任务时自动清理历史数据中的 NaN 值
✅ 解决了 JSON 序列化错误
✅ 不影响数据库原始数据
✅ 后端服务已重启

**修复完成日期**: 2026-03-09
**修改文件**: `backend/services/import_task_service.py`
**修改位置**: 3处（新增方法 + 2处调用）
**影响功能**: 导入任务查询

---

**🎯 导入任务查询功能已恢复正常！**
