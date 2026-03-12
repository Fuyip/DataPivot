#!/bin/bash

# DataPivot 后端启动脚本
# 支持大文件上传（最大 20GB）

cd "$(dirname "$0")"

echo "启动 DataPivot 后端服务..."
echo "配置："
echo "  - 端口: 8000"
echo "  - 最大文件大小: 20GB"
echo "  - 超时时间: 300秒"
echo ""

# 使用 uvicorn 启动，配置大文件上传支持
python -m uvicorn backend.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --reload \
  --timeout-keep-alive 300 \
  --limit-max-requests 10000 \
  --limit-concurrency 1000
