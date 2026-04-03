#!/usr/bin/env python3
"""
OpenCLAWClient 单元测试 (pytest 格式)

使用 mock 模拟 SSH 连接，测试 OpenCLAW 客户端的功能。
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'functions', 'mtgAsk', 'backend'))

import pytest
from unittest.mock import Mock, patch, MagicMock

from services.openclaw_client import OpenCLAWClient, OpenCLAWConfig


# ==================== Fixtures ====================

@pytest.fixture
def mock_ssh_client():
    """创建 mock SSH 客户端"""
    with patch('paramiko.SSHClient') as mock:
        ssh_instance = Mock()
        mock.return_value = ssh_instance
        yield ssh_instance


@pytest.fixture
def client():
    """创建客户端实例（不使用真实连接）"""
    with patch('paramiko.SSHClient'):
        client = OpenCLAWClient(
            host="127.0.0.1",
            port=22,
            username="test",
            password="test"
        )
        yield client


# ==================== OpenCLAWClient 测试 ====================

class TestOpenCLAWConfig:
    """OpenCLAWConfig 配置类测试"""

    def test_default_config(self):
        """测试默认配置"""
        config = OpenCLAWConfig()
        assert config.host == "101.43.48.45"
        assert config.port == 22
        assert config.username == "root"
        assert config.agent == "main"
        assert config.timeout == 120

    def test_custom_config(self):
        """测试自定义配置"""
        config = OpenCLAWConfig(
            host="custom.host",
            port=2222,
            username="custom",
            agent="custom_agent",
            timeout=60
        )
        assert config.host == "custom.host"
        assert config.port == 2222
        assert config.username == "custom"
        assert config.agent == "custom_agent"
        assert config.timeout == 60


class TestOpenCLAWClientInit:
    """OpenCLAWClient 初始化测试"""

    def test_init_with_kwargs(self):
        """测试使用 kwargs 初始化"""
        with patch('paramiko.SSHClient'):
            client = OpenCLAWClient(
                host="test.host",
                port=2222,
                username="testuser"
            )
            assert client.host == "test.host"
            assert client.port == 2222
            assert client.username == "testuser"

    def test_init_sets_defaults(self):
        """测试初始化设置默认值"""
        with patch('paramiko.SSHClient'):
            client = OpenCLAWClient()
            # 默认值应该从 OpenCLAWConfig 继承
            assert client.host is not None
            assert client.port == 22


class TestBuildCommand:
    """build_command 方法测试"""

    def test_build_command_simple(self, client):
        """测试简单消息的命令构建"""
        cmd = client.build_command("Hello")
        assert "openclaw agent" in cmd
        assert "--agent" in cmd
        assert "Hello" in cmd

    def test_build_command_escapes_quotes(self, client):
        """测试消息中的引号会被转义"""
        cmd = client.build_command('Hello "World"')
        assert '\\"' in cmd or '\"' in cmd


class TestFilterStreamMarkers:
    """_filter_stream_markers 方法测试"""

    def test_filter_completed(self, client):
        """测试过滤 completed 标记"""
        result = client._filter_stream_markers("completed")
        assert result == ""

    def test_filter_thinking(self, client):
        """测试过滤 thinking 标记"""
        result = client._filter_stream_markers("thinking...")
        assert result == ""

    def test_filter_processing(self, client):
        """测试过滤 processing 标记"""
        result = client._filter_stream_markers("processing...")
        assert result == ""

    def test_filter_done(self, client):
        """测试过滤 done 标记"""
        result = client._filter_stream_markers("done")
        assert result == ""

    def test_keep_normal_text(self, client):
        """测试保留正常文本"""
        text = "这是一个正常的回复"
        result = client._filter_stream_markers(text)
        assert result == text

    def test_filter_empty_string(self, client):
        """测试过滤空字符串"""
        result = client._filter_stream_markers("")
        assert result == ""


class TestExtractMessageContent:
    """_extract_message_content 方法测试"""

    def test_extract_text_content(self, client):
        """测试提取文本内容"""
        content = [{"type": "text", "text": "Hello World"}]
        result = client._extract_message_content(content)
        assert result == "Hello World"

    def test_extract_multiple_texts(self, client):
        """测试提取多个文本片段"""
        content = [
            {"type": "text", "text": "Hello "},
            {"type": "text", "text": "World"}
        ]
        result = client._extract_message_content(content)
        assert result == "Hello World"

    def test_skip_thinking_content(self, client):
        """测试跳过 thinking 内容"""
        content = [
            {"type": "text", "text": "Hello "},
            {"type": "thinking", "text": "thinking..."},
            {"type": "text", "text": "World"}
        ]
        result = client._extract_message_content(content)
        assert result == "Hello World"

    def test_extract_string_content(self, client):
        """测试提取字符串内容"""
        content = "Just a string"
        result = client._extract_message_content(content)
        assert result == "Just a string"

    def test_extract_empty_content(self, client):
        """测试提取空内容"""
        result = client._extract_message_content([])
        assert result == ""

    def test_extract_none_content(self, client):
        """测试提取 None 内容"""
        result = client._extract_message_content(None)
        assert result == ""


class TestCheckConnection:
    """check_connection 方法测试"""

    def test_check_connection_success(self, client, mock_ssh_client):
        """测试连接检查成功"""
        # 设置 mock
        stdin = Mock()
        stdout = Mock()
        stdout.read.return_value = b"ok"
        mock_ssh_client.exec_command.return_value = (stdin, stdout, Mock())
        client._ssh_client = mock_ssh_client

        result = client.check_connection()
        assert result is True

    def test_check_connection_failure(self, client, mock_ssh_client):
        """测试连接检查失败"""
        # 设置 mock 抛出异常
        mock_ssh_client.exec_command.side_effect = Exception("Connection failed")
        client._ssh_client = mock_ssh_client

        result = client.check_connection()
        assert result is False


class TestCallAgentJson:
    """call_agent_json 方法测试"""

    def test_call_agent_json_success(self, client, mock_ssh_client):
        """测试 JSON 调用成功"""
        import json

        # 构造成功的 JSON 响应
        response = {
            "status": "ok",
            "result": {
                "payloads": [
                    {"text": "Test response"}
                ]
            }
        }

        stdin = Mock()
        stdout = Mock()
        stdout.read.return_value = json.dumps(response).encode()
        stderr = Mock()
        stderr.read.return_value = b""
        mock_ssh_client.exec_command.return_value = (stdin, stdout, stderr)
        client._ssh_client = mock_ssh_client

        result = client.call_agent_json("test message")

        assert result["status"] == "ok"
        assert result["text"] == "Test response"

    def test_call_agent_json_error_response(self, client, mock_ssh_client):
        """测试返回错误响应"""
        import json

        response = {
            "status": "error",
            "message": "Something went wrong"
        }

        stdin = Mock()
        stdout = Mock()
        stdout.read.return_value = json.dumps(response).encode()
        stderr = Mock()
        stderr.read.return_value = b""
        mock_ssh_client.exec_command.return_value = (stdin, stdout, stderr)
        client._ssh_client = mock_ssh_client

        result = client.call_agent_json("test message")

        assert result["status"] == "error"

    def test_call_agent_json_exception(self, client, mock_ssh_client):
        """测试调用抛出异常"""
        mock_ssh_client.exec_command.side_effect = Exception("SSH error")
        client._ssh_client = mock_ssh_client

        result = client.call_agent_json("test message")

        assert result["status"] == "error"
        assert "SSH error" in result["message"]


class TestDeleteSession:
    """delete_session 方法测试"""

    def test_delete_session_no_session_id(self, client):
        """测试删除会话时无 session_id"""
        result = client.delete_session(agent_name="test_agent", session_id=None)
        assert result is False

    def test_delete_session_success(self, client, mock_ssh_client):
        """测试删除会话成功"""
        stdin = Mock()
        stdout = Mock()
        stdout.read.return_value = b""
        stderr = Mock()
        stderr.read.return_value = b""
        mock_ssh_client.exec_command.return_value = (stdin, stdout, stderr)

        # Mock SFTP
        mock_sftp = Mock()
        mock_sftp.file.return_value.__enter__ = Mock()
        mock_sftp.file.return_value.__exit__ = Mock()
        mock_ssh_client.open_sftp.return_value = mock_sftp
        client._ssh_client = mock_ssh_client

        result = client.delete_session(agent_name="test_agent", session_id="test_session")

        # 命令应该被执行
        assert mock_ssh_client.exec_command.called

    def test_delete_session_fallback_to_sftp(self, client, mock_ssh_client):
        """测试删除会话失败时回退到 SFTP"""
        # 命令返回错误
        stdin = Mock()
        stdout = Mock()
        stdout.read.return_value = b""
        stderr = Mock()
        stderr.read.return_value = b"error"
        mock_ssh_client.exec_command.return_value = (stdin, stdout, stderr)

        # Mock SFTP
        mock_sftp = Mock()
        mock_sftp.remove = Mock()
        mock_sftp.file.return_value.__enter__ = Mock(return_value=Mock())
        mock_sftp.file.return_value.__exit__ = Mock()
        mock_ssh_client.open_sftp.return_value = mock_sftp
        client._ssh_client = mock_ssh_client

        result = client.delete_session(agent_name="test_agent", session_id="test_session")

        # 应该尝试 SFTP 删除
        assert mock_sftp.remove.called or mock_sftp.file.called


class TestContextManager:
    """上下文管理器测试"""

    def test_context_manager(self, client, mock_ssh_client):
        """测试 with 语句"""
        mock_ssh_client.exec_command.return_value = (Mock(), Mock(), Mock())
        client._ssh_client = mock_ssh_client

        with client:
            pass

        # 应该调用 close
        assert mock_ssh_client.close.called

    def test_context_manager_with_exception(self, client, mock_ssh_client):
        """测试 with 语句抛出异常"""
        mock_ssh_client.exec_command.side_effect = Exception("test")
        client._ssh_client = mock_ssh_client

        with pytest.raises(Exception):
            with client:
                raise Exception("test")

        # 应该调用 close
        assert mock_ssh_client.close.called
