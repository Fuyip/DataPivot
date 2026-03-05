#!/bin/bash
# Redis 启动脚本

echo "正在启动 Redis 服务..."

# 检查 Redis 是否已安装
if ! command -v redis-server &> /dev/null; then
    echo "❌ Redis 未安装"
    echo "请运行以下命令安装: brew install redis"
    exit 1
fi

# 检查 Redis 是否已经在运行
if redis-cli ping &> /dev/null; then
    echo "✓ Redis 已经在运行"
    redis-cli ping
    exit 0
fi

# 启动 Redis
echo "启动 Redis 服务..."
brew services start redis

# 等待 Redis 启动
sleep 2

# 验证 Redis 是否启动成功
if redis-cli ping &> /dev/null; then
    echo "✓ Redis 启动成功"
    redis-cli ping
else
    echo "❌ Redis 启动失败"
    exit 1
fi
