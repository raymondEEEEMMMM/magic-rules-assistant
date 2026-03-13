#!/usr/bin/env python3
"""测试不同路径"""

import json
import urllib.request
import ssl

def test_path(path):
    """测试单个路径"""
    base_url = "https://magic-rules-assistant-0a1904c329-1410769303.ap-shanghai.app.tcloudbase.com"
    url = f"{base_url}{path}"

    print(f"测试路径: {path}")

    try:
        req = urllib.request.Request(url, method='GET')
        req.add_header('User-Agent', 'Mozilla/5.0')

        with urllib.request.urlopen(req, context=ssl._create_unverified_context(), timeout=10) as response:
            response_text = response.read().decode('utf-8')
            print(f"  状态码: {response.status}")
            print(f"  响应: {response_text[:200]}")
    except Exception as e:
        print(f"  错误: {e}")

if __name__ == "__main__":
    paths = [
        "/",
        "/wechat",
        "/wechat/",
        "/wechat/api/search",
        "/wechat/api/mtgch/search",
        "/api/search",
        "/api/mtgch/search",
    ]

    for path in paths:
        test_path(path)
        print()
