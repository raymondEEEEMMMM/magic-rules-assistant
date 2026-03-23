"""
OpenCLAW SSH + CLI 调用工具

提供通过 SSH 远程调用 OpenCLAW Gateway 的统一接口

使用方式:
    from backend.services.openclaw_client import OpenCLAWClient

    client = OpenCLAWClient(
        host="101.43.48.45",
        port=22,
        username="root",
        password="xxx",
        agent="main"
    )

    # 调用 agent
    result = client.call_agent("问题内容")

    # 获取 JSON 响应
    result = client.call_agent_json("问题内容")
"""

import json
import os
from typing import Optional, Dict, List, Any
from dataclasses import dataclass


@dataclass
class OpenCLAWConfig:
    """OpenCLAW 配置"""
    host: str = "101.43.48.45"
    port: int = 22
    username: str = "root"
    password: Optional[str] = None
    key_file: Optional[str] = None
    key_content: Optional[str] = None  # SSH 私钥内容
    agent: str = "main"
    timeout: int = 120


class OpenCLAWClient:
    """OpenCLAW SSH + CLI 客户端"""

    def __init__(self, config: Optional[OpenCLAWConfig] = None, **kwargs):
        """
        初始化客户端

        Args:
            config: OpenCLAWConfig 配置对象
            **kwargs: 直接传入配置参数，会覆盖 config
        """
        if config is None:
            config = OpenCLAWConfig()

        # 从 kwargs 覆盖配置
        self.host = kwargs.get("host", config.host)
        self.port = kwargs.get("port", config.port)
        self.username = kwargs.get("username", config.username)
        self.password = kwargs.get("password", config.password)
        self.key_file = kwargs.get("key_file", config.key_file)
        self.key_content = kwargs.get("key_content", config.key_content)  # SSH 私钥内容（Base64 或明文）
        self.agent = kwargs.get("agent", config.agent)
        self.timeout = kwargs.get("timeout", config.timeout)

        # 从环境变量读取默认值（kwargs 已有的值不会被覆盖）
        self.host = os.getenv("OPENCLAW_HOST", self.host)
        self.port = int(os.getenv("OPENCLAW_PORT", str(self.port)))
        self.username = os.getenv("OPENCLAW_SSH_USER", self.username)
        self.password = os.getenv("OPENCLAW_SSH_PASSWORD", self.password)
        self.key_file = os.getenv("OPENCLAW_SSH_KEY", self.key_file)
        self.key_content = os.getenv("OPENCLAW_SSH_KEY_CONTENT", self.key_content)
        # agent 参数以传入值优先，不被环境变量覆盖

        self._ssh_client = None

    def _get_ssh_client(self):
        """获取或创建 SSH 连接"""
        import paramiko

        if self._ssh_client is None:
            self._ssh_client = paramiko.SSHClient()
            self._ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # 使用密钥或密码连接
            if self.key_content:
                # 使用私钥内容连接
                from io import BytesIO
                import base64
                import tempfile
                import os

                key_content = self.key_content.strip()

                # 检查是否是带标记的 OpenSSH 格式
                if key_content.startswith('-----BEGIN'):
                    # 写入临时文件，paramiko 需要文件路径来读取 OpenSSH 格式密钥
                    try:
                        # 创建临时文件
                        fd, key_path = tempfile.mkstemp(suffix='_ssh_key')
                        os.write(fd, key_content.encode('utf-8'))
                        os.close(fd)

                        # 设置权限
                        os.chmod(key_path, 0o600)

                        # 使用文件路径连接
                        self._ssh_client.connect(
                            self.host,
                            port=self.port,
                            username=self.username,
                            key_filename=key_path,
                            timeout=30
                        )

                        # 清理临时文件
                        try:
                            os.unlink(key_path)
                        except:
                            pass

                        return self._ssh_client
                    except Exception:
                        # 继续尝试密码认证
                        pass

                # 如果密钥方式失败，尝试 base64 解码后的密钥内容
                try:
                    key_bytes = base64.b64decode(key_content)
                    key_file = BytesIO(key_bytes)
                    pkey = paramiko.Ed25519Key.from_private_key(key_file)
                    self._ssh_client.connect(
                        self.host,
                        port=self.port,
                        username=self.username,
                        pkey=pkey,
                        timeout=30
                    )
                except Exception:
                    # 继续尝试密码认证
                    pass

            # 密码认证（如果密钥方式失败）
            if self.password:
                self._ssh_client.connect(
                    self.host,
                    port=self.port,
                    username=self.username,
                    password=self.password,
                    timeout=30
                )
            elif self.key_file:
                self._ssh_client.connect(
                    self.host,
                    port=self.port,
                    username=self.username,
                    key_filename=self.key_file,
                    timeout=30
                )
            else:
                raise ValueError("未配置 SSH 密钥或密码")

        return self._ssh_client

    def close(self):
        """关闭 SSH 连接"""
        if self._ssh_client:
            self._ssh_client.close()
            self._ssh_client = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def build_command(self, message: str) -> str:
        """
        构建 OpenCLAW CLI 命令

        Args:
            message: 用户消息

        Returns:
            完整的命令字符串
        """
        escaped_message = message.replace('"', '\\"')
        return f'bash -i -c "openclaw agent --agent {self.agent} -m \\"{escaped_message}\\""'

    def call_agent(self, message: str, timeout: Optional[int] = None) -> str:
        """
        调用 Agent，返回纯文本响应

        Args:
            message: 用户消息
            timeout: 超时时间（秒）

        Returns:
            Agent 回复的文本内容
        """
        result = self.call_agent_json(message, timeout=timeout)
        if result and "text" in result:
            return result["text"]
        return ""

    def call_agent_json(self, message: str, timeout: Optional[int] = None) -> Dict:
        """
        调用 Agent，返回 JSON 响应

        Args:
            message: 用户消息
            timeout: 超时时间（秒）

        Returns:
            解析后的 JSON 响应
        """
        import paramiko

        timeout = timeout or self.timeout
        cmd = self.build_command(message)

        try:
            client = self._get_ssh_client()
            stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
            output = stdout.read().decode()
            error = stderr.read().decode()

            # 尝试解析 JSON 响应，如果失败则返回纯文本
            try:
                result = json.loads(output)
                if result.get("status") == "ok":
                    payloads = result.get("result", {}).get("payloads", [])
                    if payloads:
                        return {
                            "status": "ok",
                            "text": payloads[0].get("text", ""),
                            "raw": result
                        }
                return {"status": "error", "message": result}
            except json.JSONDecodeError:
                # 返回纯文本响应
                return {
                    "status": "ok",
                    "text": output.strip(),
                    "raw": output
                }

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def check_connection(self) -> bool:
        """
        检查 SSH 连接是否可用

        Returns:
            连接是否可用
        """
        try:
            client = self._get_ssh_client()
            stdin, stdout, stderr = client.exec_command("echo ok")
            result = stdout.read().decode().strip()
            return result == "ok"
        except Exception:
            return False


# ========== 便捷函数 ==========

def create_client(**kwargs) -> OpenCLAWClient:
    """创建 OpenCLAW 客户端的便捷函数"""
    return OpenCLAWClient(**kwargs)


def call_openclaw(message: str, **kwargs) -> str:
    """
    快速调用 OpenCLAW Agent

    Args:
        message: 用户消息
        **kwargs: 传递给 OpenCLAWClient 的参数

    Returns:
        Agent 回复
    """
    with OpenCLAWClient(**kwargs) as client:
        return client.call_agent(message)
