#!/bin/bash
# Celery Worker 启动脚本

# 切换到项目根目录
cd "$(dirname "$0")/.."

# 激活虚拟环境
source venv/bin/activate

# 启动 Celery Worker
echo "正在启动 Celery Worker..."
echo "项目目录: $(pwd)"
echo "Python版本: $(python --version)"
echo "================================"

celery -A backend.core.celery_app worker --loglevel=info
