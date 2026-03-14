#!/bin/bash

echo "🚀 启动万智牌规则问答服务..."
echo ""

# 激活虚拟环境
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✓ 虚拟环境已激活"
else
    echo "⚠️  虚拟环境不存在，使用系统 Python"
fi

echo ""

# 检查数据目录
if [ ! -d "data" ]; then
    echo "📁 创建数据目录..."
    mkdir -p data
fi

# 检查数据库是否存在
if [ ! -f "data/magic_rules.db" ]; then
    echo "📊 初始化数据库..."
    python backend/init_data.py
    echo ""
fi

# 启动服务
echo "🎴 启动 API 服务..."
cd backend
python main.py
