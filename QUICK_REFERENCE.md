# DataPivot 快速参考指南

## 🚀 启动服务

```bash
cd /Users/yipf/DataPivot项目/DataPivot
source venv/bin/activate
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

## 🔗 常用链接

- **API 文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health

## 🔐 默认账户

- **用户名**: `admin`
- **密码**: `admin123`

## 📡 常用 API 命令

### 1. 登录获取 Token

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

### 2. 保存 Token 到环境变量

```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}' | \
  python3 -c "import sys, json; print(json.load(sys.stdin)['data']['access_token'])")
```

### 3. 获取当前用户信息

```bash
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

### 4. 获取用户列表

```bash
curl -X GET http://localhost:8000/api/v1/users \
  -H "Authorization: Bearer $TOKEN"
```

### 5. 创建新用户

```bash
curl -X POST http://localhost:8000/api/v1/users \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "password": "password123",
    "full_name": "新用户",
    "email": "newuser@example.com"
  }'
```

### 6. 更新用户信息

```bash
curl -X PUT http://localhost:8000/api/v1/users/2 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "更新后的姓名",
    "email": "updated@example.com"
  }'
```

### 7. 修改用户角色

```bash
# 提升为管理员
curl -X PUT "http://localhost:8000/api/v1/users/2/role?role=admin" \
  -H "Authorization: Bearer $TOKEN"

# 降级为普通用户
curl -X PUT "http://localhost:8000/api/v1/users/2/role?role=user" \
  -H "Authorization: Bearer $TOKEN"
```

### 8. 重置用户密码

```bash
curl -X PUT "http://localhost:8000/api/v1/users/2/password?new_password=newpass123" \
  -H "Authorization: Bearer $TOKEN"
```

### 9. 删除用户

```bash
curl -X DELETE http://localhost:8000/api/v1/users/2 \
  -H "Authorization: Bearer $TOKEN"
```

### 10. 搜索和筛选用户

```bash
# 搜索用户名
curl -X GET "http://localhost:8000/api/v1/users?username=admin" \
  -H "Authorization: Bearer $TOKEN"

# 按角色筛选
curl -X GET "http://localhost:8000/api/v1/users?role=admin" \
  -H "Authorization: Bearer $TOKEN"

# 按激活状态筛选
curl -X GET "http://localhost:8000/api/v1/users?is_active=true" \
  -H "Authorization: Bearer $TOKEN"

# 分页查询
curl -X GET "http://localhost:8000/api/v1/users?skip=0&limit=10" \
  -H "Authorization: Bearer $TOKEN"
```

## 🗄️ 数据库操作

### 连接数据库

```bash
mysql -h 10.8.0.5 -u fuyip_net_gk -p datapivot
```

### 查看用户表

```sql
SELECT id, username, full_name, email, role, is_active, created_at
FROM users
ORDER BY created_at DESC;
```

### 统计用户数量

```sql
SELECT
  role,
  COUNT(*) as count,
  SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) as active_count
FROM users
GROUP BY role;
```

### 备份用户表

```bash
mysqldump -h 10.8.0.5 -u fuyip_net_gk -p datapivot users > backup/users_$(date +%Y%m%d).sql
```

## 🔧 数据库初始化

### 方法 1: 使用 Python 脚本

```bash
source venv/bin/activate
python backend/utils/init_db.py
```

### 方法 2: 使用 SQL 脚本

```bash
mysql -h 10.8.0.5 -u fuyip_net_gk -p datapivot < sql/init/001_create_users_table.sql
```

## 🐛 故障排查

### 服务无法启动

```bash
# 检查端口占用
lsof -i :8000

# 检查虚拟环境
which python
pip list | grep fastapi

# 重新安装依赖
pip install -r requirements.txt
```

### 数据库连接失败

```bash
# 测试数据库连接
mysql -h 10.8.0.5 -u fuyip_net_gk -p datapivot -e "SELECT 1"

# 检查 .env 配置
cat .env | grep MYSQL
```

### Token 无效

```bash
# 重新登录获取新 Token
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}' | \
  python3 -c "import sys, json; print(json.load(sys.stdin)['data']['access_token'])")

echo $TOKEN
```

## 📊 监控命令

### 检查服务状态

```bash
# 检查进程
ps aux | grep uvicorn

# 检查健康状态
curl http://localhost:8000/health

# 查看日志（如果使用 systemd）
journalctl -u datapivot -f
```

### 查看数据库状态

```bash
mysql -h 10.8.0.5 -u fuyip_net_gk -p -e "
  SELECT
    table_name,
    table_rows,
    ROUND(data_length / 1024 / 1024, 2) AS 'Size (MB)'
  FROM information_schema.tables
  WHERE table_schema = 'datapivot'
"
```

## 📚 相关文档

- [系统状态报告](SYSTEM_STATUS.md)
- [用户管理指南](USER_MANAGEMENT_GUIDE.md)
- [用户管理功能总结](USER_MANAGEMENT_SUMMARY.md)
- [登录认证快速开始](QUICKSTART_AUTH.md)
- [数据库表结构文档](docs/DATABASE_USERS_TABLE.md)

## ⚠️ 安全提醒

1. 生产环境必须修改默认密码
2. 使用强随机 SECRET_KEY
3. 启用 HTTPS
4. 定期备份数据库
5. 记录操作日志
6. 实施 IP 白名单

---

**DataPivot** - 数据情报分析系统
