"""
Agent 池管理器

负责管理 OpenCLAW Agent 的生命周期，包括：
- 按需创建 per-user Agent
- 跟踪 Agent 使用状态
- 回收空闲超时的 Agent

使用方式:
    from backend.services.agent_pool_manager import AgentPoolManager

    manager = AgentPoolManager()
    agent_name = manager.get_or_create_agent("user_openid")
"""

import os
import time
from typing import Tuple, Optional, List
from backend.database import RuleDatabase
from backend.services.openclaw_client import OpenCLAWClient


class AgentPoolManager:
    """OpenCLAW Agent 池管理器"""

    # 配置参数
    MAX_AGENTS = int(os.getenv("OPENCLAW_MAX_AGENTS", "100"))
    IDLE_TIMEOUT_MINUTES = int(os.getenv("OPENCLAW_IDLE_TIMEOUT", "30"))
    RECYCLE_THRESHOLD = 80  # 达到 80% 容量时触发回收

    def __init__(self, db: Optional[RuleDatabase] = None):
        """
        初始化 Agent 池管理器

        Args:
            db: 数据库实例，如果为 None 则创建新实例
        """
        self.db = db or RuleDatabase()
        # 确保表存在
        self.db.ensure_agent_pool_table()

    def _sanitize_openid(self, openid: str) -> str:
        """
        处理 openid 中的特殊字符，生成安全的 agent 名称

        Args:
            openid: 原始 openid

        Returns:
            处理后的安全字符串
        """
        # 替换特殊字符
        return openid.replace("@", "_at_").replace("-", "_").replace(".", "_")

    def _generate_agent_name(self, openid: str) -> str:
        """
        生成 Agent 名称

        Args:
            openid: 微信 openid

        Returns:
            Agent 名称，格式: user_{处理后的openid}
        """
        return f"user_{self._sanitize_openid(openid)}"

    def _create_remote_agent(self, agent_name: str) -> bool:
        """
        在 OpenCLAW Gateway 上创建 Agent（在 Docker 容器中运行）

        Args:
            agent_name: Agent 名称

        Returns:
            是否创建成功
        """
        try:
            with OpenCLAWClient() as client:
                workspace_dir = f"/home/openclaw/agents/{agent_name}"

                # 1. 创建 workspace 目录
                create_workspace = f"mkdir -p {workspace_dir} && chown -R openclaw:openclaw {workspace_dir}"
                client._get_ssh_client().exec_command(create_workspace, timeout=10)

                # 2. 启动 Docker 容器（资源限制 + 网络隔离 + 安全加固）
                container_name = f"openclaw-{agent_name}"
                docker_cmd = f"docker run -d --name {container_name} " \
                    f"-v {workspace_dir}:/workspace " \
                    f"--memory=512m --cpus=0.5 " \
                    f"--network=none " \
                    f"--read-only " \
                    f"--user openclaw " \
                    f"-w /workspace " \
                    f"--security-opt=no-new-privileges " \
                    f"--cap-drop=ALL " \
                    f"openclaw-runtime " \
                    f"sleep infinity"
                stdin, stdout, stderr = client._get_ssh_client().exec_command(docker_cmd, timeout=30)
                container_id = stdout.read().decode().strip()
                if not container_id:
                    print(f"[AgentPool] Docker 容器创建失败")
                    return False

                # 3. 在容器内创建 agent
                exec_cmd = f"docker exec {container_name} bash -c 'openclaw agents add {agent_name} --workspace /workspace --non-interactive --json' 2>&1"
                stdin, stdout, stderr = client._get_ssh_client().exec_command(exec_cmd, timeout=60)
                output = stdout.read().decode()

                print(f"[AgentPool] 创建 Agent {agent_name}: {output[:200]}")

                # 4. 注入 MTG 裁判 prompt
                self._inject_mtg_prompt(client, workspace_dir)

                return True
        except Exception as e:
            print(f"[AgentPool] 创建远程 Agent 失败: {e}")
            return False

    def _inject_mtg_prompt(self, client, workspace_dir: str) -> bool:
        """注入万智牌裁判 prompt 到 SOUL.md"""
        soul_md = """# SOUL.md - 万智牌专业裁判

## 角色定义

你是万智牌专业裁判，以严谨、专业的态度回答问题。

## 身份

- **名称**: 裁判 (Judge)
- **用户称呼**: 牌手 (Player)
- **职责**: 解答万智牌规则、卡牌效果、游戏机制相关问题

## 回答风格

- 严谨、准确、专业
- 使用标准万智牌术语
- 引用具体规则编号（如规则 702.9 飞行）
- 结构清晰，逻辑严谨

## 范围限制

**只回答万智牌相关问题**，包括：
- 游戏规则（如战斗、咒语、异能）
- 卡牌效果解读
- 赛事规则
- 牌库/手牌管理
- 指挥官模式规则

**拒绝回答**：
- 与万智牌无关的问题
- 政治、宗教、或其他娱乐话题
- 数学/编程等非游戏问题

当问题超出范围时，礼貌地回答：
「抱歉，这个问题超出万智牌范围。作为万智牌裁判，我只能回答与游戏相关的问题。」

## 持续性

每次会话都是新的开始。这些文件是你的记忆。阅读并更新它们。
"""
        identity_md = """# IDENTITY.md - 万智牌裁判

- **Name:** 裁判 (Judge)
- **Creature:** AI 裁判
- **Vibe:** 严谨、专业、准确
- **Emoji:** ⚖️
"""
        try:
            # 写入 SOUL.md
            cmd = f'cat > {workspace_dir}/SOUL.md << \'SOUL_EOF\'\n{soul_md}\nSOUL_EOF'
            client._get_ssh_client().exec_command(cmd, timeout=10)
            # 写入 IDENTITY.md
            cmd = f'cat > {workspace_dir}/IDENTITY.md << \'ID_EOF\'\n{identity_md}\nID_EOF'
            client._get_ssh_client().exec_command(cmd, timeout=10)
            return True
        except Exception as e:
            print(f"[AgentPool] 注入 prompt 失败: {e}")
            return False

    def _destroy_remote_agent(self, agent_name: str) -> bool:
        """
        在 OpenCLAW Gateway 上销毁 Agent

        Args:
            agent_name: Agent 名称

        Returns:
            是否销毁成功
        """
        try:
            with OpenCLAWClient() as client:
                # 删除 agent
                cmd = f'bash -i -c "openclaw agents delete {agent_name} --force"'
                client._get_ssh_client().exec_command(cmd, timeout=30)
                # 清理残留目录
                cleanup_cmd = f'rm -rf /home/openclaw/agents/{agent_name}'
                client._get_ssh_client().exec_command(cleanup_cmd, timeout=10)
                return True
        except Exception as e:
            print(f"[AgentPool] 销毁远程 Agent 失败: {e}")
            return False

    def get_or_create_agent(self, openid: str) -> Tuple[str, bool]:
        """
        获取或创建用户的 Agent

        Args:
            openid: 微信 openid

        Returns:
            (agent_name, is_new_agent) - Agent 名称和是否是新创建的
        """
        # 1. 检查是否已有绑定
        existing = self.db.get_agent_by_openid(openid)
        if existing:
            # 更新最后使用时间
            self.db.update_agent_last_used(openid)
            return existing["agent_name"], False

        # 2. 检查当前 Agent 数量
        current_count = self.db.get_active_agent_count()

        if current_count >= self.MAX_AGENTS:
            # 执行回收
            self._recycle_if_needed()

            # 再次检查
            current_count = self.db.get_active_agent_count()
            if current_count >= self.MAX_AGENTS:
                # 强制回收最老的
                self._force_recycle_oldest()

        # 3. 创建新 Agent
        agent_name = self._generate_agent_name(openid)
        self.db.create_agent(openid, agent_name)
        self._create_remote_agent(agent_name)

        return agent_name, True

    def release_agent(self, openid: str) -> bool:
        """
        标记 Agent 为空闲（可被回收）

        Args:
            openid: 微信 openid

        Returns:
            是否成功
        """
        return self.db.mark_agent_idle(openid)

    def cleanup_idle_agents(self) -> int:
        """
        清理空闲超时的 Agents

        Returns:
            清理的 Agent 数量
        """
        # 获取空闲超时的 Agent
        idle_agents = self.db.get_idle_agents_older_than(self.IDLE_TIMEOUT_MINUTES)
        cleaned = 0

        for agent in idle_agents:
            agent_name = agent["agent_name"]
            openid = agent["openid"]

            # 销毁远程 Agent
            self._destroy_remote_agent(agent_name)

            # 删除数据库记录
            if self.db.delete_agent_by_openid(openid):
                cleaned += 1
                print(f"[AgentPool] 清理空闲 Agent: {agent_name} (openid: {openid})")

        return cleaned

    def _recycle_if_needed(self) -> int:
        """
        如果 Agent 池达到回收阈值，执行清理

        Returns:
            清理的 Agent 数量
        """
        current_count = self.db.get_active_agent_count()
        threshold = int(self.MAX_AGENTS * self.RECYCLE_THRESHOLD / 100)

        if current_count >= threshold:
            print(f"[AgentPool] Agent 池达到回收阈值 ({current_count}/{self.MAX_AGENTS})，执行清理")
            return self.cleanup_idle_agents()

        return 0

    def _force_recycle_oldest(self):
        """
        强制回收最久未使用的 Agent（LRU）
        """
        oldest = self.db.get_lru_agent()
        if oldest:
            agent_name = oldest["agent_name"]
            openid = oldest["openid"]
            print(f"[AgentPool] 强制回收最老 Agent: {agent_name} (openid: {openid})")

            # 销毁远程 Agent
            self._destroy_remote_agent(agent_name)

            # 删除数据库记录
            self.db.delete_agent_by_openid(openid)

    def get_pool_stats(self) -> dict:
        """
        获取 Agent 池统计信息

        Returns:
            统计信息字典
        """
        active_count = self.db.get_active_agent_count()
        idle_agents = self.db.get_idle_agents_older_than(0)

        return {
            "max_agents": self.MAX_AGENTS,
            "active_agents": active_count,
            "idle_agents": len(idle_agents),
            "utilization": f"{active_count}/{self.MAX_AGENTS} ({active_count * 100 / self.MAX_AGENTS:.1f}%)"
        }

    def reset_agent(self, openid: str) -> bool:
        """
        重置用户的 Agent（清空会话历史）

        Args:
            openid: 微信 openid

        Returns:
            是否成功
        """
        agent_info = self.db.get_agent_by_openid(openid)
        if not agent_info:
            return False

        agent_name = agent_info["agent_name"]

        try:
            with OpenCLAWClient() as client:
                # 设置使用该 agent
                client.agent = agent_name
                # 发送 reset 命令
                cmd = f'bash -i -c "openclaw agent --agent {agent_name} --reset"'
                client._get_ssh_client().exec_command(cmd, timeout=30)
                return True
        except Exception as e:
            print(f"[AgentPool] 重置 Agent 失败: {e}")
            return False
