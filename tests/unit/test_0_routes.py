#!/usr/bin/env python3
"""
Routes 单元测试 (pytest 格式)

使用 FastAPI TestClient 和 mock 模拟数据库/服务，测试 API 路由。
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'functions', 'mtgAsk', 'backend'))

import pytest
from unittest.mock import Mock, patch, MagicMock

# 处理 XMLResponse 兼容性问题 (fastapi 0.104.1 没有 XMLResponse)
# 创建一个兼容的 XMLResponse
from fastapi.responses import Response
class XMLResponse(Response):
    def __init__(self, content="", *args, **kwargs):
        super().__init__(content=content, media_type="application/xml", *args, **kwargs)

# 在导入 routes 前 mock fastapi.responses
import fastapi.responses
fastapi.responses.XMLResponse = XMLResponse


# ==================== Fixtures ====================

@pytest.fixture
def mock_db():
    """创建 mock 数据库"""
    with patch('routes.RuleDatabase') as mock:
        db_instance = Mock()
        mock.return_value = db_instance
        yield db_instance


@pytest.fixture
def mock_rule_service():
    """创建 mock RuleService"""
    with patch('routes.rule_service') as mock:
        yield mock


@pytest.fixture
def mock_message_handler():
    """创建 mock MessageHandler"""
    with patch('routes.MessageHandler') as mock:
        handler_instance = Mock()
        mock.return_value = handler_instance
        yield handler_instance


@pytest.fixture
def client(mock_db, mock_rule_service, mock_message_handler):
    """创建 FastAPI 测试客户端"""
    # 必须在导入 routes 之前 mock
    from fastapi.testclient import TestClient
    from routes import app

    with TestClient(app) as test_client:
        yield test_client


# ==================== Routes 测试 ====================

class TestRootRoute:
    """根路由测试"""

    def test_root_returns_status(self, client):
        """测试根路径返回状态"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["status"] == "ok"


class TestSearchRulesAPI:
    """搜索规则 API 测试"""

    def test_search_rules_success(self, client, mock_rule_service):
        """测试搜索成功"""
        mock_rule_service.search_rules.return_value = {
            "rules": [{"rule_number": "100.1", "content": "Test rule"}],
            "keyword_abilities": [],
            "cards": []
        }

        response = client.get("/api/search", params={"q": "test"})

        assert response.status_code == 200
        data = response.json()
        assert data["query"] == "test"
        assert "results" in data
        mock_rule_service.search_rules.assert_called_once_with("test")

    def test_search_rules_empty_query(self, client, mock_rule_service):
        """测试空查询"""
        mock_rule_service.search_rules.return_value = {
            "rules": [],
            "keyword_abilities": [],
            "cards": []
        }

        response = client.get("/api/search", params={"q": ""})

        assert response.status_code == 200


class TestKeywordAPI:
    """关键词异能 API 测试"""

    def test_get_keyword_found(self, client, mock_rule_service):
        """测试获取存在的关键词"""
        mock_rule_service.get_keyword_ability.return_value = {
            "keyword_name": "飞行",
            "description": "描述"
        }

        response = client.get("/api/keyword", params={"keyword": "飞行"})

        assert response.status_code == 200
        data = response.json()
        assert data["keyword"] == "飞行"
        assert data["result"] is not None

    def test_get_keyword_not_found(self, client, mock_rule_service):
        """测试获取不存在的关键词"""
        mock_rule_service.get_keyword_ability.return_value = None

        response = client.get("/api/keyword", params={"keyword": "不存在"})

        assert response.status_code == 200
        data = response.json()
        assert data["result"] is None


class TestCardAPI:
    """卡牌规则 API 测试"""

    def test_get_card_rule_found(self, client, mock_rule_service):
        """测试获取存在的卡牌规则"""
        mock_rule_service.get_card_rule.return_value = {
            "name": "黑莲花",
            "rule": "效果描述"
        }

        response = client.get("/api/card", params={"card_name": "黑莲花"})

        assert response.status_code == 200
        data = response.json()
        assert data["card_name"] == "黑莲花"
        assert data["result"] is not None

    def test_get_card_rule_not_found(self, client, mock_rule_service):
        """测试获取不存在的卡牌规则"""
        mock_rule_service.get_card_rule.return_value = None

        response = client.get("/api/card", params={"card_name": "不存在的卡牌"})

        assert response.status_code == 200
        data = response.json()
        assert data["result"] is None


class TestWechatVerifyAPI:
    """微信验证 API 测试"""

    def test_wechat_verify_success(self, client):
        """测试微信签名验证成功"""
        import hashlib
        from routes import Config

        timestamp = "1234567890"
        nonce = "random_nonce"
        token = Config.WECHAT_TOKEN

        # 计算正确签名
        params = [token, timestamp, nonce]
        params.sort()
        params_str = "".join(params)
        sha1 = hashlib.sha1()
        sha1.update(params_str.encode("utf-8"))
        correct_signature = sha1.hexdigest()

        response = client.get("/wechat", params={
            "signature": correct_signature,
            "timestamp": timestamp,
            "nonce": nonce,
            "echostr": "test_echostr"
        })

        assert response.status_code == 200
        assert response.text == "test_echostr"

    def test_wechat_verify_failure(self, client):
        """测试微信签名验证失败"""
        response = client.get("/wechat", params={
            "signature": "wrong_signature",
            "timestamp": "1234567890",
            "nonce": "random_nonce",
            "echostr": "test_echostr"
        })

        assert response.status_code == 403


class TestMTGCHSearchAPI:
    """MTGCH 搜索 API 测试"""

    def test_mtgch_search_success(self, client):
        """测试 MTGCH 卡牌搜索成功"""
        with patch('services.mtgch_api.MTGCHAPIClient') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            mock_client.search_cards.return_value = {
                "items": [{"name": "Lightning Storm"}],
                "total": 1
            }

            response = client.get("/wechat/api/mtgch/search", params={
                "q": "Lightning Storm",
                "page": 1,
                "page_size": 5
            })

            assert response.status_code == 200
            data = response.json()
            assert "items" in data

    def test_mtgch_search_error(self, client):
        """测试 MTGCH 搜索错误"""
        with patch('services.mtgch_api.MTGCHAPIClient') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            mock_client.search_cards.side_effect = Exception("API Error")

            response = client.get("/wechat/api/mtgch/search", params={
                "q": "test"
            })

            assert response.status_code == 200
            data = response.json()
            assert "error" in data


class TestMTGCHRandomAPI:
    """MTGCH 随机卡牌 API 测试"""

    def test_mtgch_random_success(self, client):
        """测试获取随机卡牌成功"""
        with patch('services.mtgch_api.MTGCHAPIClient') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            mock_client.get_random_card.return_value = {"name": "Random Card"}

            response = client.get("/wechat/api/mtgch/random")

            assert response.status_code == 200

    def test_mtgch_random_no_card(self, client):
        """测试无卡牌时返回错误"""
        with patch('services.mtgch_api.MTGCHAPIClient') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            mock_client.get_random_card.return_value = None

            response = client.get("/wechat/api/mtgch/random")

            assert response.status_code == 200
            data = response.json()
            assert "error" in data


class TestMTGCHAutocompleteAPI:
    """MTGCH 自动补全 API 测试"""

    def test_autocomplete_success(self, client):
        """测试自动补全成功"""
        with patch('services.mtgch_api.MTGCHAPIClient') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            mock_client.autocomplete.return_value = {
                "items": ["闪电击", "闪电风暴"]
            }

            response = client.get("/wechat/api/mtgch/autocomplete", params={
                "q": "闪电",
                "size": 10
            })

            assert response.status_code == 200
            data = response.json()
            assert "items" in data


class TestMTGCHCardDetailAPI:
    """MTGCH 卡牌详情 API 测试"""

    def test_get_card_by_id(self, client):
        """测试通过 ID 获取卡牌"""
        with patch('services.mtgch_api.MTGCHAPIClient') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            mock_client.get_card_by_id.return_value = {
                "id": "card123",
                "name": "Test Card"
            }

            response = client.get("/wechat/api/mtgch/card", params={
                "id": "card123"
            })

            assert response.status_code == 200

    def test_get_card_by_set_and_number(self, client):
        """测试通过系列和编号获取卡牌"""
        with patch('services.mtgch_api.MTGCHAPIClient') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            mock_client.get_card_by_set_and_number.return_value = {
                "name": "Test Card"
            }

            response = client.get("/wechat/api/mtgch/card", params={
                "set": "MKM",
                "number": "1"
            })

            assert response.status_code == 200

    def test_get_card_missing_params(self, client):
        """测试缺少参数时返回错误"""
        response = client.get("/wechat/api/mtgch/card")

        assert response.status_code == 200
        data = response.json()
        assert "error" in data


class TestAIJudgeChatAPI:
    """AI 裁判对话 API 测试"""

    def test_chat_success(self, client):
        """测试 AI 裁判对话成功"""
        with patch('services.ai_judge_service') as mock_service:
            mock_service.chat.return_value = {
                "success": True,
                "reply": "这是一个回答"
            }

            response = client.post("/api/ai-judge/chat", json={
                "message": "测试问题",
                "session_id": "test_session"
            })

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True

    def test_chat_empty_message(self, client):
        """测试空消息"""
        response = client.post("/api/ai-judge/chat", json={
            "message": ""
        })

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "消息不能为空" in data["reply"]

    def test_chat_with_clear_history(self, client):
        """测试清除历史 - 验证带 clear_history 参数能返回成功响应"""
        # 注意: 由于 ai_judge_service 在路由内局部导入, mock 无法应用到运行时导入
        # 此测试验证 API 能正确处理 clear_history 参数并返回成功响应
        response = client.post("/api/ai-judge/chat", json={
            "message": "测试",
            "clear_history": True
        })

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "reply" in data


class TestAIJudgeInitAPI:
    """AI 裁判初始化 API 测试"""

    @pytest.mark.skip(reason="Integration test fails when run with test_agent_pool_manager.py due to sys.modules pollution")
    def test_init_success(self, client):
        """测试初始化成功"""
        # 注意: 由于 ai_judge_service 在路由内局部导入, mock 无法应用到运行时导入
        # 此测试验证 API 能正确处理 openid 参数并返回成功响应
        response = client.post("/api/ai-judge/init", json={
            "openid": "test_openid"
        })

        assert response.status_code == 200
        data = response.json()
        # API 应返回成功响应(实际调用真实服务)
        assert data["success"] is True
        assert "agent_name" in data

    def test_init_missing_openid(self, client):
        """测试缺少 openid"""
        response = client.post("/api/ai-judge/init", json={})

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False


class TestAIJudgeClearAPI:
    """AI 裁判清除会话 API 测试"""

    def test_clear_session(self, client):
        """测试清除会话"""
        # 注意: 由于 ai_judge_service 在路由内局部导入, mock 无法应用到运行时导入
        # 此测试验证 API 能正确处理清除会话请求并返回成功响应
        # 不再 patch routes.db, 因为 RuleDatabase 的 mock 由 mock_db fixture 处理
        response = client.post("/api/ai-judge/clear", json={
            "session_id": "test_session",
            "openid": "test_openid"
        })

        assert response.status_code == 200
        data = response.json()
        # API 应返回成功响应
        assert data["success"] is True


class TestRulesStatusAPI:
    """规则状态 API 测试"""

    def test_get_rules_status(self, client):
        """测试获取规则状态"""
        with patch('services.rule_downloader.RuleDownloader') as mock_downloader_class:
            mock_downloader = Mock()
            mock_downloader_class.return_value = mock_downloader
            mock_downloader._get_local_rules_info.return_value = {
                "version": "2024.01",
                "date": "2024-01-01"
            }
            mock_downloader._get_online_rules_info.return_value = {
                "version": "2024.02",
                "date": "2024-02-01"
            }
            mock_downloader._is_latest_version.return_value = False

            response = client.get("/api/rules/status")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
