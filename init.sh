#!/bin/bash

# 数枢 (DataPivot) 项目初始化脚本

echo "================================"
echo "数枢 (DataPivot) 项目初始化"
echo "================================"
echo ""

# 检查Python版本
echo "检查Python版本..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "当前Python版本: $python_version"

if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到Python3，请先安装Python 3.9+"
    exit 1
fi

# 检查MySQL
echo ""
echo "检查MySQL..."
if ! command -v mysql &> /dev/null; then
    echo "⚠️  警告: 未找到MySQL，请确保已安装MySQL 8.0+"
else
    mysql_version=$(mysql --version 2>&1)
    echo "MySQL版本: $mysql_version"
fi

# 创建虚拟环境
echo ""
echo "创建Python虚拟环境..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ 虚拟环境创建成功"
else
    echo "虚拟环境已存在，跳过创建"
fi

# 激活虚拟环境
echo ""
echo "激活虚拟环境..."
source venv/bin/activate

# 升级pip
echo ""
echo "升级pip..."
pip install --upgrade pip

# 安装依赖
echo ""
echo "安装Python依赖包..."
pip install -r requirements.txt

# 创建必要的目录
echo ""
echo "创建项目目录..."
mkdir -p logs
mkdir -p uploads
mkdir -p data
mkdir -p bank_statements/raw
mkdir -p bank_statements/processing
mkdir -p bank_statements/processed
mkdir -p bank_statements/error_files
mkdir -p bank_statements/logs

# 创建.gitkeep文件
touch bank_statements/raw/.gitkeep
touch bank_statements/processing/.gitkeep
touch bank_statements/processed/.gitkeep
touch bank_statements/error_files/.gitkeep
touch data/.gitkeep
touch logs/.gitkeep
touch uploads/.gitkeep

echo "✅ 目录创建完成"

# 配置环境变量
echo ""
if [ ! -f ".env" ]; then
    echo "创建环境变量文件..."
    cp .env.example .env
    echo "✅ 已创建.env文件，请编辑配置数据库连接信息"
    echo ""
    echo "请执行: vim .env"
else
    echo ".env文件已存在"
fi

# 测试数据库连接
echo ""
echo "测试数据库连接..."
python3 -c "
try:
    from database import engine
    with engine.connect() as conn:
        print('✅ 数据库连接成功')
except Exception as e:
    print(f'❌ 数据库连接失败: {e}')
    print('请检查.env文件中的数据库配置')
"

echo ""
echo "================================"
echo "初始化完成！"
echo "================================"
echo ""
echo "下一步操作："
echo "1. 编辑.env文件配置数据库连接: vim .env"
echo "2. 激活虚拟环境: source venv/bin/activate"
echo "3. 测试现有功能: python 导入云搜人员基本信息.py"
echo "4. 查看文档: cat docs/README.md"
echo ""
echo "开发环境启动（未来）："
echo "- 后端: uvicorn backend.main:app --reload"
echo "- 前端: cd frontend && npm run dev"
echo ""
