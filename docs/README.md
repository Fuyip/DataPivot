# 数枢 (DataPivot) - 项目文档索引

## 📚 文档目录

### 核心文档
- [README.md](../README.md) - 项目概述和快速开始
- [技术选型文档.md](技术选型文档.md) - 详细的技术栈选型说明
- [API接口设计文档.md](API接口设计文档.md) - 完整的API接口规范
- [开发指南.md](开发指南.md) - 开发环境搭建和编码规范
- [部署文档.md](部署文档.md) - 生产环境部署指南

### 数据库文档
- [DATABASE_QUICKSTART.md](DATABASE_QUICKSTART.md) - 数据库工具快速开始 ⭐ 推荐
- [DATABASE_DEVELOPMENT.md](DATABASE_DEVELOPMENT.md) - 数据库开发规范和连接配置
- [DATABASE_SCHEMA_GENERATOR.md](DATABASE_SCHEMA_GENERATOR.md) - 数据库结构生成工具使用指南
- [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md) - 数据库结构文档（自动生成）

### 项目信息
- **项目名称**: 数枢 (DataPivot)
- **版本**: 1.0.0
- **开发语言**: Python 3.9+ / JavaScript (Vue 3)
- **数据库**: MySQL 8.0+
- **框架**: FastAPI + Vue 3

## 🎯 核心功能

### 1. 银行流水数据清洗
- 自动解压多格式文件
- 智能数据清洗和转换
- 账号卡号自动转换
- 多线程并行处理
- 资金穿透分析

### 2. 人员情报关联分析
- 微信/QQ共同好友分析
- 档案共同关联人挖掘
- Telegram聊天记录分析
- 云搜数据整合
- 人员关系图谱

### 3. 设备与网络情报
- YM设备档案清洗
- 设备关联分析
- 网络行为轨迹

### 4. 报告生成
- 经侦云查询文书
- 调单图片盖章
- 综合分析报告
- 数据可视化

## 🏗️ 技术架构

```
前端 (Vue 3 + Element Plus)
         ↓
API网关 (FastAPI)
         ↓
业务逻辑层 (Services)
         ↓
数据访问层 (SQLAlchemy)
         ↓
数据存储 (MySQL 8.0)
```

## 📖 文档使用指南

### 新手入门
1. 阅读 [README.md](../README.md) 了解项目概况
2. 查看 [技术选型文档.md](技术选型文档.md) 理解技术栈
3. 按照 [开发指南.md](开发指南.md) 搭建开发环境
4. 使用 [DATABASE_QUICKSTART.md](DATABASE_QUICKSTART.md) 初始化数据库
5. 参考 [API接口设计文档.md](API接口设计文档.md) 进行开发

### 部署上线
1. 阅读 [部署文档.md](部署文档.md)
2. 准备服务器环境
3. 配置数据库和环境变量
4. 按步骤部署应用
5. 配置监控和备份

### 日常开发
1. 遵循 [开发指南.md](开发指南.md) 中的代码规范
2. 遵循 [DATABASE_DEVELOPMENT.md](DATABASE_DEVELOPMENT.md) 中的数据库规范
3. 参考 [API接口设计文档.md](API接口设计文档.md) 设计接口
4. 编写单元测试
5. 数据库结构变更后运行 `python generate_db_schema.py`
6. 提交代码前进行代码审查

## 🔧 快速命令

### 开发环境
```bash
# 后端启动
source venv/bin/activate
uvicorn backend.main:app --reload

# 前端启动
cd frontend
npm run dev

# 运行测试
pytest tests/

# 生成数据库结构
python generate_db_schema.py
```

### 生产环境
```bash
# Docker部署
docker-compose up -d

# 查看日志
docker-compose logs -f

# 重启服务
docker-compose restart
```

## 📝 更新日志

### v1.0.0 (2024-03-04)
- 初始版本发布
- 完成核心功能开发
- 完善项目文档

## 🤝 贡献指南

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'feat: Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

## 📞 联系方式

- 技术支持: [联系方式]
- 问题反馈: [Issue地址]

## 📄 许可证

本项目为内部使用系统，未经授权不得传播或商用。

---

**注意**: 本系统处理敏感执法数据，请务必：
- 部署在内网环境
- 启用强密码策略
- 配置访问控制
- 定期备份数据
- 记录操作日志
