#!/bin/bash
# 重启服务脚本

echo "停止现有服务..."
pkill -f "uvicorn backend.main:app"
pkill -f "celery -A backend.core.celery_app worker"

echo "启动后端服务..."
source venv/bin/activate
nohup uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload > logs/backend.log 2>&1 &

echo "启动 Celery worker..."
nohup celery -A backend.core.celery_app worker --loglevel=info > logs/celery.log 2>&1 &

echo "服务已重启"
echo "后端日志: logs/backend.log"
echo "Celery日志: logs/celery.log"
