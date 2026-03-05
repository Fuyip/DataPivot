#!/bin/bash
# 停止所有服务脚本

echo "正在停止所有服务..."

# 停止 Redis
echo "停止 Redis..."
brew services stop redis 2>/dev/null || echo "Redis 未通过 Homebrew 管理"

# 停止 Celery Worker (查找并终止进程)
echo "停止 Celery Worker..."
pkill -f "celery.*worker" 2>/dev/null || echo "Celery Worker 未运行"

# 停止 FastAPI (查找并终止进程)
echo "停止 FastAPI..."
pkill -f "uvicorn.*backend.main:app" 2>/dev/null || echo "FastAPI 未运行"

echo "✓ 所有服务已停止"
