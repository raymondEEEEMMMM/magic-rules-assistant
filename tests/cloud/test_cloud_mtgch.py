#!/usr/bin/env python3
"""
CloudBase MTGCH API 测试 v1 (pytest 格式)
"""

import json
import urllib.request
import urllib.parse
import pytest


BASE_URL = "https://magic-rules-assistant-0a1904c329.service.tcloudbaseapp.com/magic-rules-api"


def make_request(path, params=None):
    """发送 HTTP 请求"""
    url = f"{BASE_URL}{path}"
    if params:
        query_string = urllib.parse.urlencode(params)
        url += f"?{query_string}"

    req = urllib.request.Request(url, method='GET')
    req.add_header('User-Agent', 'Mozilla/5.0')

    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode('utf-8'))


@pytest.mark.cloud
@pytest.mark.api
class TestCloudMTGCHAPIV1:
    """CloudBase 云端 API 测试 V1"""

    @pytest.mark.skip(reason="需要外部网络连接")
    def test_chinese_search(self):
        """测试中文搜索"""
        result = make_request("/api/mtgch/search", {"q": "闪电风暴", "page_size": 1})
        assert result is not None

    @pytest.mark.skip(reason="需要外部网络连接")
    def test_english_search(self):
        """测试英文搜索"""
        result = make_request("/api/mtgch/search", {"q": "Lightning Storm", "page_size": 1})
        assert result is not None

    @pytest.mark.skip(reason="需要外部网络连接")
    def test_random(self):
        """测试随机卡牌"""
        result = make_request("/api/mtgch/random")
        assert result is not None

    @pytest.mark.skip(reason="需要外部网络连接")
    def test_autocomplete(self):
        """测试自动补全"""
        result = make_request("/api/mtgch/autocomplete", {"q": "闪电", "size": 5})
        assert result is not None
