#!/usr/bin/env python3
"""
AI Judge 每日限制单元测试

测试 _check_daily_limit() 方法和数据库操作方法的逻辑。
"""

import sys
import os
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
import importlib.util

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'functions', 'mtgAsk', 'backend'))

import pytest


# ==================== Mock 配置 ====================

# Mock 掉所有有问题的模块，避免链式导入失败
mock_openclaw_client = MagicMock()
mock_rule_db_class = Mock()
mock_config = MagicMock()

sys.modules['backend.services.openclaw_client'] = mock_openclaw_client
sys.modules['backend.database'] = MagicMock()
sys.modules['backend.database'].RuleDatabase = mock_rule_db_class
sys.modules['database'] = MagicMock()
sys.modules['database'].RuleDatabase = mock_rule_db_class
sys.modules['backend.services'] = MagicMock()
sys.modules['backend.services.openclaw_client'] = mock_openclaw_client
sys.modules['backend.services.agent_pool_manager'] = MagicMock()
sys.modules['backend.services.log_service'] = MagicMock()
sys.modules['backend.services.log_service'].log_info = MagicMock()
sys.modules['backend.services.log_service'].log_warning = MagicMock()
sys.modules['backend.services.log_service'].log_error = MagicMock()
sys.modules['backend.services.log_service'].log_service = MagicMock()
sys.modules['backend.services.mtgch_api'] = MagicMock()
sys.modules['backend.config'] = mock_config


# ==================== 加载模块 ====================

def load_ai_judge_service_module():
    """加载 AIJudgeService 模块"""
    ai_judge_path = os.path.join(os.path.dirname(__file__), '..', '..', 'functions', 'mtgAsk', 'backend', 'services', 'ai_judge_service.py')
    spec = importlib.util.spec_from_file_location("ai_judge_service", ai_judge_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules['ai_judge_service'] = module
    sys.modules['backend.services.ai_judge_service'] = module
    spec.loader.exec_module(module)
    return module


def load_database_module():
    """加载 RuleDatabase 模块"""
    db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'functions', 'mtgAsk', 'backend', 'database.py')
    spec = importlib.util.spec_from_file_location("database", db_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules['rule_database'] = module
    spec.loader.exec_module(module)
    return module


# ==================== Fixtures ====================

@pytest.fixture
def mock_db_instance():
    """创建 mock 数据库实例"""
    db = Mock()
    db.ensure_ai_judge_daily_stats_table = Mock(return_value=True)
    db.get_daily_question_count = Mock(return_value=0)
    db.increment_daily_question_count = Mock(return_value=True)
    return db


@pytest.fixture
def mock_config():
    """创建 mock 配置"""
    config = Mock()
    config.MINIMAX_API_KEY = "test_api_key"
    config.MINIMAX_MODEL = "MiniMax-Text-01"
    config.MINIMAX_BASE_URL = "https://api.minimax.chat/v1"
    config.OPENCLAW_ENABLED = False
    config.OPENCLAW_HOST = "127.0.0.1"
    config.OPENCLAW_PORT = "22"
    config.OPENCLAW_SSH_USER = "test"
    config.OPENCLAW_SSH_PASSWORD = ""
    config.OPENCLAW_SSH_KEY = ""
    config.OPENCLAW_SSH_KEY_CONTENT = ""
    config.OPENCLAW_AGENT = "main"
    config.OPENCLAW_MOCK = True
    config.AI_JUDGE_DAILY_LIMIT = 10
    return config


# ==================== _check_daily_limit 测试 ====================

class TestCheckDailyLimit:
    """测试 _check_daily_limit 方法"""

    def test_no_openid_returns_unlimited(self, mock_db_instance, mock_config):
        """无 openid 时不限制"""
        module = load_ai_judge_service_module()
        module.Config = mock_config

        service = module.AIJudgeService.__new__(module.AIJudgeService)
        service._daily_limit = mock_config.AI_JUDGE_DAILY_LIMIT

        # 无 openid
        is_allowed, current_count, remaining = service._check_daily_limit(None, mock_db_instance)

        assert is_allowed is True
        assert current_count == 0
        assert remaining == 10
        mock_db_instance.ensure_ai_judge_daily_stats_table.assert_not_called()

    def test_empty_openid_returns_unlimited(self, mock_db_instance, mock_config):
        """空字符串 openid 不限制"""
        module = load_ai_judge_service_module()
        module.Config = mock_config

        service = module.AIJudgeService.__new__(module.AIJudgeService)
        service._daily_limit = mock_config.AI_JUDGE_DAILY_LIMIT

        is_allowed, current_count, remaining = service._check_daily_limit("", mock_db_instance)

        assert is_allowed is True
        assert remaining == 10

    def test_under_limit_allows(self, mock_db_instance, mock_config):
        """当日次数未超限，允许"""
        mock_db_instance.get_daily_question_count.return_value = 5  # 用了5次

        module = load_ai_judge_service_module()
        module.Config = mock_config

        service = module.AIJudgeService.__new__(module.AIJudgeService)
        service._daily_limit = mock_config.AI_JUDGE_DAILY_LIMIT

        is_allowed, current_count, remaining = service._check_daily_limit("test_user", mock_db_instance)

        assert is_allowed is True
        assert current_count == 5
        assert remaining == 5  # 10 - 5 = 5

    def test_at_limit_blocks(self, mock_db_instance, mock_config):
        """达到限制时阻止"""
        mock_db_instance.get_daily_question_count.return_value = 10  # 已用完

        module = load_ai_judge_service_module()
        module.Config = mock_config

        service = module.AIJudgeService.__new__(module.AIJudgeService)
        service._daily_limit = mock_config.AI_JUDGE_DAILY_LIMIT

        is_allowed, current_count, remaining = service._check_daily_limit("test_user", mock_db_instance)

        assert is_allowed is False
        assert current_count == 10
        assert remaining == 0

    def test_over_limit_blocks(self, mock_db_instance, mock_config):
        """超过限制时阻止"""
        mock_db_instance.get_daily_question_count.return_value = 15  # 超过限制

        module = load_ai_judge_service_module()
        module.Config = mock_config

        service = module.AIJudgeService.__new__(module.AIJudgeService)
        service._daily_limit = mock_config.AI_JUDGE_DAILY_LIMIT

        is_allowed, current_count, remaining = service._check_daily_limit("test_user", mock_db_instance)

        assert is_allowed is False
        assert remaining == 0

    def test_zero_count_allows(self, mock_db_instance, mock_config):
        """当日次数为0时允许"""
        mock_db_instance.get_daily_question_count.return_value = 0

        module = load_ai_judge_service_module()
        module.Config = mock_config

        service = module.AIJudgeService.__new__(module.AIJudgeService)
        service._daily_limit = mock_config.AI_JUDGE_DAILY_LIMIT

        is_allowed, current_count, remaining = service._check_daily_limit("new_user", mock_db_instance)

        assert is_allowed is True
        assert remaining == 10

    def test_custom_daily_limit(self, mock_db_instance):
        """自定义每日限制"""
        mock_db_instance.get_daily_question_count.return_value = 5

        module = load_ai_judge_service_module()
        module.Config = mock_config

        service = module.AIJudgeService.__new__(module.AIJudgeService)
        service._daily_limit = 5  # 自定义限制为5

        is_allowed, current_count, remaining = service._check_daily_limit("test_user", mock_db_instance)

        assert is_allowed is False  # 5 >= 5，超限
        assert remaining == 0


# ==================== 数据库方法测试 ====================

class TestDatabaseMethods:
    """测试数据库每日统计相关方法"""

    def test_ensure_table_sql(self):
        """验证建表 SQL 正确"""
        module = load_database_module()
        db = module.RuleDatabase()

        # Mock execute_write_sql
        db._execute_write_sql = Mock(return_value=True)

        result = db.ensure_ai_judge_daily_stats_table()

        assert result is True
        db._execute_write_sql.assert_called_once()
        call_args = db._execute_write_sql.call_args[0][0]
        assert 'ai_judge_daily_stats' in call_args
        assert 'openid' in call_args
        assert 'date' in call_args
        assert 'question_count' in call_args
        assert 'UNIQUE KEY uk_openid_date' in call_args

    def test_get_daily_question_count_returns_value(self):
        """验证查询返回正确次数"""
        module = load_database_module()
        db = module.RuleDatabase()

        mock_result = [{'question_count': 7}]
        db._execute_read_sql_with_params = Mock(return_value=mock_result)

        result = db.get_daily_question_count("test_user", "2026-03-30")

        assert result == 7
        db._execute_read_sql_with_params.assert_called_once()
        call_args = db._execute_read_sql_with_params.call_args
        # call_args[0] 是 (sql, params) tuple
        _, params = call_args[0]
        assert 'test_user' in params
        assert '2026-03-30' in params

    def test_get_daily_question_count_returns_zero_when_empty(self):
        """验证无记录时返回0"""
        module = load_database_module()
        db = module.RuleDatabase()

        db._execute_read_sql_with_params = Mock(return_value=[])

        result = db.get_daily_question_count("new_user", "2026-03-30")

        assert result == 0

    def test_increment_uses_on_duplicate_key(self):
        """验证递增使用 ON DUPLICATE KEY UPDATE"""
        module = load_database_module()
        db = module.RuleDatabase()

        db._execute_write_sql_with_params = Mock(return_value=True)

        result = db.increment_daily_question_count("test_user", "2026-03-30")

        assert result is True
        db._execute_write_sql_with_params.assert_called_once()
        call_args = db._execute_write_sql_with_params.call_args[0][0]
        assert 'INSERT INTO ai_judge_daily_stats' in call_args
        assert 'ON DUPLICATE KEY UPDATE' in call_args
        assert 'question_count = question_count + 1' in call_args


# ==================== chat() 限制触发测试 ====================

class TestChatDailyLimit:
    """测试 chat() 方法的每日限制触发"""

    def test_chat_blocks_when_limit_exceeded(self, mock_config):
        """chat() 在超限时返回限制提示"""
        module = load_ai_judge_service_module()
        module.Config = mock_config

        service = module.AIJudgeService.__new__(module.AIJudgeService)
        service._daily_limit = 2
        service._last_request_time = {}  # 避免限流检查
        service._rate_limit_seconds = 0
        service.openclaw_enabled = False  # 禁用 OpenCLAW，避免真实调用

        # Mock agent_pool
        mock_db = Mock()
        mock_db.ensure_ai_judge_daily_stats_table = Mock()
        mock_db.get_daily_question_count = Mock(return_value=2)  # 已用完
        mock_db.increment_daily_question_count = Mock()

        service.agent_pool = Mock()
        service.agent_pool.db = mock_db

        result = service.chat("测试问题", session_id="test", openid="limit_user")

        assert result['success'] is False
        assert '今日问答次数已用完' in result['reply']
        assert result['daily_limit'] == 2
        assert result['remaining'] == 0

    def test_under_limit_does_not_block(self, mock_config):
        """验证未超限时 _check_daily_limit 返回允许"""
        module = load_ai_judge_service_module()
        module.Config = mock_config

        service = module.AIJudgeService.__new__(module.AIJudgeService)
        service._daily_limit = 10

        mock_db = Mock()
        mock_db.ensure_ai_judge_daily_stats_table = Mock()
        mock_db.get_daily_question_count = Mock(return_value=5)  # 用了5次

        is_allowed, current_count, remaining = service._check_daily_limit("normal_user", mock_db)

        assert is_allowed is True
        assert remaining == 5

    def test_increment_not_called_when_blocked(self, mock_config):
        """验证超限时 chat() 不调用 increment（因为直接返回了）"""
        module = load_ai_judge_service_module()
        module.Config = mock_config

        service = module.AIJudgeService.__new__(module.AIJudgeService)
        service._daily_limit = 2
        service._last_request_time = {}
        service._rate_limit_seconds = 0
        service.openclaw_enabled = False

        mock_db = Mock()
        mock_db.ensure_ai_judge_daily_stats_table = Mock()
        mock_db.get_daily_question_count = Mock(return_value=2)  # 已用完
        mock_db.increment_daily_question_count = Mock()

        service.agent_pool = Mock()
        service.agent_pool.db = mock_db

        result = service.chat("测试问题", session_id="test", openid="limit_user")

        # 直接被限制拦住，不会调用 increment
        assert result['success'] is False
        mock_db.increment_daily_question_count.assert_not_called()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
