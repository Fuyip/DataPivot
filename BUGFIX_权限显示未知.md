# Bug修复：权限显示"未知"问题

## 问题描述
超级管理员分配案件权限后，权限列表和案件列表中显示"未知"，且无法修改权限。

## 问题截图
用户提供的截图显示：权限列表中所有权限都显示为"未知"。

## 根本原因

### 1. 后端字段名不匹配
- 前端发送 `permission_level` 字段
- 后端 Schema 期望 `role` 字段
- 后端返回 `role` 字段
- 前端期望接收 `permission_level` 字段

### 2. 前端缺少 `user` 值的映射
- 数据库存储：`admin` 或 `user`
- 前端映射表只有：`admin`, `write`, `read`
- 缺少 `user` 的映射，导致显示"未知"

## 修复方案

### 后端修改

**文件**: `backend/api/v1/case_permissions.py`

1. **修改接口参数类型**
   - 从 `UserCasePermissionCreate/Update` Schema 改为 `dict`
   - 兼容前端的 `permission_level` 和后端的 `role` 字段

2. **添加字段映射**
   ```python
   # 接收参数时兼容两种字段名
   role = permission_data.get("role") or permission_data.get("permission_level")

   # 将前端三级权限映射为数据库两级权限
   if role in ["read", "write"]:
       role = "user"
   ```

3. **返回数据同时包含两个字段**
   ```python
   {
       "role": perm.role,
       "permission_level": perm.role,  # 兼容前端
       ...
   }
   ```

4. **统一权限检查逻辑**
   - 所有接口统一处理 `super_admin` 权限
   - `super_admin` 可以执行所有操作

**修改的接口**:
- `GET /cases/{case_id}/permissions` - 获取权限列表
- `POST /cases/{case_id}/permissions` - 创建权限
- `PUT /cases/{case_id}/permissions/{permission_id}` - 更新权限
- `DELETE /cases/{case_id}/permissions/{permission_id}` - 删除权限
- `GET /cases/users/{user_id}/cases` - 获取用户案件列表

### 前端修改

**文件**:
- `frontend/src/views/System/CaseManagement/index.vue`
- `frontend/src/views/System/CaseManagement/PermissionDialog.vue`

**修改内容**:
```javascript
// 将后端返回的 user 值映射为"读写"
function getPermissionLabel(permission) {
  const labelMap = {
    admin: '管理员',
    write: '读写',
    read: '只读',
    user: '读写'  // 后端返回 user 时映射为"读写"
  }
  return labelMap[permission] || '未知'
}

function getPermissionTagType(permission) {
  const typeMap = {
    admin: 'danger',
    write: 'warning',
    read: 'info',
    user: 'warning'  // 后端返回 user 时显示为警告色（橙色）
  }
  return typeMap[permission] || 'info'
}
```

## 修改文件清单

### 后端
- ✅ `backend/api/v1/case_permissions.py` - 修复字段名不匹配，添加兼容性处理

### 前端
- ✅ `frontend/src/views/System/CaseManagement/index.vue` - 添加 user 值映射
- ✅ `frontend/src/views/System/CaseManagement/PermissionDialog.vue` - 添加 user 值映射

### 文档
- ✅ `docs/权限问题修复总结.md` - 详细修复说明
- ✅ `test_permission_fix.md` - 测试步骤
- ✅ `BUGFIX_权限显示未知.md` - 本文档

## 测试步骤

### 1. 重启服务

**后端**:
```bash
cd /Users/yipf/DataPivot项目/DataPivot/backend
# 停止现有服务
# 重新启动
python main.py
```

**前端**:
```bash
cd /Users/yipf/DataPivot项目/DataPivot/frontend
npm run dev
```

### 2. 测试场景

#### 场景1：分配权限
1. 使用 super_admin 账号登录
2. 进入"案件管理"页面
3. 点击某个案件的"权限管理"按钮
4. 选择用户，选择权限级别（管理员/读写/只读）
5. 点击"添加"按钮

**预期结果**:
- ✅ 权限添加成功
- ✅ 权限列表中显示正确的权限标签（管理员/读写/只读）
- ✅ 不再显示"未知"或"普通用户"
- ✅ 显示授权人和授权时间

#### 场景2：修改权限
1. 在权限列表中点击"修改权限"按钮
2. 选择新的权限级别
3. 点击"确定"

**预期结果**:
- ✅ 权限更新成功
- ✅ 权限列表中显示更新后的权限

#### 场景3：案件列表显示
1. 返回"案件管理"页面
2. 查看案件列表中的"我的权限"列

**预期结果**:
- ✅ 显示正确的权限标签（管理员/读写/只读）
- ✅ 不再显示"未知"或"普通用户"

#### 场景4：撤销权限
1. 在权限列表中点击"撤销"按钮
2. 确认撤销

**预期结果**:
- ✅ 权限撤销成功
- ✅ 权限从列表中移除

## 注意事项

### 当前系统限制

由于数据库 `role` 字段只有 `admin` 和 `user` 两个值：
- ✅ 可以区分"管理员"权限
- ❌ 无法区分"读写"和"只读"权限
- 前端选择"读写"或"只读"时，后端都会存储为 `user`
- 显示时统一显示为"读写"（因为 `user` 映射为"读写"）

### 未来优化建议

如需真正实现三级权限（admin/write/read），需要：

1. **修改数据库表结构**
   ```sql
   ALTER TABLE user_case_permissions
   MODIFY COLUMN role VARCHAR(20) DEFAULT 'read'
   COMMENT '案件内角色: admin/write/read';
   ```

2. **更新现有数据**
   ```sql
   UPDATE user_case_permissions
   SET role = 'write'
   WHERE role = 'user';
   ```

3. **更新权限检查逻辑**
   - 修改 `backend/services/case_service.py` 中的权限级别映射
   - 更新所有相关的权限检查代码

4. **更新Schema验证**
   - 修改 `backend/schemas/case.py` 中的验证规则

## 修复时间
- 修复日期: 2026-03-04
- 修复人: Claude (AI Assistant)

## 相关文档
- [权限控制文档](./docs/权限控制文档.md)
- [权限问题修复总结](./docs/权限问题修复总结.md)
