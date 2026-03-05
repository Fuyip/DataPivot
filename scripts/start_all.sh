#!/bin/bash
# 一键启动所有服务（使用 tmux 多窗口）

# 检查 tmux 是否安装
if ! command -v tmux &> /dev/null; then
    echo "❌ tmux 未安装"
    echo "请运行以下命令安装: brew install tmux"
    exit 1
fi

# 项目根目录
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SESSION_NAME="datapivot"

echo "正在启动 DataPivot 服务..."
echo "项目目录: $PROJECT_DIR"

# 检查会话是否已存在
if tmux has-session -t $SESSION_NAME 2>/dev/null; then
    echo "会话 $SESSION_NAME 已存在，正在关闭..."
    tmux kill-session -t $SESSION_NAME
fi

# 创建新的 tmux 会话
tmux new-session -d -s $SESSION_NAME -n "Redis"

# 窗口1: Redis
tmux send-keys -t $SESSION_NAME:0 "cd $PROJECT_DIR" C-m
tmux send-keys -t $SESSION_NAME:0 "./scripts/start_redis.sh" C-m

# 窗口2: Celery Worker
tmux new-window -t $SESSION_NAME -n "Celery"
tmux send-keys -t $SESSION_NAME:1 "cd $PROJECT_DIR" C-m
tmux send-keys -t $SESSION_NAME:1 "sleep 3" C-m
tmux send-keys -t $SESSION_NAME:1 "./scripts/start_celery.sh" C-m

# 窗口3: FastAPI
tmux new-window -t $SESSION_NAME -n "FastAPI"
tmux send-keys -t $SESSION_NAME:2 "cd $PROJECT_DIR" C-m
tmux send-keys -t $SESSION_NAME:2 "sleep 5" C-m
tmux send-keys -t $SESSION_NAME:2 "./scripts/start_api.sh" C-m

# 选择第一个窗口
tmux select-window -t $SESSION_NAME:0

echo ""
echo "✓ 所有服务已在 tmux 会话中启动"
echo ""
echo "使用以下命令："
echo "  tmux attach -t $SESSION_NAME    # 连接到会话"
echo "  Ctrl+B 然后按 0/1/2             # 切换窗口"
echo "  Ctrl+B 然后按 D                 # 断开会话（服务继续运行）"
echo "  ./scripts/stop_all.sh           # 停止所有服务"
echo ""
echo "窗口说明："
echo "  0: Redis"
echo "  1: Celery Worker"
echo "  2: FastAPI (http://localhost:8000/docs)"
echo ""

# 自动连接到会话
tmux attach -t $SESSION_NAME
