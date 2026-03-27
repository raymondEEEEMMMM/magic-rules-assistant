#!/usr/bin/env python3
"""
CloudBase MTGCH API 测试 (pytest 格式)
"""

import json
import urllib.request
import urllib.parse
import urllib.error
import ssl
import pytest


BASE_URL = "https://magic-rules-assistant-0a1904c329-1410769303.ap-shanghai.app.tcloudbase.com"


def make_request(path, params=None):
    """发送 HTTP 请求"""
    url = f"{BASE_URL}{path}"
    if params:
        query_string = urllib.parse.urlencode(params)
        url += f"?{query_string}"

    ssl_context = ssl._create_unverified_context()
    req = urllib.request.Request(url, method='GET')
    req.add_header('User-Agent', 'Mozilla/5.0')

    with urllib.request.urlopen(req, context=ssl_context, timeout=30) as response:
        return json.loads(response.read().decode('utf-8'))


@pytest.mark.cloud
@pytest.mark.api
class TestCloudMTGCHAPI:
    """CloudBase 云端 API 测试"""

    @pytest.mark.skip(reason="需要外部网络连接")
    def test_root_path(self):
        """测试根路径"""
        result = make_request("/")
        assert result is not None

    @pytest.mark.skip(reason="需要外部网络连接")
    def test_chinese_card_search(self):
        """测试中文卡牌搜索"""
        result = make_request("/wechat/api/mtgch/search", {
            "q": "闪电风暴",
            "page_size": 1,
            "priority_chinese": "true"
        })

        assert result is not None
        if "items" in result:
            assert isinstance(result["items"], list)

    @pytest.mark.skip(reason="需要外部网络连接")
    def test_english_card_search(self):
        """测试英文卡牌搜索"""
        result = make_request("/wechat/api/mtgch/search", {
            "q": "Lightning Storm",
            "page_size": 1,
            "priority_chinese": "false"
        })

        assert result is not None

    @pytest.mark.skip(reason="需要外部网络连接")
    def test_random_card(self):
        """测试随机卡牌"""
        result = make_request("/wechat/api/mtgch/random")

        assert result is not None
        # 随机卡牌可能返回任何响应

    @pytest.mark.skip(reason="需要外部网络连接")
    def test_autocomplete(self):
        """测试自动补全"""
        result = make_request("/wechat/api/mtgch/autocomplete", {
            "q": "闪电",
            "size": 5
        })

        assert result is not None
        if "items" in result:
            assert isinstance(result["items"], list)
