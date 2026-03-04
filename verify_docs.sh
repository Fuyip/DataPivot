#!/bin/bash

# 数枢 (DataPivot) 项目文档验证脚本

echo "================================"
echo "数枢 (DataPivot) 文档验证"
echo "================================"
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查计数
total=0
passed=0
failed=0

check_file() {
    total=$((total + 1))
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $1"
        passed=$((passed + 1))
    else
        echo -e "${RED}✗${NC} $1 (缺失)"
        failed=$((failed + 1))
    fi
}

echo "检查核心文档..."
check_file "README.md"
check_file "PROJECT_SUMMARY.md"
check_file "DOCUMENTATION_REPORT.md"
check_file "DOCS_INDEX.md"
check_file "TODO.md"

echo ""
echo "检查docs/目录文档..."
check_file "docs/README.md"
check_file "docs/技术选型文档.md"
check_file "docs/API接口设计文档.md"
check_file "docs/开发指南.md"
check_file "docs/部署文档.md"
check_file "docs/功能清单.md"

echo ""
echo "检查配置文件..."
check_file "requirements.txt"
check_file ".gitignore"
check_file ".env.example"
check_file "docker-compose.yml"
check_file "docker/backend/Dockerfile"
check_file "docker/frontend/Dockerfile"
check_file "docker/nginx/nginx.conf"
check_file "docker/mysql/conf.d/custom.cnf"

echo ""
echo "检查脚本文件..."
check_file "init.sh"

echo ""
echo "检查现有代码文件..."
check_file "config.py"
check_file "database.py"
check_file "bank_config.py"

echo ""
echo "================================"
echo "验证结果"
echo "================================"
echo -e "总计: $total 个文件"
echo -e "${GREEN}通过: $passed${NC}"
echo -e "${RED}失败: $failed${NC}"
echo ""

if [ $failed -eq 0 ]; then
    echo -e "${GREEN}✓ 所有文档验证通过！${NC}"
    echo ""
    echo "下一步操作："
    echo "1. 运行初始化脚本: bash init.sh"
    echo "2. 配置环境变量: vim .env"
    echo "3. 查看文档索引: cat DOCS_INDEX.md"
    echo "4. 查看待办事项: cat TODO.md"
    exit 0
else
    echo -e "${RED}✗ 有 $failed 个文件缺失，请检查！${NC}"
    exit 1
fi
