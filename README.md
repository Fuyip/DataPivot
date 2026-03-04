# 数枢 (DataPivot)

## 项目简介

数枢（DataPivot）是一款面向经侦、刑侦等执法部门的综合数据分析平台，集成了数据清洗、资金穿透分析、人员情报关联分析等核心功能。系统通过对多源异构数据的整合与深度挖掘，为案件侦办提供高效的数据支撑。

## 核心功能模块

### 1. 银行流水数据清洗与分析
- 自动解压、清洗银行返回的多格式数据文件
- 支持人员信息、账户信息、子账户信息、强制措施信息、交易明细等多类型数据
- 智能账号卡号转换与去重
- 多线程并行处理，提升数据导入效率
- 资金穿透分析，追踪资金流向

### 2. 人员情报关联分析
- **社交关系分析**：微信/QQ共同好友挖掘，识别跨平台关联
- **档案共同关联人分析**：同乘车、同住宿、同出入境等行为关联
- **Telegram聊天记录导入与分析**
- **云搜数据整合**：人员基本信息、综合档案信息导入
- **人员总体归纳**：多源数据融合，构建完整人员画像

### 3. 设备与网络情报
- YM设备档案清洗（路由设备、出口路由等）
- 设备关联分析
- 网络行为轨迹分析

### 4. 文书与报告生成
- 经侦云查询文书自动生成
- 调单图片自动盖章
- 疑似员工卡交易报告生成
- 多维度数据可视化报告

## 技术架构

### 前端技术栈
- **框架**: Vue 3
- **UI组件库**: Element Plus / Ant Design Vue
- **状态管理**: Pinia
- **路由**: Vue Router
- **HTTP客户端**: Axios
- **图表可视化**: ECharts / D3.js
- **构建工具**: Vite

### 后端技术栈
- **框架**: FastAPI (Python 3.9+)
- **ORM**: SQLAlchemy
- **数据库**: MySQL 8.0+
- **数据处理**: Pandas, NumPy
- **异步任务**: Celery + Redis
- **日志**: Loguru
- **文档解析**: BeautifulSoup4, openpyxl
- **API文档**: FastAPI自动生成 (Swagger/OpenAPI)

### 数据库设计
- **关系型数据库**: MySQL 8.0
- **多数据库架构**:
  - `datapivot` 数据库：系统核心配置（用户认证、案件管理、系统配置）
  - 案件专用数据库：每个案件独立数据库，数据库名称为案件代码，表结构参考 `fx_test` 数据库
- **连接池**: SQLAlchemy连接池管理
- **字符集**: utf8mb4 (支持emoji和特殊字符)

## 项目结构

```
DataPivot/
├── backend/                    # 后端代码目录
│   ├── api/                   # API路由
│   │   ├── v1/               # API版本1
│   │   │   ├── bank.py       # 银行流水相关接口
│   │   │   ├── person.py     # 人员分析接口
│   │   │   ├── device.py     # 设备分析接口
│   │   │   └── report.py     # 报告生成接口
│   │   └── deps.py           # 依赖注入
│   ├── core/                 # 核心配置
│   │   ├── config.py         # 配置管理
│   │   ├── security.py       # 安全认证
│   │   └── database.py       # 数据库连接
│   ├── models/               # 数据模型
│   │   ├── bank.py          # 银行相关模型
│   │   ├── person.py        # 人员相关模型
│   │   └── device.py        # 设备相关模型
│   ├── schemas/              # Pydantic数据验证
│   ├── services/             # 业务逻辑层
│   │   ├── bank_service.py  # 银行流水处理
│   │   ├── person_service.py # 人员分析
│   │   └── report_service.py # 报告生成
│   ├── utils/                # 工具函数
│   │   ├── data_cleaner.py  # 数据清洗
│   │   └── file_handler.py  # 文件处理
│   └── main.py              # FastAPI应用入口
├── frontend/                  # 前端代码目录
│   ├── src/
│   │   ├── api/             # API请求封装
│   │   ├── assets/          # 静态资源
│   │   ├── components/      # 公共组件
│   │   ├── views/           # 页面视图
│   │   │   ├── Bank/       # 银行流水模块
│   │   │   ├── Person/     # 人员分析模块
│   │   │   ├── Device/     # 设备分析模块
│   │   │   └── Report/     # 报告模块
│   │   ├── router/          # 路由配置
│   │   ├── store/           # 状态管理
│   │   ├── utils/           # 工具函数
│   │   ├── App.vue
│   │   └── main.js
│   ├── public/
│   ├── package.json
│   └── vite.config.js
├── data/                      # 数据文件目录
│   ├── 云搜人员基本信息/
│   ├── 云搜人员综合信息/
│   ├── 微信好友/
│   ├── TG/
│   └── YM/
├── bank_statements/           # 银行流水处理目录
│   ├── raw/                  # 原始文件
│   ├── processing/           # 处理中
│   ├── processed/            # 已处理
│   ├── error_files/          # 错误文件
│   └── logs/                 # 日志
├── scripts/                   # 现有功能脚本（待迁移）
│   ├── 银行流水清洗重构-经侦-多线程.py
│   ├── 分析微信QQ共同好友.py
│   ├── 导入云搜人员基本信息.py
│   └── ...
├── tests/                     # 测试代码
├── docs/                      # 文档
├── .env                       # 环境变量配置
├── requirements.txt           # Python依赖
└── README.md                  # 项目说明
```

## 快速开始

### 环境要求
- Python 3.9+
- Node.js 16+
- MySQL 8.0+
- Redis 6.0+ (可选，用于异步任务)

### 后端启动

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置数据库连接等信息

# 3. 初始化数据库
python scripts/init_db.py

# 4. 启动后端服务
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 前端启动

```bash
# 1. 进入前端目录
cd frontend

# 2. 安装依赖
npm install

# 3. 启动开发服务器
npm run dev
```

### 访问应用
- 前端地址: http://localhost:5173
- 后端API文档: http://localhost:8000/docs
- 后端ReDoc文档: http://localhost:8000/redoc

## 配置说明

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
# 调试模式
DEBUG_MODE=true

# 数据库配置（系统核心数据库）
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DB=datapivot

# 海警API配置（如需要）
HAIJING_API_KEY=your_api_key
HAIJING_BASE_URL=https://api.example.com

# JWT密钥
SECRET_KEY=your_secret_key_here

# Redis配置（可选）
REDIS_HOST=localhost
REDIS_PORT=6379
```

## 数据库表结构

### 系统核心表（datapivot 数据库）
- `users`: 用户认证信息
- 案件管理相关表
- 系统配置表

### 案件分析表（案件专用数据库，如 case_20240301）
- `bank_people_info`: 银行人员信息
- `bank_account_info`: 银行账户信息
- `bank_all_statements`: 银行交易明细
- `29-微信好友`: 微信好友关系
- `29-qq好友`: QQ好友关系
- `人员总体归纳`: 人员综合信息
- `tg_messages`: Telegram聊天记录
- `case_card`: 案件卡号信息

**注**: 案件分析表结构参考 `fx_test` 数据库

## 开发规范

### 代码风格
- Python: PEP 8
- JavaScript: ESLint + Prettier
- 提交信息: Conventional Commits

### API设计规范
- RESTful API设计
- 统一响应格式
- 完善的错误处理
- 接口版本控制

## 部署指南

### Docker部署（推荐）

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d
```

### 生产环境部署
- 使用Nginx作为反向代理
- 使用Gunicorn + Uvicorn运行FastAPI
- 配置SSL证书
- 配置日志轮转
- 配置数据库备份

## 安全说明

本系统处理敏感执法数据，请务必：
- 部署在内网环境
- 启用强密码策略
- 配置访问控制
- 定期备份数据
- 记录操作日志
- 数据脱敏处理

## 许可证

本项目为内部使用系统，未经授权不得传播或商用。

## 联系方式

技术支持: [联系方式]
