#!/usr/bin/env python3
"""
AgentPoolManager 单元测试 (pytest 格式)

使用 mock 模拟数据库和 SSH 连接，测试 Agent 池管理器的功能。
"""

import sys
import os

# 添加项目路径 (指向 functions/mtgAsk/backend，这样 backend.database 可以正确导入)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'functions', 'mtgAsk', 'backend'))

import pytest
from unittest.mock import Mock, patch, MagicMock
import importlib.util

# Mock 掉所有有问题的模块，避免链式导入失败
mock_openclaw_client = MagicMock()
mock_rule_db_class = Mock()

# 预先注册 mock 模块
sys.modules['backend.services.openclaw_client'] = mock_openclaw_client
sys.modules['backend.database'] = MagicMock()
sys.modules['backend.database'].RuleDatabase = mock_rule_db_class
sys.modules['database'] = MagicMock()
sys.modules['database'].RuleDatabase = mock_rule_db_class
sys.modules['backend.services'] = MagicMock()

# 使用 importlib 直接从文件加载 agent_pool_manager 模块
agent_pool_mgr_path = os.path.join(os.path.dirname(__file__), '..', '..', 'functions', 'mtgAsk', 'backend', 'services', 'agent_pool_manager.py')
spec = importlib.util.spec_from_file_location("backend.services.agent_pool_manager", agent_pool_mgr_path)
agent_pool_module = importlib.util.module_from_spec(spec)

# 注入 mock 的 RuleDatabase 到模块的全局命名空间 (覆盖原文件导入)
agent_pool_module.RuleDatabase = mock_rule_db_class
agent_pool_module.OpenCLAWClient = mock_openclaw_client

# 执行加载模块
spec.loader.exec_module(agent_pool_module)

# 注册到 sys.modules 这样 patch 可以找到
sys.modules['agent_pool_manager'] = agent_pool_module
sys.modules['backend.services.agent_pool_manager'] = agent_pool_module

# 获取 AgentPoolManager 类
AgentPoolManager = agent_pool_module.AgentPoolManager


# ==================== Fixtures ====================

@pytest.fixture
def mock_db():
    """创建 mock 数据库"""
    with patch('agent_pool_manager.RuleDatabase') as mock:
        db_instance = Mock()
        mock.return_value = db_instance
        db_instance.ensure_agent_pool_table = Mock()
        yield db_instance


@pytest.fixture
def mock_openclaw_client():
    """创建 mock OpenCLAWClient"""
    with patch('agent_pool_manager.OpenCLAWClient') as mock:
        client_instance = Mock()
        mock.return_value.__enter__ = Mock(return_value=client_instance)
        mock.return_value.__exit__ = Mock(return_value=False)
        yield client_instance


@pytest.fixture
def manager(mock_db, mock_openclaw_client):
    """创建 AgentPoolManager 实例"""
    manager = AgentPoolManager(db=mock_db)
    yield manager


# ==================== AgentPoolManager 测试 ====================

class TestSanitizeOpenid:
    """_sanitize_openid 方法测试"""

    def test_sanitize_at_symbol(self, manager):
        """测试处理 @ 符号"""
        result = manager._sanitize_openid("user@example.com")
        assert "@" not in result
        assert "_at_" in result

    def test_sanitize_dash(self, manager):
        """测试处理连字符"""
        result = manager._sanitize_openid("user-id-123")
        assert "-" not in result
        assert "_" in result

    def test_sanitize_dot(self, manager):
        """测试处理点号"""
        result = manager._sanitize_openid("user.name")
        assert "." not in result
        assert "_" in result

    def test_sanitize_multiple_special_chars(self, manager):
        """测试处理多个特殊字符"""
        result = manager._sanitize_openid("user@domain.com-id")
        assert "@" not in result
        assert "." not in result
        assert "-" not in result


class TestGenerateAgentName:
    """_generate_agent_name 方法测试"""

    def test_generate_agent_name_format(self, manager):
        """测试生成的 agent 名称格式"""
        result = manager._generate_agent_name("test_openid")
        assert result == "user_test_openid"

    def test_generate_agent_name_with_special_chars(self, manager):
        """测试带特殊字符的 openid"""
        result = manager._generate_agent_name("user@example.com")
        assert result.startswith("user_")
        assert "@" not in result


class TestGetOrCreateAgent:
    """get_or_create_agent 方法测试"""

    def test_get_existing_agent(self, manager, mock_db):
        """测试获取已存在的 Agent"""
        mock_db.get_agent_by_openid.return_value = {
            "openid": "test_openid",
            "agent_name": "user_test_openid"
        }

        agent_name, is_new = manager.get_or_create_agent("test_openid")

        assert agent_name == "user_test_openid"
        assert is_new is False
        mock_db.update_agent_last_used.assert_called_once_with("test_openid")

    def test_create_new_agent(self, manager, mock_db, mock_openclaw_client):
        """测试创建新的 Agent"""
        mock_db.get_agent_by_openid.return_value = None
        mock_db.get_active_agent_count.return_value = 0
        mock_db.create_agent = Mock()

        # Mock SSH client
        ssh_mock = Mock()
        mock_openclaw_client._get_ssh_client.return_value = ssh_mock
        stdin_mock = Mock()
        stdout_mock = Mock()
        stdout_mock.read.return_value = b'{"status": "ok"}'
        stderr_mock = Mock()
        stderr_mock.read.return_value = b""
        ssh_mock.exec_command.return_value = (stdin_mock, stdout_mock, stderr_mock)

        agent_name, is_new = manager.get_or_create_agent("new_openid")

        assert agent_name == "user_new_openid"
        assert is_new is True
        mock_db.create_agent.assert_called_once()

    def test_create_new_agent_when_at_limit(self, manager, mock_db, mock_openclaw_client):
        """测试 Agent 数量达到上限时创建新 Agent"""
        mock_db.get_agent_by_openid.return_value = None
        mock_db.get_active_agent_count.return_value = 100  # 达到上限

        # Mock _recycle_if_needed
        with patch.object(manager, '_recycle_if_needed', return_value=1):
            # 再调用时返回略低数量
            mock_db.get_active_agent_count.side_effect = [100, 99]

            # Mock _force_recycle_oldest
            with patch.object(manager, '_force_recycle_oldest'):
                # Mock SSH client
                ssh_mock = Mock()
                mock_openclaw_client._get_ssh_client.return_value = ssh_mock
                stdin_mock = Mock()
                stdout_mock = Mock()
                stdout_mock.read.return_value = b'{"status": "ok"}'
                stderr_mock = Mock()
                stderr_mock.read.return_value = b""
                ssh_mock.exec_command.return_value = (stdin_mock, stdout_mock, stderr_mock)

                agent_name, is_new = manager.get_or_create_agent("new_openid")

                assert is_new is True


class TestReleaseAgent:
    """release_agent 方法测试"""

    def test_release_agent(self, manager, mock_db):
        """测试标记 Agent 为空闲"""
        mock_db.mark_agent_idle.return_value = True

        result = manager.release_agent("test_openid")

        assert result is True
        mock_db.mark_agent_idle.assert_called_once_with("test_openid")


class TestCleanupIdleAgents:
    """cleanup_idle_agents 方法测试"""

    def test_cleanup_no_idle_agents(self, manager, mock_db):
        """测试无空闲 Agent 时"""
        mock_db.get_idle_agents_older_than.return_value = []

        result = manager.cleanup_idle_agents()

        assert result == 0

    def test_cleanup_with_idle_agents(self, manager, mock_db, mock_openclaw_client):
        """测试清理空闲 Agents"""
        mock_db.get_idle_agents_older_than.return_value = [
            {"openid": "user1", "agent_name": "user_user1"},
            {"openid": "user2", "agent_name": "user_user2"}
        ]
        mock_db.delete_agent_by_openid.return_value = True

        # Mock SSH client
        ssh_mock = Mock()
        mock_openclaw_client._get_ssh_client.return_value = ssh_mock
        stdin_mock = Mock()
        stdout_mock = Mock()
        stdout_mock.read.return_value = b""
        stderr_mock = Mock()
        stderr_mock.read.return_value = b""
        ssh_mock.exec_command.return_value = (stdin_mock, stdout_mock, stderr_mock)

        with patch.object(manager, '_destroy_remote_agent', return_value=True):
            result = manager.cleanup_idle_agents()

        assert result == 2


class TestRecycleIfNeeded:
    """_recycle_if_needed 方法测试"""

    def test_recycle_below_threshold(self, manager, mock_db):
        """测试未达到回收阈值时"""
        mock_db.get_active_agent_count.return_value = 50

        with patch.object(manager, 'cleanup_idle_agents', return_value=0) as mock_cleanup:
            result = manager._recycle_if_needed()

            assert result == 0
            mock_cleanup.assert_not_called()

    def test_recycle_at_threshold(self, manager, mock_db):
        """测试达到回收阈值时"""
        # MAX_AGENTS = 100, RECYCLE_THRESHOLD = 80
        # 达到 80 时触发回收
        mock_db.get_active_agent_count.return_value = 85

        with patch.object(manager, 'cleanup_idle_agents', return_value=2) as mock_cleanup:
            result = manager._recycle_if_needed()

            assert result == 2
            mock_cleanup.assert_called_once()


class TestGetPoolStats:
    """get_pool_stats 方法测试"""

    def test_get_pool_stats(self, manager, mock_db):
        """测试获取池统计信息"""
        mock_db.get_active_agent_count.return_value = 50
        mock_db.get_idle_agents_older_than.return_value = [
            {"openid": "user1"},
            {"openid": "user2"},
            {"openid": "user3"}
        ]

        result = manager.get_pool_stats()

        assert result["max_agents"] == 100
        assert result["active_agents"] == 50
        assert result["idle_agents"] == 3
        assert "50/100" in result["utilization"]


class TestDestroyRemoteAgent:
    """_destroy_remote_agent 方法测试"""

    def test_destroy_remote_agent_success(self, manager, mock_openclaw_client):
        """测试成功销毁远程 Agent"""
        # Mock SSH client
        ssh_mock = Mock()
        mock_openclaw_client._get_ssh_client.return_value = ssh_mock
        stdin_mock = Mock()
        stdout_mock = Mock()
        stdout_mock.read.return_value = b""
        stderr_mock = Mock()
        stderr_mock.read.return_value = b""
        ssh_mock.exec_command.return_value = (stdin_mock, stdout_mock, stderr_mock)

        result = manager._destroy_remote_agent("test_agent")

        assert result is True
        # 应该执行多个命令
        assert ssh_mock.exec_command.call_count >= 2

    def test_destroy_remote_agent_exception(self, manager, mock_openclaw_client):
        """测试销毁远程 Agent 失败"""
        mock_openclaw_client._get_ssh_client.side_effect = Exception("SSH error")

        result = manager._destroy_remote_agent("test_agent")

        assert result is False


class TestResetAgent:
    """reset_agent 方法测试"""

    def test_reset_agent_not_found(self, manager, mock_db):
        """测试重置不存在的 Agent"""
        mock_db.get_agent_by_openid.return_value = None

        result = manager.reset_agent("nonexistent_openid")

        assert result is False

    def test_reset_agent_success(self, manager, mock_db, mock_openclaw_client):
        """测试成功重置 Agent"""
        mock_db.get_agent_by_openid.return_value = {
            "openid": "test_openid",
            "agent_name": "user_test_openid"
        }

        # Mock SSH client
        ssh_mock = Mock()
        mock_openclaw_client._get_ssh_client.return_value = ssh_mock
        stdin_mock = Mock()
        stdout_mock = Mock()
        stdout_mock.read.return_value = b""
        stderr_mock = Mock()
        stderr_mock.read.return_value = b""
        ssh_mock.exec_command.return_value = (stdin_mock, stdout_mock, stderr_mock)

        result = manager.reset_agent("test_openid")

        assert result is True


class TestCleanupAllSessions:
    """cleanup_all_sessions 方法测试"""

    def test_cleanup_all_sessions_success(self, manager, mock_openclaw_client):
        """测试成功清理所有会话"""
        # Mock SSH client
        ssh_mock = Mock()
        mock_openclaw_client._get_ssh_client.return_value = ssh_mock
        stdin_mock = Mock()
        stdout_mock = Mock()
        stdout_mock.read.return_value = b"Cleanup completed"
        stderr_mock = Mock()
        stderr_mock.read.return_value = b""
        ssh_mock.exec_command.return_value = (stdin_mock, stdout_mock, stderr_mock)

        result = manager.cleanup_all_sessions()

        assert result["success"] is True
        assert "Cleanup" in result["output"]

    def test_cleanup_all_sessions_exception(self, manager, mock_openclaw_client):
        """测试清理所有会话失败"""
        mock_openclaw_client._get_ssh_client.side_effect = Exception("SSH error")

        result = manager.cleanup_all_sessions()

        assert result["success"] is False
        assert "SSH error" in result["error"]


class TestForceRecycleOldest:
    """_force_recycle_oldest 方法测试"""

    def test_force_recycle_oldest_no_agent(self, manager, mock_db, mock_openclaw_client):
        """测试没有可回收的 Agent 时"""
        mock_db.get_lru_agent.return_value = None

        with patch.object(manager, '_destroy_remote_agent', return_value=True) as mock_destroy:
            manager._force_recycle_oldest()
            mock_destroy.assert_not_called()

    def test_force_recycle_oldest_with_agent(self, manager, mock_db, mock_openclaw_client):
        """测试回收最老的 Agent"""
        mock_db.get_lru_agent.return_value = {
            "openid": "old_user",
            "agent_name": "user_old_user"
        }

        # Mock SSH client
        ssh_mock = Mock()
        mock_openclaw_client._get_ssh_client.return_value = ssh_mock
        stdin_mock = Mock()
        stdout_mock = Mock()
        stdout_mock.read.return_value = b""
        stderr_mock = Mock()
        stderr_mock.read.return_value = b""
        ssh_mock.exec_command.return_value = (stdin_mock, stdout_mock, stderr_mock)

        with patch.object(manager, '_destroy_remote_agent', return_value=True):
            manager._force_recycle_oldest()

        mock_db.delete_agent_by_openid.assert_called_once_with("old_user")


# ==================== Cleanup ====================

@pytest.fixture(scope="module", autouse=True)
def cleanup_sys_modules():
    """清理 sys.modules 中被污染的 mock 模块,避免影响其他测试"""
    yield
    # 清理 test_agent_pool_manager.py 添加的 mock 模块
    modules_to_remove = [
        'backend.services.openclaw_client',
        'backend.database',
        'database',
        'backend.services',
        'agent_pool_manager',
        'backend.services.agent_pool_manager',
        'backend.services.ai_judge_service',
        'ai_judge_service',
    ]
    for mod in modules_to_remove:
        if mod in sys.modules:
            del sys.modules[mod]
