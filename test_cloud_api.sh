#!/bin/bash
# 云端 API 测试脚本

API_BASE="https://magic-rules-assistant-0a1904c329.tcb.qcloud.la"

echo "=== 云端 API 测试 ==="
echo "API 地址: $API_BASE"
echo ""

# 测试服务状态
echo "1. 测试服务状态"
response=$(curl -s -o /dev/null -w "%{http_code}" "$API_BASE/")
if [ "$response" = "200" ]; then
    echo "   ✓ 服务状态正常 (HTTP 200)"
    curl -s "$API_BASE/" | python3 -m json.tool 2>/dev/null || curl -s "$API_BASE/"
else
    echo "   ✗ 服务异常 (HTTP $response)"
fi
echo ""

# 测试规则搜索
echo "2. 测试规则搜索 (/api/search?q=combat)"
response=$(curl -s -o /dev/null -w "%{http_code}" "$API_BASE/api/search?q=combat")
if [ "$response" = "200" ]; then
    echo "   ✓ 规则搜索正常 (HTTP 200)"
    curl -s "$API_BASE/api/search?q=combat" | python3 -m json.tool 2>/dev/null | head -20
else
    echo "   ✗ 规则搜索异常 (HTTP $response)"
fi
echo ""

# 测试关键词查询
echo "3. 测试关键词查询 (/api/keyword?k=Flying)"
response=$(curl -s -o /dev/null -w "%{http_code}" "$API_BASE/api/keyword?k=Flying")
if [ "$response" = "200" ]; then
    echo "   ✓ 关键词查询正常 (HTTP 200)"
    curl -s "$API_BASE/api/keyword?k=Flying" | python3 -m json.tool 2>/dev/null
else
    echo "   ✗ 关键词查询异常 (HTTP $response)"
fi
echo ""

# 测试卡牌搜索
echo "4. 测试卡牌搜索 (/api/card?q=Lightning)"
response=$(curl -s -o /dev/null -w "%{http_code}" "$API_BASE/api/card?q=Lightning")
if [ "$response" = "200" ]; then
    echo "   ✓ 卡牌搜索正常 (HTTP 200)"
    curl -s "$API_BASE/api/card?q=Lightning" | python3 -m json.tool 2>/dev/null | head -30
else
    echo "   ✗ 卡牌搜索异常 (HTTP $response)"
fi
echo ""

# 测试随机卡牌
echo "5. 测试随机卡牌 (/api/mtgch/random)"
response=$(curl -s -o /dev/null -w "%{http_code}" "$API_BASE/api/mtgch/random")
if [ "$response" = "200" ]; then
    echo "   ✓ 随机卡牌正常 (HTTP 200)"
    curl -s "$API_BASE/api/mtgch/random" | python3 -m json.tool 2>/dev/null | head -20
else
    echo "   ✗ 随机卡牌异常 (HTTP $response)"
fi
echo ""

# 测试自动补全
echo "6. 测试自动补全 (/api/mtgch/autocomplete?q=light&size=5)"
response=$(curl -s -o /dev/null -w "%{http_code}" "$API_BASE/api/mtgch/autocomplete?q=light&size=5")
if [ "$response" = "200" ]; then
    echo "   ✓ 自动补全正常 (HTTP 200)"
    curl -s "$API_BASE/api/mtgch/autocomplete?q=light&size=5" | python3 -m json.tool 2>/dev/null
else
    echo "   ✗ 自动补全异常 (HTTP $response)"
fi
echo ""

echo "=== 测试完成 ==="
