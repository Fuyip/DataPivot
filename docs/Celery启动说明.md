# Celery Worker 启动说明

## 问题原因

银行流水上传任务一直停留在"等待中"状态，是因为 **Celery Worker 没有运行**。

- ✅ Redis 正在运行
- ✅ 文件已成功上传到服务器
- ❌ Celery Worker 未启动，无法处理异步任务

## 启动 Celery Worker

### 方法 1：使用启动脚本（推荐）

```bash
cd /Users/yipf/DataPivot项目/DataPivot
./start_celery.sh
```

### 方法 2：手动启动

```bash
cd /Users/yipf/DataPivot项目/DataPivot
celery -A backend.core.celery_app worker --loglevel=info --logfile=celery.log --concurrency=4
```

## 启动后的效果

启动 Celery Worker 后：
1. 等待中的任务会立即开始处理
2. 任务状态会从"等待中"变为"处理中"
3. 处理完成后会变为"已完成"或"失败"

## 完整的服务启动顺序

DataPivot 系统需要启动 3 个服务：

1. **Redis**（消息队列）
   ```bash
   redis-server
   ```
   ✅ 已经在运行

2. **后端 API**（FastAPI）
   ```bash
   ./start_backend.sh
   # 或
   python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
   ```
   ✅ 已经在运行

3. **Celery Worker**（异步任务处理）
   ```bash
   ./start_celery.sh
   # 或
   celery -A backend.core.celery_app worker --loglevel=info
   ```
   ❌ 需要启动

4. **前端**（Vue.js）
   ```bash
   cd frontend && npm run dev
   ```
   ✅ 已经在运行

## 查看 Celery 日志

启动后可以查看日志：

```bash
# 实时查看日志
tail -f celery.log

# 查看最近的日志
tail -100 celery.log
```

## 验证 Celery 是否正常工作

启动 Celery Worker 后，可以通过以下方式验证：

1. **检查进程**
   ```bash
   ps aux | grep celery
   ```
   应该能看到 celery worker 进程

2. **查看任务状态**
   - 刷新浏览器页面
   - 查看任务列表
   - 等待中的任务应该开始处理

3. **查看日志**
   ```bash
   tail -f celery.log
   ```
   应该能看到任务处理的日志

## 常见问题

### Q: Celery 启动失败
A: 检查 Redis 是否运行：
```bash
redis-cli ping
# 应该返回 PONG
```

### Q: 任务处理失败
A: 查看 celery.log 中的错误信息：
```bash
tail -100 celery.log | grep ERROR
```

### Q: 如何停止 Celery
A: 按 `Ctrl+C` 或使用：
```bash
pkill -f "celery.*worker"
```

## 开发环境启动建议

建议使用多个终端窗口分别运行各个服务：

**终端 1 - 后端 API**
```bash
cd /Users/yipf/DataPivot项目/DataPivot
./start_backend.sh
```

**终端 2 - Celery Worker**
```bash
cd /Users/yipf/DataPivot项目/DataPivot
./start_celery.sh
```

**终端 3 - 前端**
```bash
cd /Users/yipf/DataPivot项目/DataPivot/frontend
npm run dev
```

这样可以方便地查看各个服务的日志输出。
