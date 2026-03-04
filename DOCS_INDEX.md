# 数枢 (DataPivot) - 文档清单

## 📚 所有文档列表

### 根目录文档
| 文件名 | 说明 | 行数 |
|--------|------|------|
| [README.md](README.md) | 项目主文档，包含项目概述、功能介绍、快速开始 | ~200 |
| [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) | 项目总结和快速导航 | ~150 |
| [DOCUMENTATION_REPORT.md](DOCUMENTATION_REPORT.md) | 文档生成完成报告 | ~200 |
| [QUICK_REFERENCE.md](QUICK_REFERENCE.md) | ⭐ 快速参考指南，包含常用命令和操作 | ~300 |
| [SYSTEM_STATUS.md](SYSTEM_STATUS.md) | ⭐ 系统当前状态报告，包含所有功能清单 | ~250 |
| [QUICKSTART_AUTH.md](QUICKSTART_AUTH.md) | ⭐ 登录认证快速开始指南 | ~260 |
| [USER_MANAGEMENT_GUIDE.md](USER_MANAGEMENT_GUIDE.md) | ⭐ 用户管理完整指南，包含所有 API 接口说明 | ~460 |
| [USER_MANAGEMENT_SUMMARY.md](USER_MANAGEMENT_SUMMARY.md) | 用户管理功能实施总结 | ~270 |
| [LOGIN_AUTH_SUMMARY.md](LOGIN_AUTH_SUMMARY.md) | 登录认证实施总结 | ~200 |

### docs/ 目录文档
| 文件名 | 说明 | 行数 |
|--------|------|------|
| [docs/README.md](docs/README.md) | 文档索引和使用指南 | ~100 |
| [docs/技术选型文档.md](docs/技术选型文档.md) | 详细的技术栈选型说明，包含前后端、数据库、部署等 | ~600 |
| [docs/API接口设计文档.md](docs/API接口设计文档.md) | 完整的RESTful API接口规范 | ~500 |
| [docs/开发指南.md](docs/开发指南.md) | 开发环境搭建、代码规范、调试技巧 | ~700 |
| [docs/部署文档.md](docs/部署文档.md) | 生产环境部署、监控、备份策略 | ~800 |
| [docs/功能清单.md](docs/功能清单.md) | 已实现和待开发功能详细清单 | ~400 |
| [docs/DATABASE_USERS_TABLE.md](docs/DATABASE_USERS_TABLE.md) | ⭐ 用户表结构详细文档 | ~230 |
| [docs/DATABASE_DEVELOPMENT.md](docs/DATABASE_DEVELOPMENT.md) | 数据库开发规范 | ~300 |

### 配置文件
| 文件名 | 说明 |
|--------|------|
| [requirements.txt](requirements.txt) | Python依赖包列表 |
| [.gitignore](.gitignore) | Git忽略文件配置 |
| [.env.example](.env.example) | 环境变量配置模板 |
| [docker-compose.yml](docker-compose.yml) | Docker容器编排配置 |
| [docker/backend/Dockerfile](docker/backend/Dockerfile) | 后端Docker镜像配置 |
| [docker/frontend/Dockerfile](docker/frontend/Dockerfile) | 前端Docker镜像配置 |
| [docker/nginx/nginx.conf](docker/nginx/nginx.conf) | Nginx配置文件 |
| [docker/mysql/conf.d/custom.cnf](docker/mysql/conf.d/custom.cnf) | MySQL配置文件 |

### 脚本文件
| 文件名 | 说明 |
|--------|------|
| [init.sh](init.sh) | 项目初始化脚本（创建目录、安装依赖等） |

## 📖 文档内容速查

### README.md
- 项目简介和核心功能
- 技术架构图
- 项目结构说明
- 快速开始指南
- 配置说明
- 开发规范
- 部署指南
- 安全说明

### 技术选型文档.md
**第1章**: 技术选型概述
- 选型原则
- 整体架构图

**第2章**: 前端技术选型
- Vue 3核心框架
- Element Plus UI组件库
- Pinia状态管理
- Vue Router路由
- Axios HTTP客户端
- ECharts/D3.js数据可视化
- Vite构建工具

**第3章**: 后端技术选型
- FastAPI核心框架
- SQLAlchemy ORM
- Pandas/NumPy数据处理
- Celery异步任务
- Loguru日志管理
- Pydantic数据验证

**第4章**: 数据库技术选型
- MySQL 8.0主数据库
- Redis缓存（可选）

**第5-11章**: 开发工具、部署、安全、监控、性能优化等

### API接口设计文档.md
**第1章**: 接口规范
- 统一响应格式
- HTTP状态码
- 认证方式

**第2章**: 认证模块
- 登录接口
- Token刷新
- 退出登录

**第3章**: 银行流水模块
- 文件上传
- 任务状态查询
- 交易明细查询
- 资金穿透分析
- 报告导出

**第4章**: 人员分析模块
- 数据导入
- 人员查询
- 共同好友分析
- 档案关联分析
- 关系图谱

**第5-9章**: 设备分析、报告生成、系统管理、WebSocket、错误码

### 开发指南.md
**第1章**: 开发环境搭建
- 系统要求
- 工具推荐
- 环境配置步骤

**第2章**: 项目结构说明
- 后端目录结构
- 前端目录结构

**第3章**: 代码规范
- Python代码规范
- JavaScript代码规范
- Git提交规范

**第4-9章**: 开发流程、调试技巧、测试指南、性能优化、常见问题

### 部署文档.md
**第1章**: 部署架构
- 生产环境架构图
- 服务器配置建议

**第2章**: 服务器准备
- 系统要求
- 基础软件安装

**第3章**: 数据库部署
- MySQL配置
- Redis安装

**第4-14章**: 后端部署、前端部署、监控日志、备份策略、安全加固、故障排查等

### 功能清单.md
**第1章**: 已实现功能
- 15个现有Python脚本详细说明

**第2章**: 待开发功能
- 后端API模块
- 前端界面模块
- 数据可视化模块
- 高级功能

**第3-5章**: 功能优先级、技术债务、开发路线图

## 🎯 快速查找

### 我想了解...

**项目概况**
→ 阅读 [README.md](README.md)

**技术架构**
→ 阅读 [docs/技术选型文档.md](docs/技术选型文档.md)

**如何开发**
→ 阅读 [docs/开发指南.md](docs/开发指南.md)

**API接口规范**
→ 阅读 [docs/API接口设计文档.md](docs/API接口设计文档.md)

**如何部署**
→ 阅读 [docs/部署文档.md](docs/部署文档.md)

**功能进度**
→ 阅读 [docs/功能清单.md](docs/功能清单.md)

**快速开始**
→ 阅读 [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)

**系统当前状态**
→ 阅读 [SYSTEM_STATUS.md](SYSTEM_STATUS.md) ⭐

**登录认证**
→ 阅读 [QUICKSTART_AUTH.md](QUICKSTART_AUTH.md) ⭐

**用户管理**
→ 阅读 [USER_MANAGEMENT_GUIDE.md](USER_MANAGEMENT_GUIDE.md) ⭐

**数据库表结构**
→ 阅读 [docs/DATABASE_USERS_TABLE.md](docs/DATABASE_USERS_TABLE.md) ⭐

**常用命令**
→ 阅读 [QUICK_REFERENCE.md](QUICK_REFERENCE.md) ⭐

### 我遇到了问题...

**环境搭建问题**
→ 查看 [docs/开发指南.md](docs/开发指南.md) 第8节"常见问题"

**部署问题**
→ 查看 [docs/部署文档.md](docs/部署文档.md) 第11节"故障排查"

**数据库连接问题**
→ 查看 [docs/开发指南.md](docs/开发指南.md) 第8.1节

**Docker问题**
→ 查看 [docs/部署文档.md](docs/部署文档.md) 第11节

**登录认证问题**
→ 查看 [QUICKSTART_AUTH.md](QUICKSTART_AUTH.md) 常见问题部分 ⭐

**用户管理问题**
→ 查看 [USER_MANAGEMENT_GUIDE.md](USER_MANAGEMENT_GUIDE.md) 注意事项部分 ⭐

**服务启动失败**
→ 查看 [QUICK_REFERENCE.md](QUICK_REFERENCE.md) 故障排查部分 ⭐

## 📊 文档统计

- **文档总数**: 24个文件
- **文档总行数**: 约5500行
- **核心文档**: 15个
- **配置文件**: 8个
- **脚本文件**: 1个
- **涵盖内容**:
  - 项目介绍 ✅
  - 技术选型 ✅
  - API设计 ✅
  - 开发规范 ✅
  - 部署指南 ✅
  - 功能清单 ✅
  - Docker配置 ✅
  - 初始化脚本 ✅
  - 登录认证系统 ✅
  - 用户管理系统 ✅
  - 数据库文档 ✅
  - 快速参考指南 ✅

## 🚀 推荐阅读路径

### 路径1: 快速了解（15分钟）
1. README.md
2. PROJECT_SUMMARY.md
3. SYSTEM_STATUS.md ⭐
4. docs/功能清单.md

### 路径2: 快速上手使用（30分钟）
1. QUICKSTART_AUTH.md ⭐
2. QUICK_REFERENCE.md ⭐
3. USER_MANAGEMENT_GUIDE.md ⭐
4. 访问 http://localhost:8000/docs

### 路径3: 开发准备（1小时）
1. README.md
2. docs/技术选型文档.md
3. docs/开发指南.md
4. docs/API接口设计文档.md
5. docs/DATABASE_USERS_TABLE.md ⭐

### 路径4: 部署上线（2小时）
1. README.md
2. docs/技术选型文档.md
3. docs/部署文档.md
4. docker-compose.yml

### 路径5: 全面掌握（4小时）
1. README.md
2. PROJECT_SUMMARY.md
3. SYSTEM_STATUS.md ⭐
4. docs/技术选型文档.md
5. docs/API接口设计文档.md
6. docs/开发指南.md
7. docs/部署文档.md
8. docs/功能清单.md
9. USER_MANAGEMENT_GUIDE.md ⭐
10. docs/DATABASE_USERS_TABLE.md ⭐

## 📝 文档维护

### 文档更新原则
- 代码变更时同步更新文档
- 每个版本发布前检查文档准确性
- 定期审查文档完整性
- 及时补充常见问题

### 文档版本
- **当前版本**: v1.0.0
- **生成日期**: 2026-03-04
- **最后更新**: 2026-03-04（新增登录认证和用户管理文档）
- **下次更新**: 功能开发完成后

## 🔗 相关链接

- [FastAPI官方文档](https://fastapi.tiangolo.com/zh/)
- [Vue 3官方文档](https://cn.vuejs.org/)
- [Element Plus文档](https://element-plus.org/zh-CN/)
- [SQLAlchemy文档](https://docs.sqlalchemy.org/)
- [Docker文档](https://docs.docker.com/)
- [MySQL 8.0文档](https://dev.mysql.com/doc/)

---

**提示**: 所有文档均使用Markdown格式编写，可使用任何Markdown阅读器查看。推荐使用VS Code + Markdown Preview Enhanced插件获得最佳阅读体验。
