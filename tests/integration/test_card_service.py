#!/usr/bin/env python3
"""
MTG 卡牌服务测试 (pytest 格式)

运行: pytest tests/integration/ -v -m integration
"""

import pytest

# 这些测试需要实际的数据库连接，默认跳过
pytestmark = pytest.mark.skip(reason="需要数据库环境")


def test_card_service_placeholder():
    """测试占位符"""
    pass
