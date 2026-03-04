# DataPivot 前端项目

## 项目说明

这是 DataPivot 数据情报分析系统的前端项目，采用 Vue 3 + Element Plus 构建。

## 技术栈

- **框架**: Vue 3 (Composition API)
- **构建工具**: Vite 5
- **UI 组件库**: Element Plus 2.5
- **状态管理**: Pinia 2.1
- **路由**: Vue Router 4
- **HTTP 客户端**: Axios 1.6
- **样式**: SCSS

## 项目结构

```
frontend/
├── src/
│   ├── api/                  # API 请求封装
│   │   ├── request.js       # Axios 实例配置
│   │   ├── auth.js          # 认证 API
│   │   └── user.js          # 用户管理 API
│   ├── assets/              # 静态资源
│   │   └── styles/          # 样式文件
│   ├── components/          # 公共组件
│   │   └── Layout/          # 布局组件
│   ├── router/              # 路由配置
│   ├── stores/              # Pinia 状态管理
│   ├── utils/               # 工具函数
│   ├── views/               # 页面视图
│   │   ├── Login/           # 登录页
│   │   ├── Dashboard/       # 仪表盘
│   │   └── System/          # 系统管理
│   ├── App.vue              # 根组件
│   └── main.js              # 入口文件
├── index.html               # HTML 模板
├── package.json             # 依赖配置
└── vite.config.js          # Vite 配置
```

## 开发指南

### 安装依赖

```bash
npm install
```

### 启动开发服务器

```bash
npm run dev
```

访问地址: http://localhost:5173

### 构建生产版本

```bash
npm run build
```

构建产物输出到 `dist/` 目录。

## 功能特性

### 已实现功能

- ✅ 用户登录（JWT Token 认证）
- ✅ 路由守卫（登录拦截、权限控制）
- ✅ Token 自动刷新机制
- ✅ 后台管理布局（顶部导航 + 侧边栏）
- ✅ 用户管理（列表、新增、编辑、删除、重置密码）
- ✅ 基于角色的权限控制（管理员/普通用户）
- ✅ 统一的错误处理
- ✅ 响应式布局

### 默认账户

- 用户名: `admin`
- 密码: `admin123`
- 角色: 管理员

## API 配置

开发环境下，前端会自动将 `/api` 请求代理到后端服务 `http://localhost:8000`。

确保后端服务已启动：

```bash
cd ..
source venv/bin/activate
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

## 注意事项

1. **后端依赖**: 前端需要后端 API 服务运行才能正常工作
2. **CORS 配置**: 后端已配置允许 `http://localhost:5173` 跨域访问
3. **Token 存储**: Token 存储在 localStorage 中
4. **权限控制**:
   - 普通用户只能访问仪表盘
   - 管理员可以访问用户管理等系统功能

## 开发建议

- 使用 Vue DevTools 进行调试
- 查看浏览器控制台了解 API 请求详情
- 参考 Element Plus 文档进行组件开发
