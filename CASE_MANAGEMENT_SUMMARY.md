# 案件管理功能实施完成

## 已完成的工作

### 1. 数据模型层
- ✅ 创建了 `backend/models/case.py`
  - `Case` 模型：案件信息表
  - `UserCasePermission` 模型：用户案件权限关联表

### 2. Schema定义层
- ✅ 创建了 `backend/schemas/case.py`
  - 案件相关的请求/响应Schema
  - 权限相关的请求/响应Schema

### 3. 服务层
- ✅ 创建了 `backend/services/case_service.py`
  - `create_case_database()`: 动态创建案件数据库
  - `drop_case_database()`: 删除案件数据库
  - `get_case_database_url()`: 获取案件数据库连接URL
  - `check_case_permission()`: 检查用户权限
  - `get_user_cases()`: 获取用户有权限的案件列表
  - `get_case_permission_level()`: 获取用户权限级别
  - `require_case_permission()`: 权限检查依赖注入

### 4. API路由层
- ✅ 创建了 `backend/api/v1/cases.py` - 案件管理API
  - `GET /api/v1/cases` - 获取案件列表（支持分页、搜索、筛选）
  - `GET /api/v1/cases/{case_id}` - 获取案件详情
  - `POST /api/v1/cases` - 创建案件（自动创建数据库）
  - `PUT /api/v1/cases/{case_id}` - 更新案件信息
  - `DELETE /api/v1/cases/{case_id}` - 删除案件（软删除）
  - `POST /api/v1/cases/{case_id}/archive` - 归档案件

- ✅ 创建了 `backend/api/v1/case_permissions.py` - 权限管理API
  - `GET /api/v1/cases/{case_id}/permissions` - 获取案件的所有权限
  - `POST /api/v1/cases/{case_id}/permissions` - 分配案件权限
  - `PUT /api/v1/cases/{case_id}/permissions/{permission_id}` - 修改权限级别
  - `DELETE /api/v1/cases/{case_id}/permissions/{permission_id}` - 撤销权限
  - `GET /api/v1/users/{user_id}/cases` - 获取用户的案件列表

### 5. 数据库迁移
- ✅ 更新了 `backend/models/__init__.py` - 添加模型导入
- ✅ 创建了 `sql/init/002_create_cases_tables.sql` - SQL迁移脚本
- ✅ 创建了 `create_case_tables.py` - Python表创建脚本
- ✅ 成功创建了数据库表：
  - `cases` - 案件表
  - `user_case_permissions` - 用户案件权限表

### 6. 应用集成
- ✅ 更新了 `backend/main.py` - 注册案件管理路由

## 功能特性

### 权限控制
- **三级权限**：read（只读）、write（读写）、admin（管理）
- **系统管理员**：拥有所有案件的完全权限
- **案件创建者**：自动获得该案件的admin权限
- **权限保护**：不允许撤销创建者的权限

### 数据库隔离
- 每个案件拥有独立的数据库
- 数据库命名规则：`case_{案件ID}_{时间戳}`
- 自动创建和管理案件数据库

### 安全特性
- 细粒度的权限控制
- 案件名称和编号唯一性检查
- 软删除机制（保留数据）
- 权限级别验证

## API文档

启动后端服务后，访问 http://localhost:8000/docs 查看完整的API文档。

## 使用示例

### 1. 创建案件（管理员）
```bash
curl -X POST http://localhost:8000/api/v1/cases \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "case_name": "测试案件001",
    "case_code": "CASE001",
    "description": "这是一个测试案件"
  }'
```

### 2. 分配权限（案件管理员）
```bash
curl -X POST http://localhost:8000/api/v1/cases/1/permissions \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 2,
    "permission_level": "write"
  }'
```

### 3. 获取案件列表
```bash
curl -X GET "http://localhost:8000/api/v1/cases?page=1&page_size=10" \
  -H "Authorization: Bearer <token>"
```

### 4. 获取用户的案件列表
```bash
curl -X GET http://localhost:8000/api/v1/users/2/cases \
  -H "Authorization: Bearer <token>"
```

## 后续工作

### 前端开发（可选）
1. 创建案件管理页面 `frontend/src/views/System/CaseManagement/`
2. 创建权限管理对话框
3. 封装案件管理API `frontend/src/api/case.js`
4. 添加路由配置

### 功能增强
1. 案件数据库模板管理
2. 批量权限分配
3. 权限审计日志
4. 案件数据导入导出
5. 案件统计报表

## 注意事项

1. 确保MySQL用户有创建数据库的权限
2. 案件数据库名称不能重复
3. 删除案件默认为软删除，不会删除数据库
4. 如需硬删除，需要手动调用 `drop_case_database()` 函数
