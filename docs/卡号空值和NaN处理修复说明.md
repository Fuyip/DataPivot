# 卡号空值和 NaN 处理修复说明

## 修复日期
2026-03-09

## 问题描述

后端日志显示 JSON 序列化错误：
```
ValueError: Out of range float values are not JSON compliant: nan
when serializing dict item 'card_no'
```

导入任务的错误详情中包含了 `nan` 值，导致无法正确序列化为 JSON。

---

## 问题原因

### 原因1：卡号为空时的处理
当 Excel 文件中某行的卡号单元格为空时：
1. pandas 读取为 `nan` (float 类型)
2. 代码直接使用 `str(row['卡号'])` 会得到字符串 `"nan"`
3. 后续处理中，这个 `"nan"` 字符串可能被当作有效卡号
4. 在错误信息中包含 `nan` 值，导致 JSON 序列化失败

### 原因2：异常处理中的不安全获取
在异常处理代码中：
```python
errors.append({
    "row": index + 2,
    "card_no": row.get('卡号', 'N/A'),  # 可能返回 nan
    "error": str(e)
})
```

如果 `row['卡号']` 是 `nan`，`row.get('卡号', 'N/A')` 会返回 `nan` 而不是默认值 `'N/A'`。

---

## 解决方案

### 修复1：在循环开始时检查卡号

**文件**：`backend/services/case_card_service.py`

**修改位置**：第318-330行

**修改内容**：
```python
for index, row in df.iterrows():
    try:
        # 检查卡号是否为空
        if pd.isna(row['卡号']) or str(row['卡号']).strip() == '':
            error_count += 1
            errors.append({
                "row": index + 2,
                "card_no": "空",
                "error": "卡号不能为空"
            })
            continue

        card_no = str(row['卡号']).strip()
```

**说明**：
- 使用 `pd.isna()` 检查是否为 nan
- 如果为空，记录错误并跳过该行
- 避免后续代码处理无效的卡号

---

### 修复2：安全的异常处理

**文件**：`backend/services/case_card_service.py`

**修改位置**：第423-443行

**修改内容**：
```python
except IntegrityError:
    error_count += 1
    errors.append({
        "row": index + 2,
        "card_no": card_no if 'card_no' in locals() else "未知",
        "error": "卡号已存在"
    })
except Exception as e:
    error_count += 1
    # 安全获取卡号，避免 nan 值
    safe_card_no = "未知"
    if 'card_no' in locals():
        safe_card_no = card_no
    elif pd.notna(row.get('卡号')):
        safe_card_no = str(row.get('卡号'))

    errors.append({
        "row": index + 2,
        "card_no": safe_card_no,
        "error": str(e)
    })
```

**说明**：
- 检查 `card_no` 变量是否已定义
- 使用 `pd.notna()` 检查是否为 nan
- 确保 `card_no` 字段始终是字符串，不会是 nan

---

## pandas NaN 处理最佳实践

### 问题：dict.get() 不能处理 NaN
```python
# ❌ 错误：如果值是 nan，get() 会返回 nan 而不是默认值
value = row.get('column', 'default')  # 如果 row['column'] 是 nan，返回 nan

# ✅ 正确：先检查是否为 nan
value = row.get('column', 'default') if pd.notna(row.get('column')) else 'default'
```

### 问题：str() 会将 nan 转换为字符串 "nan"
```python
# ❌ 错误：nan 会变成字符串 "nan"
card_no = str(row['卡号'])  # 如果是 nan，得到 "nan"

# ✅ 正确：先检查是否为 nan
if pd.isna(row['卡号']):
    card_no = None
else:
    card_no = str(row['卡号'])
```

### 推荐的处理模式
```python
# 模式1：必填字段
if pd.isna(row['field']) or str(row['field']).strip() == '':
    # 记录错误，跳过该行
    continue
value = str(row['field']).strip()

# 模式2：可选字段
value = str(row.get('field', '')).strip() if pd.notna(row.get('field')) else None

# 模式3：带默认值的可选字段
value = str(row['field']).strip() if pd.notna(row['field']) else 'default_value'
```

---

## 验证方法

### 测试场景1：卡号为空
```
Excel 数据：
| 卡号 | 卡类型 |
|------|--------|
| (空) | 入款卡 |

预期结果：
- 拒绝导入
- 错误信息：{"row": 2, "card_no": "空", "error": "卡号不能为空"}
- 不会出现 JSON 序列化错误
```

### 测试场景2：异常情况下的卡号获取
```
Excel 数据：包含导致异常的数据

预期结果：
- 错误信息中 card_no 字段是字符串
- 不会包含 nan 值
- JSON 可以正常序列化
```

### 测试场景3：导入任务列表查询
```
GET /api/v1/cases/22/case-cards/import-tasks

预期结果：
- 返回 200 OK
- error_details 可以正常序列化
- 不会出现 "Out of range float values" 错误
```

---

## 修改的文件

1. ✅ `backend/services/case_card_service.py` - 添加卡号空值检查和安全的异常处理
2. ✅ `docs/卡号空值和NaN处理修复说明.md` - 本文档

---

## 相关问题

### 为什么 dict.get() 不能处理 NaN？
在 Python 中，`nan` 是一个实际存在的值（float 类型），不是 `None`。所以：
- `row.get('key', 'default')` 如果 `row['key']` 是 `nan`，会返回 `nan`
- 只有当 key 不存在时，才会返回默认值

### 为什么 JSON 不能序列化 NaN？
JSON 标准不支持 `NaN`、`Infinity` 等特殊浮点数值。Python 的 `json.dumps()` 在遇到这些值时会抛出 `ValueError`。

---

## 总结

✅ 添加了卡号空值检查
✅ 修复了异常处理中的 nan 问题
✅ 确保错误信息可以正常序列化
✅ 后端服务已重启

**修复完成日期**: 2026-03-09
**修改文件**: `backend/services/case_card_service.py`
**修改位置**: 2处
**影响功能**: 导入功能、错误处理

---

**🎯 NaN 处理问题已解决，导入任务可以正常查询！**
