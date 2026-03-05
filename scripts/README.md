# 启动脚本使用指南

## 📁 脚本列表

已创建5个启动脚本，位于 `scripts/` 目录：

| 脚本 | 功能 | 说明 |
|------|------|------|
| `start_all.sh` | 一键启动所有服务 | 使用tmux多窗口管理（推荐） |
| `start_redis.sh` | 启动Redis | 单独启动Redis服务 |
| `start_celery.sh` | 启动Celery Worker | 单独启动Celery |
| `start_api.sh` | 启动FastAPI | 单独启动API服务 |
| `stop_all.sh` | 停止所有服务 | 一键停止所有服务 |

## 🚀 快速启动（推荐）

### 方式1：一键启动（使用tmux）

```bash
cd /Users/yipf/DataPivot项目/DataPivot
./scripts/start_all.sh
```

这会在tmux中启动3个窗口：
- 窗口0: Redis
- 窗口1: Celery Worker
- 窗口2: FastAPI

**tmux常用命令：**
- `Ctrl+B` 然后按 `0/1/2` - 切换窗口
- `Ctrl+B` 然后按 `D` - 断开会话（服务继续运行）
- `tmux attach -t datapivot` - 重新连接会话
- `./scripts/stop_all.sh` - 停止所有服务

### 方式2：分别启动（使用多个终端）

**终端1 - 启动Redis：**
```bash
cd /Users/yipf/DataPivot项目/DataPivot
./scripts/start_redis.sh
```

**终端2 - 启动Celery Worker：**
```bash
cd /Users/yipf/DataPivot项目/DataPivot
./scripts/start_celery.sh
```

**终端3 - 启动FastAPI：**
```bash
cd /Users/yipf/DataPivot项目/DataPivot
./scripts/start_api.sh
```

## 🛑 停止服务

```bash
cd /Users/yipf/DataPivot项目/DataPivot
./scripts/stop_all.sh
```

## 📋 首次启动前的准备

### 1. 安装tmux（如果使用一键启动）
```bash
brew install tmux
```

### 2. 安装Redis
```bash
brew install redis
```

### 3. 执行数据库迁移
```bash
mysql -u root -p datapivot < backend/migrations/add_bank_statement_tasks.sql
```

## ✅ 验证服务状态

### 检查Redis
```bash
redis-cli ping
# 应返回: PONG
```

### 检查Celery
查看Celery终端输出，应该看到：
```
[tasks]
  . backend.tasks.bank_statement_tasks.process_bank_statements
```

### 检查FastAPI
访问：http://localhost:8000/docs

应该能看到Swagger API文档，包括银行流水相关的6个端点。

## 🔍 查看日志

### tmux方式
```bash
# 连接到会话
tmux attach -t datapivot

# 切换到不同窗口查看日志
Ctrl+B 然后按 0  # Redis日志
Ctrl+B 然后按 1  # Celery日志
Ctrl+B 然后按 2  # FastAPI日志
```

### 分别启动方式
直接查看对应终端的输出

## 🐛 故障排查

### Redis启动失败
```bash
# 检查Redis是否已安装
which redis-server

# 手动启动Redis
redis-server

# 检查端口是否被占用
lsof -i :6379
```

### Celery无法连接Redis
```bash
# 检查Redis是否运行
redis-cli ping

# 检查config.py中的Redis配置
cat config.py | grep REDIS
```

### FastAPI启动失败
```bash
# 检查端口是否被占用
lsof -i :8000

# 手动启动查看详细错误
cd backend
source ../venv/bin/activate
python main.py
```

## 📝 脚本说明

### start_all.sh
- 使用tmux创建多窗口会话
- 自动按顺序启动所有服务
- 服务在后台持续运行
- 可以断开连接后重新连接

### start_redis.sh
- 检查Redis是否已安装
- 检查Redis是否已运行
- 使用brew services启动Redis

### start_celery.sh
- 激活虚拟环境
- 启动Celery Worker
- 显示项目信息和Python版本

### start_api.sh
- 激活虚拟环境
- 使用uvicorn启动FastAPI
- 启用热重载（代码修改自动重启）
- 显示API文档地址

### stop_all.sh
- 停止Redis服务
- 终止Celery Worker进程
- 终止FastAPI进程

## 🎯 推荐工作流

1. **首次启动**
   ```bash
   ./scripts/start_all.sh
   ```

2. **开发过程中**
   - 保持tmux会话运行
   - 需要查看日志时连接到会话
   - 代码修改后FastAPI会自动重载

3. **结束工作**
   ```bash
   ./scripts/stop_all.sh
   ```

4. **下次继续**
   ```bash
   ./scripts/start_all.sh
   ```

## 🌟 提示

- 使用 `start_all.sh` 最方便，所有服务在一个tmux会话中管理
- FastAPI支持热重载，修改代码后自动重启
- Celery Worker需要手动重启才能加载代码更改
- 可以在tmux中使用 `Ctrl+C` 停止单个服务，然后重新启动
