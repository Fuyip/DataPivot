#!/bin/bash
# 重启服务脚本

set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_DIR"

echo "停止现有服务..."
./scripts/backend_service.sh stop || true
pkill -f "celery -A backend.core.celery_app worker" 2>/dev/null || true

echo "启动后端服务..."
./scripts/backend_service.sh start

echo "启动 Celery worker..."
source venv/bin/activate
nohup celery -A backend.core.celery_app worker --loglevel=info > logs/celery.log 2>&1 &

echo "服务已重启"
echo "后端日志: logs/backend.log"
echo "Celery日志: logs/celery.log"
