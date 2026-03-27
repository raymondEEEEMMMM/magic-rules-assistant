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
echo ""
echo "【请用微信扫码登录】"
echo ""

# 捕获登录URL和用户码
LOGIN_OUTPUT=$(tcb login 2>&1)
echo "$LOGIN_OUTPUT"

# 提取用户码
USER_CODE=$(echo "$LOGIN_OUTPUT" | grep -oP 'user_code=\K[A-Z0-9-]+' | head -1)
if [ -n "$USER_CODE" ]; then
    echo ""
    echo "【用户码】: $USER_CODE"
    echo "【登录URL】: https://tcb.cloud.tencent.com/dev#/cli-auth?user_code=$USER_CODE&from=cli&flow=device"
fi

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
