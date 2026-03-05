#!/bin/bash
# 系统状态检查脚本

echo "================================"
echo "DataPivot 系统状态检查"
echo "================================"
echo ""

# 检查 Redis
echo "1. Redis 状态:"
if redis-cli ping > /dev/null 2>&1; then
    echo "   ✓ Redis 正在运行"
else
    echo "   ✗ Redis 未运行"
fi
echo ""

# 检查 FastAPI
echo "2. FastAPI 状态:"
if curl -s http://localhost:8000/docs > /dev/null 2>&1; then
    echo "   ✓ FastAPI 正在运行 (http://localhost:8000)"
else
    echo "   ✗ FastAPI 未运行"
fi
echo ""

# 检查 Celery
echo "3. Celery Worker 状态:"
if pgrep -f "celery.*worker" > /dev/null 2>&1; then
    echo "   ✓ Celery Worker 正在运行"
else
    echo "   ✗ Celery Worker 未运行"
fi
echo ""

# 检查银行流水接口
echo "4. 银行流水接口:"
if curl -s http://localhost:8000/openapi.json | grep -q "bank-statements"; then
    echo "   ✓ 银行流水接口已注册"
    echo "   - POST /api/v1/cases/{case_id}/bank-statements/upload"
    echo "   - GET  /api/v1/cases/{case_id}/bank-statements/tasks/{task_id}"
    echo "   - GET  /api/v1/cases/{case_id}/bank-statements/tasks"
    echo "   - POST /api/v1/cases/{case_id}/bank-statements/tasks/{task_id}/cancel"
    echo "   - GET  /api/v1/cases/{case_id}/bank-statements/statistics"
else
    echo "   ✗ 银行流水接口未找到"
fi
echo ""

echo "================================"
echo "检查完成"
echo "================================"
