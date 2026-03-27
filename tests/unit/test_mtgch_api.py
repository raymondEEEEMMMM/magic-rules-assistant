#!/usr/bin/env python3
"""
MTGCH API 单元测试 (pytest 格式)

使用 mock 模拟 HTTP 请求，测试 API 客户端的功能。
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'functions', 'mtgAsk', 'backend'))

import pytest
from unittest.mock import Mock, patch, MagicMock

from services.mtgch_api import MTGCHAPIClient, format_card_info


# ==================== Fixtures ====================

@pytest.fixture
def mock_session():
    """创建 mock session"""
    with patch('services.mtgch_api.requests.Session') as mock:
        yield mock.return_value


@pytest.fixture
def client():
    """创建客户端实例"""
    client = MTGCHAPIClient(timeout=5)
    yield client
    client.close()


# ==================== MTGCHAPIClient 测试 ====================

class TestMTGCHAPIClient:
    """MTGCH API 客户端测试类"""

    def test_search_cards_success(self, mock_session):
        """测试搜索卡牌成功"""
        # Mock 响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {"name": "闪电风暴", "name_en": "Lightning Storm", "mana_cost": "{2}{R}"}
            ],
            "total": 1
        }
        mock_session.get.return_value = mock_response

        # 使用新客户端
        client = MTGCHAPIClient()
        result = client.search_cards("闪电风暴")

        # 验证
        assert "items" in result
        assert len(result["items"]) == 1
        assert result["items"][0]["name"] == "闪电风暴"
        mock_session.get.assert_called_once()

    def test_search_cards_with_params(self, mock_session):
        """测试带参数的搜索"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": [], "total": 0}
        mock_session.get.return_value = mock_response

        client = MTGCHAPIClient()
        client.search_cards("test", page=2, page_size=50, order="name", unique="oracle_id")

        # 验证请求参数
        call_args = mock_session.get.call_args
        params = call_args.kwargs.get('params', {})

        assert params['q'] == "test"
        assert params['page'] == 2
        assert params['page_size'] == 50
        assert params['order'] == "name"
        assert params['unique'] == "oracle_id"

    def test_search_cards_network_error(self, mock_session):
        """测试搜索卡牌网络错误"""
        import requests
        mock_session.get.side_effect = requests.RequestException("Network error")

        client = MTGCHAPIClient()
        result = client.search_cards("test")

        assert "error" in result
        assert result["error"] == "Network error"

    def test_get_card_by_id_success(self, mock_session):
        """测试通过ID获取卡牌成功"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "uuid": "abc123",
            "name": "黑莲花",
            "name_en": "Black Lotus"
        }
        mock_session.get.return_value = mock_response

        client = MTGCHAPIClient()
        result = client.get_card_by_id("abc123")

        assert result is not None
        assert result["name"] == "黑莲花"

    def test_get_card_by_id_not_found(self, mock_session):
        """测试通过ID获取卡牌404"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_session.get.return_value = mock_response

        client = MTGCHAPIClient()
        result = client.get_card_by_id("notexist")

        assert result is None

    def test_get_card_by_set_and_number(self, mock_session):
        """测试通过系列代码和编号获取卡牌"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "name": "Test Card",
            "set_code": "MKM",
            "collector_number": "1"
        }
        mock_session.get.return_value = mock_response

        client = MTGCHAPIClient()
        result = client.get_card_by_set_and_number("MKM", "1")

        assert result is not None
        assert result["set_code"] == "MKM"

    def test_get_card_versions(self, mock_session):
        """测试获取卡牌所有版本"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"name": "Card V1", "rarity": "C"},
            {"name": "Card V2", "rarity": "R"}
        ]
        mock_session.get.return_value = mock_response

        client = MTGCHAPIClient()
        result = client.get_card_versions("abc123")

        assert isinstance(result, list)
        assert len(result) == 2

    def test_get_random_card(self, mock_session):
        """测试随机获取卡牌"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"name": "Random Card"}
        mock_session.get.return_value = mock_response

        client = MTGCHAPIClient()
        result = client.get_random_card()

        assert result is not None
        assert result["name"] == "Random Card"

    def test_get_adjacent_card(self, mock_session):
        """测试获取相邻卡牌"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"name": "Next Card"}
        mock_session.get.return_value = mock_response

        client = MTGCHAPIClient()
        result = client.get_adjacent_card("MKM", "1", "next")

        assert result is not None
        assert result["name"] == "Next Card"

    def test_get_adjacent_card_invalid_direction(self):
        """测试获取相邻卡牌无效方向"""
        client = MTGCHAPIClient()

        with pytest.raises(ValueError) as exc_info:
            client.get_adjacent_card("MKM", "1", "invalid")

        assert "next" in str(exc_info.value)

    def test_autocomplete(self, mock_session):
        """测试自动补全"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {"name": "闪电击"},
                {"name": "闪电风暴"}
            ]
        }
        mock_session.get.return_value = mock_response

        client = MTGCHAPIClient()
        result = client.autocomplete("闪电", size=10)

        assert "items" in result
        assert len(result["items"]) == 2

    def test_get_sets(self, mock_session):
        """测试获取系列列表"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"code": "MKM", "name": "Murders at Karlov Manor"},
            {"code": "ONE", "name": "Phyrexia: All Will Be One"}
        ]
        mock_session.get.return_value = mock_response

        client = MTGCHAPIClient()
        result = client.get_sets()

        assert isinstance(result, list)
        assert len(result) == 2

    def test_get_set_by_code(self, mock_session):
        """测试获取单个系列"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"code": "MKM", "name": "Test Set"}
        mock_session.get.return_value = mock_response

        client = MTGCHAPIClient()
        result = client.get_set_by_code("MKM")

        assert result is not None
        assert result["code"] == "MKM"

    def test_get_set_by_code_not_found(self, mock_session):
        """测试获取不存在的系列"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_session.get.return_value = mock_response

        client = MTGCHAPIClient()
        result = client.get_set_by_code("NOTEXIST")

        assert result is None

    def test_get_set_cards(self, mock_session):
        """测试获取系列卡牌"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [{"name": "Card1"}, {"name": "Card2"}],
            "total": 2
        }
        mock_session.get.return_value = mock_response

        client = MTGCHAPIClient()
        result = client.get_set_cards("MKM", page=1, page_size=10)

        assert "items" in result
        assert len(result["items"]) == 2

    def test_context_manager(self):
        """测试上下文管理器"""
        with MTGCHAPIClient() as client:
            assert client is not None


# ==================== format_card_info 测试 ====================

class TestFormatCardInfo:
    """format_card_info 函数测试类"""

    def test_format_card_info_none(self):
        """测试 None 输入"""
        result = format_card_info(None)
        assert result == "未找到卡牌"

    def test_format_card_info_empty(self):
        """测试空字典（空字典在Python中是falsy，返回'未找到卡牌'）"""
        result = format_card_info({})
        assert result == "未找到卡牌"

    def test_format_card_info_basic(self):
        """测试基本卡牌信息"""
        card = {
            "name": "闪电击",
            "name_en": "Lightning Bolt",
            "mana_cost": "{R}",
            "type_line": "瞬间",
            "rarity": "U"
        }

        result = format_card_info(card)

        assert "闪电击" in result
        assert "Lightning Bolt" in result
        assert "{R}" in result
        assert "瞬间" in result
        assert "非普通" in result  # U = 非普通

    def test_format_card_info_creature(self):
        """测试生物卡牌（包含力量/防御）"""
        card = {
            "name": "鬼怪向导",
            "power": "1",
            "toughness": "1"
        }

        result = format_card_info(card)

        assert "鬼怪向导" in result
        assert "1/1" in result

    def test_format_card_info_planeswalker(self):
        """测试鹏洛客卡牌（包含忠诚度）"""
        card = {
            "name": "杰斯",
            "loyalty": "3"
        }

        result = format_card_info(card)

        assert "杰斯" in result
        assert "忠诚度" in result
        assert "3" in result

    @pytest.mark.parametrize("rarity,expected", [
        ("C", "普通"),
        ("U", "非普通"),
        ("R", "稀有"),
        ("M", "秘稀"),
        ("S", "特别稀有"),
        ("X", "X"),  # 未知稀有度
    ])
    def test_format_card_info_rarity_mapping(self, rarity, expected):
        """测试稀有度映射"""
        card = {"name": "Test", "rarity": rarity}
        result = format_card_info(card)
        assert expected in result
