#!/bin/bash

echo "🔄 正在重启 DataPivot 服务..."

# 切换到项目根目录
cd /Users/yipf/DataPivot项目/DataPivot

# 创建日志目录
mkdir -p logs

echo "🚀 重启后端服务..."
./scripts/backend_service.sh restart

echo "🚀 重启前端服务..."
./scripts/frontend_service.sh restart

echo ""
echo "✅ 重启完成!"
echo ""
echo "服务地址:"
echo "  前端: http://localhost:5173"
echo "  后端 API: http://localhost:8000"
echo "  API 文档: http://localhost:8000/docs"
echo ""
echo "查看日志:"
echo "  后端: tail -f logs/backend.log"
echo "  前端: tail -f logs/frontend.log"
