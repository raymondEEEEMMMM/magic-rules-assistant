#!/bin/bash
# CloudBase 云函数部署脚本

echo "=== mtgAsk - 部署脚本 ==="
echo ""

# 检查是否安装了 cloudbase CLI
if ! command -v tcb &> /dev/null; then
    echo "正在安装 CloudBase CLI..."
    npm install -g @cloudbase/cli
fi

# 登录 CloudBase
echo "步骤 1: 登录 CloudBase"
tcb login

# 部署云函数
echo ""
echo "步骤 2: 部署云函数"
cd functions/mtgAsk
tcb fn deploy mtgAsk

# 部署静态网站（如果需要）
echo ""
echo "步骤 3: 部署静态网站（可选）"
echo "如果需要部署小程序静态资源，请运行:"
echo "  tcb hosting deploy miniprogram -e magic-rules-assistant-0a1904c329"

echo ""
echo "=== 部署完成 ==="
echo ""
echo "API 访问地址:"
echo "  https://magic-rules-assistant-0a1904c329.tcb.qcloud.la/"
echo ""
echo "测试命令:"
echo "  curl 'https://magic-rules-assistant-0a1904c329.tcb.qcloud.la/api/search?q=combat'"
