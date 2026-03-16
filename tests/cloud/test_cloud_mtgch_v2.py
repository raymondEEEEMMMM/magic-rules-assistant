#!/usr/bin/env python3
"""
CloudBase MTGCH API 测试 v2 (pytest 格式)
"""

import json
import urllib.request
import urllib.parse
import pytest


BASE_URL = "https://magic-rules-assistant-0a1904c329.ap-shanghai.tcloudbaseapp.com/wechat"


def make_request(path, params=None):
    """发送 HTTP 请求"""
    url = f"{BASE_URL}{path}"
    if params:
        query_string = urllib.parse.urlencode(params)
        url += f"?{query_string}"

    import ssl
    ssl_context = ssl._create_unverified_context()

    req = urllib.request.Request(url, method='GET')
    req.add_header('User-Agent', 'Mozilla/5.0')

    with urllib.request.urlopen(req, context=ssl_context, timeout=30) as response:
        return json.loads(response.read().decode('utf-8'))


@pytest.mark.cloud
@pytest.mark.api
class TestCloudMTGCHAPIV2:
    """CloudBase 云端 API 测试 V2 (微信路径)"""

    @pytest.mark.skip(reason="需要外部网络连接")
    def test_chinese_search(self):
        """测试中文搜索"""
        result = make_request("/api/mtgch/search", {"q": "闪电风暴", "page_size": 1})
        assert result is not None

    @pytest.mark.skip(reason="需要外部网络连接")
    def test_random(self):
        """测试随机卡牌"""
        result = make_request("/api/mtgch/random")
        assert result is not None
