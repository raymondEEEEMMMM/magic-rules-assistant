#!/usr/bin/env python3
"""
路径调试测试 (pytest 格式)
"""

import urllib.request
import ssl
import pytest


BASE_URL = "https://magic-rules-assistant-0a1904c329-1410769303.ap-shanghai.app.tcloudbase.com"


def make_request(path):
    """发送 HTTP 请求"""
    url = f"{BASE_URL}{path}"
    req = urllib.request.Request(url, method='GET')
    req.add_header('User-Agent', 'Mozilla/5.0')

    with urllib.request.urlopen(req, context=ssl._create_unverified_context(), timeout=10) as response:
        return response.status, response.read().decode('utf-8')


@pytest.mark.cloud
@pytest.mark.api
class TestPathDebug:
    """路径调试测试"""

    @pytest.mark.skip(reason="需要外部网络连接")
    def test_root_path(self):
        """测试根路径"""
        status, text = make_request("/")
        assert status == 200

    @pytest.mark.skip(reason="需要外部网络连接")
    def test_wechat_path(self):
        """测试微信路径"""
        status, _ = make_request("/wechat")
        assert status in [200, 400, 401, 403]  # 微信验证可能返回这些状态

    @pytest.mark.skip(reason="需要外部网络连接")
    def test_api_search(self):
        """测试搜索 API"""
        status, _ = make_request("/wechat/api/search")
        assert status in [200, 400, 404]

    @pytest.mark.skip(reason="需要外部网络连接")
    def test_mtgch_search(self):
        """测试 MTGCH 搜索"""
        status, _ = make_request("/wechat/api/mtgch/search")
        assert status in [200, 400, 404]
