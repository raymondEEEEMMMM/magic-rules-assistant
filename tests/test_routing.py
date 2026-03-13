#!/usr/bin/env python3
"""
测试路由逻辑
"""
# 模拟 CloudBase 的路径处理
test_cases = [
    "/api/keyword?k=飞行",
    "/keyword?k=飞行",
    "/api/search?q=践踏",
    "/search?q=践踏",
]

for full_path in test_cases:
    path = full_path.split('?')[0]
    
    # 关键词查询 API
    if path in ('/api/keyword', '/keyword'):
        print(f"✓ Matched keyword API: {path}")
    # 规则搜索 API
    elif path in ('/api/search', '/search'):
        print(f"✓ Matched search API: {path}")
    else:
        print(f"✗ No match: {path}")
