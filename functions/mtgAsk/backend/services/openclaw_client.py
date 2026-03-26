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
        return f'bash -c "openclaw agent --agent {self.agent} -m \\"{escaped_message}\\""'

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
            text = result["text"]
            # 过滤流式标记
            text = self._filter_stream_markers(text)
            if text:
                return text
            # 如果过滤后为空，重新调用一次
            print("流式标记过滤后为空，重新调用...")
            return self._call_agent_with_retry(message, timeout)
        return ""

    def _call_agent_with_retry(self, message: str, timeout: Optional[int] = None, max_retries: int = 2) -> str:
        """带重试的 Agent 调用"""
        for attempt in range(max_retries):
            result = self.call_agent_json(message, timeout=timeout)
            if result and "text" in result:
                text = result["text"]
                text = self._filter_stream_markers(text)
                if text:
                    return text
                if attempt < max_retries - 1:
                    print(f"重试第 {attempt + 1} 次...")
            else:
                break
        # 多次重试后仍失败，返回空字符串
        return ""

    def _filter_stream_markers(self, text: str) -> str:
        """过滤 OpenCLAW 流式响应标记"""
        if not text:
            return text
        # 已知的流式标记
        markers = ["completed", "thinking...", "processing...", "done"]
        for marker in markers:
            if text.strip() == marker:
                return ""
        return text

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

    def get_sessions(self, agent_name: str = None, limit: int = 10, offset: int = 0) -> Dict:
        """
        获取 agent 的会话列表

        Args:
            agent_name: Agent 名称（默认使用 self.agent）
            limit: 返回数量限制
            offset: 偏移量

        Returns:
            包含 sessions 列表和总数的信息
        """
        effective_agent = agent_name or self.agent

        try:
            client = self._get_ssh_client()
            # 使用 openclaw sessions 命令获取会话列表
            cmd = f'bash -i -c "openclaw sessions --agent {effective_agent} --json"'
            stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
            output = stdout.read().decode().strip()

            if not output:
                return {"sessions": [], "pagination": {"total": 0, "limit": limit, "offset": offset, "hasMore": False}}

            result = json.loads(output)
            sessions = result.get("sessions", [])

            # 统计消息数量
            for session in sessions:
                session["messageCount"] = self._count_session_messages(effective_agent, session.get("sessionId"))

            # 处理分页
            total = len(sessions)
            paginated_sessions = sessions[offset:offset + limit]

            # 格式化输出
            formatted = []
            for s in paginated_sessions:
                ts = s.get("updatedAt", 0)
                from datetime import datetime
                formatted.append({
                    "sessionId": s.get("sessionId"),
                    "key": s.get("key"),
                    "updatedAt": ts,
                    "updatedAtReadable": datetime.fromtimestamp(ts/1000).strftime("%Y-%m-%d %H:%M:%S") if ts else None,
                    "ageMs": s.get("ageMs", 0),
                    "inputTokens": s.get("inputTokens", 0),
                    "outputTokens": s.get("outputTokens", 0),
                    "totalTokens": s.get("totalTokens", 0),
                    "model": s.get("model"),
                    "agentId": s.get("agentId"),
                    "kind": s.get("kind"),
                    "messageCount": s.get("messageCount", 0)
                })

            return {
                "sessions": formatted,
                "pagination": {
                    "total": total,
                    "limit": limit,
                    "offset": offset,
                    "hasMore": offset + limit < total
                }
            }
        except Exception as e:
            print(f"获取会话列表失败: {e}")
            return {"sessions": [], "error": str(e), "pagination": {"total": 0, "limit": limit, "offset": offset, "hasMore": False}}

    def _count_session_messages(self, agent_name: str, session_id: str) -> int:
        """统计会话的消息数量"""
        if not session_id:
            return 0
        try:
            session_file = f"/home/openclaw/.openclaw/agents/{agent_name}/sessions/{session_id}.jsonl"
            client = self._get_ssh_client()
            sftp = client.open_sftp()
            count = 0
            with sftp.file(session_file, 'r') as f:
                for line in f:
                    if line.strip():
                        event = json.loads(line)
                        if event.get("type") == "message":
                            count += 1
            sftp.close()
            return count
        except Exception:
            return 0

    def get_session_messages(self, agent_name: str, session_id: str, limit: int = 100) -> List[Dict]:
        """
        读取指定会话的消息历史

        Args:
            agent_name: Agent 名称
            session_id: 会话 ID
            limit: 返回消息数量限制

        Returns:
            消息列表
        """
        if not session_id:
            return []

        session_file = f"/home/openclaw/.openclaw/agents/{agent_name}/sessions/{session_id}.jsonl"

        try:
            client = self._get_ssh_client()
            sftp = client.open_sftp()

            messages = []
            seen_ids = set()  # 用于去重
            with sftp.file(session_file, 'r') as f:
                for line in f:
                    if line.strip():
                        event = json.loads(line)
                        if event.get("type") == "message":
                            msg = event.get("message", {})
                            role = msg.get("role")
                            # 只添加 user 和 assistant 消息，排除 toolResult
                            if role not in ("user", "assistant"):
                                continue
                            content = self._extract_message_content(msg.get("content", []))
                            if not content:
                                continue
                            msg_id = event.get("id")
                            # 去重：同一 id 的消息只添加一次
                            if msg_id in seen_ids:
                                continue
                            seen_ids.add(msg_id)
                            messages.append({
                                "id": msg_id,
                                "type": event.get("type"),
                                "role": role,
                                "content": content,
                                "timestamp": event.get("timestamp")
                            })

            sftp.close()

            # 限制返回数量
            return messages[-limit:] if len(messages) > limit else messages

        except Exception as e:
            print(f"读取会话消息失败: {e}")
            return []

    def _extract_message_content(self, content: List[Dict]) -> str:
        """
        从消息 content 列表中提取纯文本

        Args:
            content: 消息的 content 列表，通常是 [{"type": "text", "text": "..."}] 格式

        Returns:
            提取的纯文本内容
        """
        if not content:
            return ""
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts = []
            for item in content:
                if isinstance(item, dict):
                    if item.get("type") == "text":
                        parts.append(item.get("text", ""))
                    elif item.get("type") == "thinking":
                        # 跳过 thinking 内容
                        pass
            return "".join(parts)
        return str(content)

    def delete_session(self, agent_name: str = None, session_id: str = None) -> bool:
        """
        删除指定会话

        Args:
            agent_name: Agent 名称（默认使用 self.agent）
            session_id: 会话 ID

        Returns:
            是否删除成功
        """
        if not session_id:
            return False

        effective_agent = agent_name or self.agent

        try:
            client = self._get_ssh_client()
            # 使用 openclaw sessions --delete 命令删除会话
            cmd = f'bash -c "openclaw sessions --agent {effective_agent} --delete {session_id}"'
            stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
            output = stdout.read().decode().strip()
            error = stderr.read().decode().strip()
            print(f"删除会话命令输出: {output}, 错误: {error}")

            # 如果命令没有错误，尝试直接删除文件作为备用
            if error:
                session_file = f"/home/openclaw/.openclaw/agents/{effective_agent}/sessions/{session_id}.jsonl"
                sftp = client.open_sftp()
                try:
                    sftp.remove(session_file)
                    print(f"已通过 SFTP 删除会话文件: {session_file}")
                except FileNotFoundError:
                    print(f"会话文件不存在: {session_file}")
                except Exception as e:
                    print(f"SFTP 删除失败: {e}")
                finally:
                    sftp.close()
            return True
        except Exception as e:
            print(f"删除会话失败: {e}")
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
