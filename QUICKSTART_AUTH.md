# DataPivot 登录认证快速开始

## 🚀 快速启动

### 1. 启动服务

```bash
# 进入项目目录
cd /Users/yipf/DataPivot项目/DataPivot

# 激活虚拟环境
source venv/bin/activate

# 启动后端服务
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

服务启动后访问：
- **API 文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health

### 2. 默认账户

- **用户名**: `admin`
- **密码**: `admin123`
- **角色**: `admin`

⚠️ **重要**: 生产环境部署后请立即修改默认密码！

## 📡 API 接口

### 登录
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

**响应示例**:
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "access_token": "eyJhbGc...",
    "token_type": "bearer",
    "expires_in": 86400,
    "user": {
      "id": 1,
      "username": "admin",
      "role": "admin"
    }
  }
}
```

### 获取当前用户信息
```bash
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <your_token>"
```

### 刷新 Token
```bash
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Authorization: Bearer <your_token>"
```

### 登出
```bash
curl -X POST http://localhost:8000/api/v1/auth/logout \
  -H "Authorization: Bearer <your_token>"
```

## 🔧 配置说明

### 数据库架构

DataPivot 采用多数据库架构：

- **`datapivot` 数据库**：存储系统核心配置
  - 用户认证（users 表）
  - 案件管理
  - 系统配置

- **案件专用数据库**：每个案件独立数据库
  - 数据库名称：案件代码（如 `case_20240301`）
  - 表结构参考：`fx_test` 数据库中的表结构
  - 包含案件相关的所有分析数据

### 环境变量 (.env)

```env
# 数据库配置（系统核心数据库）
MYSQL_HOST=10.8.0.5
MYSQL_PORT=3306
MYSQL_USER=fuyip_net_gk
MYSQL_PASSWORD=Fuyip@235813
MYSQL_DB=datapivot

# JWT 配置
SECRET_KEY=your-secret-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440

# CORS 配置
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

## 📝 前端集成示例

### JavaScript/Axios

```javascript
// 登录
async function login(username, password) {
  const response = await axios.post('http://localhost:8000/api/v1/auth/login', {
    username,
    password
  });

  const { access_token } = response.data.data;
  localStorage.setItem('token', access_token);
  return response.data;
}

// 请求拦截器 - 自动添加 Token
axios.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 获取当前用户
async function getCurrentUser() {
  const response = await axios.get('http://localhost:8000/api/v1/auth/me');
  return response.data.data;
}
```

### Vue 3 示例

```vue
<script setup>
import { ref } from 'vue'
import axios from 'axios'

const username = ref('admin')
const password = ref('admin123')
const user = ref(null)

async function handleLogin() {
  try {
    const response = await axios.post('http://localhost:8000/api/v1/auth/login', {
      username: username.value,
      password: password.value
    })

    const { access_token, user: userData } = response.data.data
    localStorage.setItem('token', access_token)
    user.value = userData

    console.log('登录成功', userData)
  } catch (error) {
    console.error('登录失败', error.response?.data)
  }
}
</script>

<template>
  <div>
    <input v-model="username" placeholder="用户名" />
    <input v-model="password" type="password" placeholder="密码" />
    <button @click="handleLogin">登录</button>
    <div v-if="user">欢迎, {{ user.full_name }}</div>
  </div>
</template>
```

## 🛠️ 开发工具

### 使用 Postman/Insomnia 测试

1. **登录获取 Token**
   - Method: POST
   - URL: `http://localhost:8000/api/v1/auth/login`
   - Body (JSON):
     ```json
     {
       "username": "admin",
       "password": "admin123"
     }
     ```

2. **使用 Token 访问受保护接口**
   - Method: GET
   - URL: `http://localhost:8000/api/v1/auth/me`
   - Headers:
     ```
     Authorization: Bearer <your_token>
     ```

### 使用 Swagger UI (推荐)

访问 http://localhost:8000/docs，可以直接在浏览器中测试所有接口：

1. 点击 `/api/v1/auth/login` 接口
2. 点击 "Try it out"
3. 输入用户名和密码
4. 点击 "Execute"
5. 复制返回的 `access_token`
6. 点击页面右上角的 "Authorize" 按钮
7. 输入 `Bearer <your_token>`
8. 现在可以测试其他需要认证的接口

## ⚠️ 常见问题

### 1. 服务启动失败

**问题**: `ModuleNotFoundError: No module named 'xxx'`

**解决**:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### 2. 数据库连接失败

**问题**: `Can't connect to MySQL server`

**解决**:
- 检查 `.env` 文件中的数据库配置
- 确认数据库服务正在运行
- 检查网络连接和防火墙设置

### 3. Token 无效

**问题**: `{"detail": "无效的认证凭证"}`

**解决**:
- 检查 Token 是否过期（默认 24 小时）
- 确认 Authorization 头格式正确：`Bearer <token>`
- 重新登录获取新 Token

### 4. CORS 错误

**问题**: 前端请求被 CORS 策略阻止

**解决**:
在 `.env` 文件中添加前端地址到 `CORS_ORIGINS`：
```env
CORS_ORIGINS=http://localhost:5173,http://localhost:3000,http://your-frontend-url
```

## 📚 相关文档

- [完整实施总结](LOGIN_AUTH_SUMMARY.md)
- [API 接口设计文档](docs/API接口设计文档.md)
- [开发指南](docs/开发指南.md)
- [数据库开发规范](docs/DATABASE_DEVELOPMENT.md)

## 🔐 安全建议

1. ✅ 生产环境使用强随机 SECRET_KEY
2. ✅ 使用 HTTPS 加密传输
3. ✅ 定期更新依赖包
4. ✅ 实施 IP 白名单（如果需要）
5. ✅ 启用请求频率限制
6. ✅ 记录登录日志和异常访问
7. ✅ 定期备份数据库

---

**DataPivot** - 数据情报分析系统
