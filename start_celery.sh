#!/bin/bash

# DataPivot Celery Worker 启动脚本

cd "$(dirname "$0")"

echo "启动 Celery Worker..."
echo "配置："
echo "  - Redis: localhost:6379"
echo "  - 任务超时: 4小时"
echo "  - 日志级别: info"
echo ""

# 启动 Celery worker
celery -A backend.core.celery_app worker \
  --loglevel=info \
  --logfile=celery.log \
  --concurrency=4 \
  --max-tasks-per-child=50
