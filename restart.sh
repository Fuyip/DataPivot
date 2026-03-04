#!/bin/bash

echo "🔄 正在重启 DataPivot 服务..."

# 切换到项目根目录
cd /Users/yipf/DataPivot项目/DataPivot

# 创建日志目录
mkdir -p logs

# 停止后端服务
echo "⏹️  停止后端服务..."
pkill -f "uvicorn backend.main"
if [ $? -eq 0 ]; then
    echo "   后端服务已停止"
else
    echo "   未找到运行中的后端服务"
fi

# 停止前端服务
echo "⏹️  停止前端服务..."
pkill -f "vite"
pkill -f "npm run dev"
if [ $? -eq 0 ]; then
    echo "   前端服务已停止"
else
    echo "   未找到运行中的前端服务"
fi

# 等待进程完全停止
sleep 2

# 启动后端服务
echo "🚀 启动后端服务..."
source venv/bin/activate
nohup uvicorn backend.main:app --host 0.0.0.0 --port 8000 > logs/backend.log 2>&1 &
BACKEND_PID=$!
echo "   后端服务已启动 (PID: $BACKEND_PID)"

# 启动前端服务
echo "🚀 启动前端服务..."
cd frontend
nohup npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "   前端服务已启动 (PID: $FRONTEND_PID)"
cd ..

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 3

# 检查服务状态
echo ""
echo "📊 服务状态:"
if ps -p $BACKEND_PID > /dev/null; then
    echo "   ✅ 后端服务运行中 (PID: $BACKEND_PID)"
else
    echo "   ❌ 后端服务启动失败"
fi

if ps -p $FRONTEND_PID > /dev/null; then
    echo "   ✅ 前端服务运行中 (PID: $FRONTEND_PID)"
else
    echo "   ❌ 前端服务启动失败"
fi

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
