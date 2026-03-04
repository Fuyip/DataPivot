# DataPivot 用户管理指南

## 📋 概述

用户管理模块提供了完整的用户增删改查功能，包括用户列表查询、创建用户、更新用户信息、删除用户、修改角色和重置密码等功能。

## 🔐 权限说明

- **管理员 (admin)**: 拥有所有权限
- **普通用户 (user)**: 只能查看和修改自己的信息

## 📡 API 接口

### 1. 获取用户列表

**接口**: `GET /api/v1/users`

**权限**: 需要管理员权限

**查询参数**:
- `skip`: 跳过记录数（分页，默认 0）
- `limit`: 返回记录数（分页，默认 20，最大 100）
- `username`: 用户名模糊搜索（可选）
- `role`: 角色筛选 (admin/user)（可选）
- `is_active`: 激活状态筛选 (true/false)（可选）

**示例**:
```bash
# 获取所有用户
curl -X GET "http://localhost:8000/api/v1/users" \
  -H "Authorization: Bearer <your_token>"

# 分页查询
curl -X GET "http://localhost:8000/api/v1/users?skip=0&limit=10" \
  -H "Authorization: Bearer <your_token>"

# 搜索用户名包含 "admin" 的用户
curl -X GET "http://localhost:8000/api/v1/users?username=admin" \
  -H "Authorization: Bearer <your_token>"

# 查询所有管理员
curl -X GET "http://localhost:8000/api/v1/users?role=admin" \
  -H "Authorization: Bearer <your_token>"

# 查询已禁用的用户
curl -X GET "http://localhost:8000/api/v1/users?is_active=false" \
  -H "Authorization: Bearer <your_token>"
```

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "username": "admin",
        "full_name": "系统管理员",
        "email": null,
        "role": "admin",
        "is_active": true,
        "created_at": "2024-03-04T10:00:00",
        "updated_at": null
      }
    ],
    "total": 1,
    "skip": 0,
    "limit": 20
  }
}
```

### 2. 获取用户详情

**接口**: `GET /api/v1/users/{user_id}`

**权限**: 管理员或用户本人

**示例**:
```bash
curl -X GET "http://localhost:8000/api/v1/users/1" \
  -H "Authorization: Bearer <your_token>"
```

### 3. 创建用户

**接口**: `POST /api/v1/users`

**权限**: 需要管理员权限

**请求体**:
```json
{
  "username": "zhangsan",
  "password": "password123",
  "full_name": "张三",
  "email": "zhangsan@example.com"
}
```

**示例**:
```bash
curl -X POST "http://localhost:8000/api/v1/users" \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "zhangsan",
    "password": "password123",
    "full_name": "张三",
    "email": "zhangsan@example.com"
  }'
```

**响应示例**:
```json
{
  "code": 200,
  "message": "用户创建成功",
  "data": {
    "id": 2,
    "username": "zhangsan",
    "full_name": "张三",
    "email": "zhangsan@example.com",
    "role": "user",
    "is_active": true
  }
}
```

### 4. 更新用户信息

**接口**: `PUT /api/v1/users/{user_id}`

**权限**: 管理员或用户本人

**请求体** (所有字段可选):
```json
{
  "full_name": "张三丰",
  "email": "zhangsan_new@example.com",
  "password": "newpassword123",
  "is_active": false
}
```

**注意**:
- `is_active` 字段只有管理员可以修改
- 用户本人可以修改自己的姓名、邮箱和密码

**示例**:
```bash
curl -X PUT "http://localhost:8000/api/v1/users/2" \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "张三丰",
    "email": "zhangsan_new@example.com"
  }'
```

### 5. 删除用户

**接口**: `DELETE /api/v1/users/{user_id}`

**权限**: 需要管理员权限

**限制**: 不能删除自己的账户

**示例**:
```bash
curl -X DELETE "http://localhost:8000/api/v1/users/2" \
  -H "Authorization: Bearer <your_token>"
```

**响应示例**:
```json
{
  "code": 200,
  "message": "用户删除成功",
  "data": null
}
```

### 6. 修改用户角色

**接口**: `PUT /api/v1/users/{user_id}/role`

**权限**: 需要管理员权限

**查询参数**:
- `role`: 新角色 (admin 或 user)

**限制**: 不能修改自己的角色

**示例**:
```bash
# 将用户提升为管理员
curl -X PUT "http://localhost:8000/api/v1/users/2/role?role=admin" \
  -H "Authorization: Bearer <your_token>"

# 将管理员降级为普通用户
curl -X PUT "http://localhost:8000/api/v1/users/2/role?role=user" \
  -H "Authorization: Bearer <your_token>"
```

**响应示例**:
```json
{
  "code": 200,
  "message": "用户角色已更新为 admin",
  "data": {
    "id": 2,
    "username": "zhangsan",
    "role": "admin"
  }
}
```

### 7. 重置用户密码

**接口**: `PUT /api/v1/users/{user_id}/password`

**权限**: 管理员可以重置任何用户，用户只能重置自己

**查询参数**:
- `new_password`: 新密码（至少 6 位）

**示例**:
```bash
# 管理员重置其他用户密码
curl -X PUT "http://localhost:8000/api/v1/users/2/password?new_password=newpass123" \
  -H "Authorization: Bearer <your_token>"

# 用户重置自己的密码
curl -X PUT "http://localhost:8000/api/v1/users/2/password?new_password=mynewpass" \
  -H "Authorization: Bearer <your_token>"
```

## 🎯 使用场景

### 场景 1: 管理员创建新用户

```bash
# 1. 管理员登录
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}' | \
  python3 -c "import sys, json; print(json.load(sys.stdin)['data']['access_token'])")

# 2. 创建新用户
curl -X POST "http://localhost:8000/api/v1/users" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "analyst01",
    "password": "analyst123",
    "full_name": "分析员01",
    "email": "analyst01@company.com"
  }'
```

### 场景 2: 查询和筛选用户

```bash
# 查询所有激活的管理员
curl -X GET "http://localhost:8000/api/v1/users?role=admin&is_active=true" \
  -H "Authorization: Bearer $TOKEN"

# 搜索用户名包含 "analyst" 的用户
curl -X GET "http://localhost:8000/api/v1/users?username=analyst" \
  -H "Authorization: Bearer $TOKEN"
```

### 场景 3: 用户自己修改信息

```bash
# 1. 用户登录
USER_TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "analyst01", "password": "analyst123"}' | \
  python3 -c "import sys, json; print(json.load(sys.stdin)['data']['access_token'])")

# 2. 修改自己的邮箱和姓名
curl -X PUT "http://localhost:8000/api/v1/users/2" \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "高级分析员01",
    "email": "senior.analyst01@company.com"
  }'

# 3. 修改自己的密码
curl -X PUT "http://localhost:8000/api/v1/users/2/password?new_password=newpass456" \
  -H "Authorization: Bearer $USER_TOKEN"
```

### 场景 4: 管理员禁用用户

```bash
# 禁用用户账户
curl -X PUT "http://localhost:8000/api/v1/users/2" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"is_active": false}'

# 重新启用用户账户
curl -X PUT "http://localhost:8000/api/v1/users/2" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"is_active": true}'
```

## 🖥️ 前端集成示例

### Vue 3 用户管理组件

```vue
<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const users = ref([])
const loading = ref(false)
const pagination = ref({
  skip: 0,
  limit: 20,
  total: 0
})

// 获取用户列表
async function fetchUsers() {
  loading.value = true
  try {
    const response = await axios.get('/api/v1/users', {
      params: {
        skip: pagination.value.skip,
        limit: pagination.value.limit
      }
    })
    users.value = response.data.data.items
    pagination.value.total = response.data.data.total
  } catch (error) {
    console.error('获取用户列表失败', error)
  } finally {
    loading.value = false
  }
}

// 创建用户
async function createUser(userData) {
  try {
    await axios.post('/api/v1/users', userData)
    await fetchUsers() // 刷新列表
    alert('用户创建成功')
  } catch (error) {
    alert('创建失败: ' + error.response?.data?.message)
  }
}

// 删除用户
async function deleteUser(userId) {
  if (!confirm('确定要删除该用户吗？')) return

  try {
    await axios.delete(`/api/v1/users/${userId}`)
    await fetchUsers() // 刷新列表
    alert('用户删除成功')
  } catch (error) {
    alert('删除失败: ' + error.response?.data?.message)
  }
}

// 修改用户角色
async function changeRole(userId, newRole) {
  try {
    await axios.put(`/api/v1/users/${userId}/role`, null, {
      params: { role: newRole }
    })
    await fetchUsers() // 刷新列表
    alert('角色修改成功')
  } catch (error) {
    alert('修改失败: ' + error.response?.data?.message)
  }
}

onMounted(() => {
  fetchUsers()
})
</script>

<template>
  <div class="user-management">
    <h2>用户管理</h2>

    <button @click="showCreateDialog = true">创建用户</button>

    <table v-if="!loading">
      <thead>
        <tr>
          <th>ID</th>
          <th>用户名</th>
          <th>姓名</th>
          <th>邮箱</th>
          <th>角色</th>
          <th>状态</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="user in users" :key="user.id">
          <td>{{ user.id }}</td>
          <td>{{ user.username }}</td>
          <td>{{ user.full_name }}</td>
          <td>{{ user.email }}</td>
          <td>{{ user.role }}</td>
          <td>{{ user.is_active ? '激活' : '禁用' }}</td>
          <td>
            <button @click="changeRole(user.id, user.role === 'admin' ? 'user' : 'admin')">
              切换角色
            </button>
            <button @click="deleteUser(user.id)">删除</button>
          </td>
        </tr>
      </tbody>
    </table>

    <div v-else>加载中...</div>
  </div>
</template>
```

## ⚠️ 注意事项

1. **权限控制**: 所有用户管理操作都需要认证，大部分操作需要管理员权限
2. **不能自我操作**: 管理员不能删除自己或修改自己的角色
3. **唯一性约束**: 用户名和邮箱必须唯一
4. **密码安全**: 密码使用 bcrypt 加密存储，最少 6 位
5. **默认角色**: 新创建的用户默认角色为 `user`
6. **软删除建议**: 生产环境建议使用软删除而不是物理删除

## 📊 错误码说明

| 错误码 | 说明 |
|--------|------|
| 400 | 请求参数错误（用户名已存在、邮箱已使用等） |
| 401 | 未认证或 Token 无效 |
| 403 | 权限不足 |
| 404 | 用户不存在 |

## 🔗 相关文档

- [登录认证快速开始](QUICKSTART_AUTH.md)
- [API 接口设计文档](docs/API接口设计文档.md)

---

**DataPivot** - 数据情报分析系统
