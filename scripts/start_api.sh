#!/bin/bash
# FastAPI 应用启动脚本

# 切换到项目根目录
cd "$(dirname "$0")/.."

# 激活虚拟环境
source venv/bin/activate

# 启动 FastAPI 应用
echo "正在启动 FastAPI 应用..."
echo "项目目录: $(pwd)"
echo "Python版本: $(python --version)"
echo "================================"
echo "API文档地址: http://localhost:8000/docs"
echo "================================"

# 使用 uvicorn 启动
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
