#!/usr/bin/env python3
"""
AI 裁判知识库同步脚本
用于定时同步万智牌规则、卡牌数据到云存储，供 AI 裁判使用

知识库来源: https://github.com/Kuuusoda/magic-comp-rules-zh-cn-agent

使用方法:
    python sync_judge_knowledge.py           # 同步所有知识
    python sync_judge_knowledge.py --rules   # 仅同步规则
    python sync_judge_knowledge.py --cards   # 仅同步卡牌
    python sync_judge_knowledge.py --force   # 强制同步（忽略版本检查）
    python sync_judge_knowledge.py --schedule # 启动定时任务
"""
import os
import sys
import json
import logging
import argparse
import asyncio
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
import requests

# 添加 backend 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class KnowledgeSync:
    """知识库同步器"""

    # 云存储路径前缀
    CLOUD_STORAGE_PATH = "ai-judge/knowledge"

    # 知识库来源
    KNOWLEDGE_REPO = "Kuuusoda/magic-comp-rules-zh-cn-agent"
    KNOWLEDGE_BRANCH = "master"
    KNOWLEDGE_BASE_URL = f"https://raw.githubusercontent.com/{KNOWLEDGE_REPO}/{KNOWLEDGE_BRANCH}"

    # 本地数据目录
    LOCAL_DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'backend', 'data')
    RULES_DIR = os.path.join(LOCAL_DATA_DIR, 'rules')
    KNOWLEDGE_DIR = os.path.join(LOCAL_DATA_DIR, 'knowledge')
    CARDS_DIR = os.path.join(LOCAL_DATA_DIR, 'cards')

    # 知识库文件列表
    KNOWLEDGE_FILES = [
        # 规则文件（1-9章）
        "markdown/1.md",
        "markdown/2.md",
        "markdown/3.md",
        "markdown/4.md",
        "markdown/5.md",
        "markdown/6.md",
        "markdown/7.md",
        "markdown/8.md",
        "markdown/9.md",
        # 术语表
        "markdown/glossarycn.md",
        "markdown/glossary.md",        # 英文术语表
        "markdown/translatedterms.md",
        # 其他 markdown 文件
        "markdown/index.md",           # 规则索引
        "markdown/intro.md",           # 简介
        "markdown/credits.md",        # 贡献者
        # 知识图谱（新位置 references/）
        "references/triggered-abilities.md",
        "references/stack-priority.md",
        "references/continuous-effects.md",
        "references/copy-effects.md",
        "references/prevention-effects.md",
        "references/replacement-effects.md",
    ]

    # 知识图谱旧位置（兼容）
    KNOWLEDGE_FILES_LEGACY = [
        "knowledge-map/triggered-abilities.md",
        "knowledge-map/stack-priority.md",
        "knowledge-map/continuous-effects.md",
        "knowledge-map/copy-effects.md",
        "knowledge-map/prevention-effects.md",
        "knowledge-map/replacement-effects.md",
    ]

    # OpenCLAW Gateway 技能目录（服务器路径）
    OPENCLAW_SERVER_PATH = os.getenv("OPENCLAW_SERVER_PATH", "/root/openclaw/workspace/skills/ai_judge")

    # 本地 AI 裁判目录
    AI_JUDGE_LOCAL_DIR = os.path.join(
        os.path.dirname(__file__), '..', '..', '..',
        'ai_judge'
    )

    # SSH 配置
    OPENCLAW_HOST = os.getenv("OPENCLAW_HOST", "101.43.48.45")
    OPENCLAW_PORT = int(os.getenv("OPENCLAW_PORT_SSH", "19601"))
    OPENCLAW_USER = os.getenv("OPENCLAW_SSH_USER", "root")
    OPENCLAW_PASSWORD = os.getenv("OPENCLAW_SSH_PASSWORD", "")
    OPENCLAW_KEY = os.getenv("OPENCLAW_SSH_KEY", "")

    def __init__(self):
        """初始化同步器"""
        self.cloud_storage = None
        self.ssh_client = None
        self._init_cloud_storage()
        self._ensure_directories()

    def _ensure_directories(self):
        """确保目录存在"""
        os.makedirs(self.RULES_DIR, exist_ok=True)
        os.makedirs(self.KNOWLEDGE_DIR, exist_ok=True)
        os.makedirs(self.CARDS_DIR, exist_ok=True)

    def _init_ssh(self):
        """初始化 SSH 连接"""
        try:
            import paramiko
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # 使用密钥或密码连接
            if self.OPENCLAW_KEY and os.path.exists(self.OPENCLAW_KEY):
                self.ssh_client.connect(
                    self.OPENCLAW_HOST,
                    port=self.OPENCLAW_PORT,
                    username=self.OPENCLAW_USER,
                    key_filename=self.OPENCLAW_KEY
                )
            elif self.OPENCLAW_PASSWORD:
                self.ssh_client.connect(
                    self.OPENCLAW_HOST,
                    port=self.OPENCLAW_PORT,
                    username=self.OPENCLAW_USER,
                    password=self.OPENCLAW_PASSWORD
                )
            else:
                logger.warning("未配置 SSH 密钥或密码")
                return False

            logger.info(f"SSH 连接到 {self.OPENCLAW_HOST}:{self.OPENCLAW_PORT} 成功")
            return True
        except Exception as e:
            logger.warning(f"SSH 连接失败: {e}")
            return False

    def _close_ssh(self):
        """关闭 SSH 连接"""
        if self.ssh_client:
            self.ssh_client.close()
            self.ssh_client = None

    def sync_skill_to_server(self) -> Dict:
        """
        同步裁判技能到自建服务器

        同步内容：
        1. ai_judge/ 目录（345.md, cc.pem, 345-head.jpg）
        2. knowledge/ 目录（规则 + 知识图谱）

        Returns:
            同步结果
        """
        result = {
            "success": False,
            "ai_judge_files": 0,
            "knowledge_files": 0,
            "errors": []
        }

        # 连接 SSH
        if not self._init_ssh():
            result["errors"].append("SSH 连接失败")
            return result

        try:
            # 1. 同步 ai_judge/ 目录
            logger.info("开始同步 ai_judge/ 目录...")
            ai_judge_count = self._sync_directory_via_ssh(
                self.AI_JUDGE_LOCAL_DIR,
                self.OPENCLAW_SERVER_PATH
            )
            result["ai_judge_files"] = ai_judge_count
            logger.info(f"✓ ai_judge/ 同步完成: {ai_judge_count} 个文件")

            # 2. 同步 knowledge/ 目录
            logger.info("开始同步 knowledge/ 目录...")
            knowledge_path = os.path.join(
                os.path.dirname(__file__), '..', 'backend', 'data', 'knowledge'
            )
            knowledge_dest = os.path.join(self.OPENCLAW_SERVER_PATH, 'knowledge')
            knowledge_count = self._sync_directory_via_ssh(
                knowledge_path,
                knowledge_dest
            )
            result["knowledge_files"] = knowledge_count
            logger.info(f"✓ knowledge/ 同步完成: {knowledge_count} 个文件")

            result["success"] = True

        except Exception as e:
            logger.error(f"同步失败: {e}")
            result["errors"].append(str(e))
        finally:
            self._close_ssh()

        return result

    def _sync_directory_via_ssh(self, local_dir: str, remote_dir: str) -> int:
        """
        通过 SSH 同步目录到服务器

        Args:
            local_dir: 本地目录
            remote_dir: 远程目录

        Returns:
            同步的文件数量
        """
        if not os.path.exists(local_dir):
            logger.warning(f"本地目录不存在: {local_dir}")
            return 0

        synced_count = 0

        # 使用 rsync 或 scp 同步
        # 方法1: 使用 rsync (推荐)
        try:
            # 先尝试 rsync
            cmd = f'rsync -avz --delete -e "ssh -p {self.OPENCLAW_PORT}" '
            if self.OPENCLAW_KEY:
                cmd += f'-i {self.OPENCLAW_KEY} '
            cmd += f'{local_dir}/ {self.OPENCLAW_USER}@{self.OPENCLAW_HOST}:{remote_dir}/'

            logger.info(f"执行: rsync {local_dir} -> {self.OPENCLAW_USER}@{self.OPENCLAW_HOST}:{remote_dir}")
            stdin, stdout, stderr = self.ssh_client.exec_command(cmd)
            exit_status = stdout.channel.recv_exit_status()

            if exit_status == 0:
                # 统计同步的文件数
                for root, dirs, files in os.walk(local_dir):
                    synced_count += len([f for f in files if not f.startswith('.')])
                logger.info(f"rsync 同步成功")
            else:
                error = stderr.read().decode()
                logger.warning(f"rsync 失败，尝试 scp: {error}")
                raise Exception("rsync failed")
        except Exception as e:
            # 方法2: 回退到 scp
            logger.info(f"使用 scp 方式同步...")
            synced_count = self._sync_via_scp(local_dir, remote_dir)

        return synced_count

    def _sync_via_scp(self, local_dir: str, remote_dir: str) -> int:
        """通过 scp 同步目录"""
        synced_count = 0

        for root, dirs, files in os.walk(local_dir):
            # 跳过隐藏文件和目录
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            files = [f for f in files if not f.startswith('.')]

            for file in files:
                local_file = os.path.join(root, file)
                rel_path = os.path.relpath(local_file, local_dir)
                remote_file = os.path.join(remote_dir, rel_path)

                # 确保远程目录存在
                remote_subdir = os.path.dirname(remote_file)
                self.ssh_client.exec_command(f'mkdir -p {remote_subdir}')

                # 读取本地文件内容
                with open(local_file, 'rb') as f:
                    content = f.read()

                # 使用 SFTP 上传
                sftp = self.ssh_client.open_sftp()
                try:
                    with sftp.file(remote_file, 'w') as remote_file_handle:
                        remote_file_handle.write(content)
                    synced_count += 1
                    logger.info(f"  → 已同步: {rel_path}")
                except Exception as e:
                    logger.warning(f"  → 同步失败: {rel_path} - {e}")
                finally:
                    sftp.close()

        return synced_count

    def _init_cloud_storage(self):
        """初始化云存储客户端"""
        try:
            import tcbmcp
            # 尝试使用 CloudBase SDK
            self.has_cloud_storage = True
            logger.info("CloudBase SDK 可用")
        except ImportError:
            self.has_cloud_storage = False
            logger.warning("CloudBase SDK 不可用，将使用本地模式")

    async def sync_rules(self, force: bool = False) -> Dict:
        """
        同步规则数据（从 GitHub 知识库）

        Args:
            force: 是否强制同步

        Returns:
            同步结果
        """
        logger.info("=" * 50)
        logger.info("开始同步规则数据（从 GitHub 知识库）")
        logger.info(f"来源: https://github.com/{self.KNOWLEDGE_REPO}")
        logger.info("=" * 50)

        try:
            # 检查本地版本
            version_file = os.path.join(self.KNOWLEDGE_DIR, "version.json")
            local_version = None
            if os.path.exists(version_file) and not force:
                with open(version_file, 'r', encoding='utf-8') as f:
                    local_data = json.load(f)
                    local_version = local_data.get("version")

            # 获取 GitHub 最新提交来确认版本
            commit_url = f"https://api.github.com/repos/{self.KNOWLEDGE_REPO}/commits/{self.KNOWLEDGE_BRANCH}"
            response = requests.get(commit_url, timeout=30)
            if response.status_code == 200:
                commit_data = response.json()
                remote_version = commit_data.get("sha", "")[:7]
                commit_date = commit_data.get("commit", {}).get("committer", {}).get("date", "")[:10]
            else:
                remote_version = datetime.now().strftime("%Y%m%d")
                commit_date = datetime.now().strftime("%Y-%m-%d")

            if not force and local_version == remote_version:
                logger.info(f"本地已是最新版本: {local_version}")
                return {
                    "success": True,
                    "type": "rules",
                    "version": local_version,
                    "message": "已是最新"
                }

            # 下载知识库文件
            downloaded_files = []
            total_chars = 0

            for file_path in self.KNOWLEDGE_FILES:
                url = f"{self.KNOWLEDGE_BASE_URL}/{file_path}"
                local_file = os.path.join(self.KNOWLEDGE_DIR, file_path)

                logger.info(f"下载: {file_path}...")

                try:
                    response = requests.get(url, timeout=60)
                    if response.status_code == 200:
                        os.makedirs(os.path.dirname(local_file), exist_ok=True)
                        with open(local_file, 'w', encoding='utf-8') as f:
                            f.write(response.text)
                        downloaded_files.append(file_path)
                        total_chars += len(response.text)
                        logger.info(f"  ✓ 已保存: {len(response.text)} 字符")
                    else:
                        logger.warning(f"  ✗ 下载失败: {response.status_code}")
                except Exception as e:
                    logger.warning(f"  ✗ 错误: {e}")

            # 保存版本信息
            version_info = {
                "version": remote_version,
                "commit_date": commit_date,
                "sync_time": datetime.now().isoformat(),
                "source": f"https://github.com/{self.KNOWLEDGE_REPO}",
                "files": downloaded_files,
                "total_chars": total_chars
            }

            with open(version_file, 'w', encoding='utf-8') as f:
                json.dump(version_info, f, ensure_ascii=False, indent=2)

            logger.info(f"✓ 规则同步完成")
            logger.info(f"  版本: {remote_version}")
            logger.info(f"  日期: {commit_date}")
            logger.info(f"  文件: {len(downloaded_files)} 个")
            logger.info(f"  总字符: {total_chars:,}")

            return {
                "success": True,
                "type": "rules",
                "version": remote_version,
                "commit_date": commit_date,
                "data": version_info
            }

        except Exception as e:
            logger.error(f"规则同步失败: {e}", exc_info=True)
            return {
                "success": False,
                "type": "rules",
                "message": str(e)
            }

    async def sync_cards(self, force: bool = False) -> Dict:
        """
        同步卡牌数据

        Args:
            force: 是否强制同步

        Returns:
            同步结果
        """
        logger.info("=" * 50)
        logger.info("开始同步卡牌数据")
        logger.info("=" * 50)

        try:
            # 导入卡牌下载器
            from services.card_downloader import CardDownloader

            downloader = CardDownloader()

            # 下载卡牌数据
            result = await asyncio.to_thread(downloader.download_cards, force)

            if not result.get("success"):
                logger.warning(f"卡牌下载失败: {result.get('message')}")
                return result

            # 准备知识库数据
            knowledge_data = {
                "type": "cards",
                "version": result.get("version"),
                "date": result.get("date"),
                "sync_time": datetime.now().isoformat(),
                "data": result.get("data", {})
            }

            # 保存本地备份
            local_path = os.path.join(self.CARDS_DIR, "knowledge_metadata.json")
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            with open(local_path, 'w', encoding='utf-8') as f:
                json.dump(knowledge_data, f, ensure_ascii=False, indent=2)

            logger.info(f"✓ 卡牌同步完成")
            logger.info(f"  版本: {result.get('version')}")
            logger.info(f"  卡牌数: {result.get('data', {}).get('total_cards', 'N/A')}")

            return {
                "success": True,
                "type": "cards",
                "version": result.get("version"),
                "data": knowledge_data["data"]
            }

        except ImportError as e:
            logger.warning(f"卡牌下载器不可用: {e}")
            return {
                "success": False,
                "type": "cards",
                "message": "卡牌下载器未实现"
            }
        except Exception as e:
            logger.error(f"卡牌同步失败: {e}", exc_info=True)
            return {
                "success": False,
                "type": "cards",
                "message": str(e)
            }

    async def sync_all(self, force: bool = False) -> Dict:
        """
        同步所有知识库

        Args:
            force: 是否强制同步

        Returns:
            同步结果汇总
        """
        logger.info("=" * 50)
        logger.info("开始同步 AI 裁判知识库")
        logger.info(f"强制模式: {force}")
        logger.info("=" * 50)

        results = {
            "success": True,
            "sync_time": datetime.now().isoformat(),
            "items": []
        }

        # 同步规则
        rules_result = await self.sync_rules(force)
        results["items"].append(rules_result)
        results["success"] = results["success"] and rules_result.get("success", False)

        # 同步卡牌
        cards_result = await self.sync_cards(force)
        results["items"].append(cards_result)
        results["success"] = results["success"] and cards_result.get("success", False)

        # 总结
        logger.info("=" * 50)
        logger.info("知识库同步完成")
        logger.info(f"总状态: {'成功' if results['success'] else '部分失败'}")

        success_count = sum(1 for r in results["items"] if r.get("success"))
        logger.info(f"成功: {success_count}/{len(results['items'])}")

        return results

    async def _upload_to_cloud(self, path: str, data: dict):
        """上传到云存储"""
        try:
            # 这里应该使用 CloudBase SDK 上传
            # 暂时跳过，因为需要在云函数环境中才能使用
            logger.info(f"  [云存储] 准备上传: {path}")
        except Exception as e:
            logger.warning(f"云存储上传失败: {e}")

    def get_sync_status(self) -> Dict:
        """
        获取同步状态

        Returns:
            状态信息
        """
        status = {
            "last_sync": None,
            "rules_version": None,
            "cards_version": None,
            "rules_count": 0,
            "cards_count": 0
        }

        # 读取本地状态
        rules_metadata = os.path.join(self.RULES_DIR, "knowledge_metadata.json")
        if os.path.exists(rules_metadata):
            with open(rules_metadata, 'r', encoding='utf-8') as f:
                data = json.load(f)
                status["last_sync"] = data.get("sync_time")
                status["rules_version"] = data.get("version")
                status["rules_count"] = data.get("data", {}).get("rules_count", 0)

        cards_metadata = os.path.join(self.CARDS_DIR, "knowledge_metadata.json")
        if os.path.exists(cards_metadata):
            with open(cards_metadata, 'r', encoding='utf-8') as f:
                data = json.load(f)
                status["last_sync"] = data.get("sync_time")
                status["cards_version"] = data.get("version")
                status["cards_count"] = data.get("data", {}).get("total_cards", 0)

        return status


def run_schedule():
    """运行定时同步任务"""
    import schedule
    import time

    sync = KnowledgeSync()

    # 每天凌晨 4 点同步
    schedule.every().day.at("04:00").do(
        lambda: asyncio.run(sync.sync_all())
    )

    # 每周一凌晨 5 点全面检查
    schedule.every().monday.at("05:00").do(
        lambda: asyncio.run(sync.sync_all(force=True))
    )

    logger.info("定时同步任务已启动")
    logger.info("  - 每天 04:00: 同步知识库")
    logger.info("  - 每周一 05:00: 全面检查")

    while True:
        schedule.run_pending()
        time.sleep(60)


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="AI 裁判知识库同步工具")
    parser.add_argument("--rules", action="store_true", help="仅同步规则")
    parser.add_argument("--cards", action="store_true", help="仅同步卡牌")
    parser.add_argument("--skill", action="store_true", help="同步裁判技能到服务器")
    parser.add_argument("--force", action="store_true", help="强制同步（忽略版本检查）")
    parser.add_argument("--schedule", action="store_true", help="启动定时任务")
    parser.add_argument("--status", action="store_true", help="查看同步状态")

    args = parser.parse_args()

    sync = KnowledgeSync()

    if args.schedule:
        run_schedule()
        return

    if args.status:
        status = sync.get_sync_status()
        print("\n=== 知识库同步状态 ===")
        print(f"最后同步: {status['last_sync'] or '从未同步'}")
        print(f"规则版本: {status['rules_version'] or '未同步'}")
        print(f"规则数量: {status['rules_count']}")
        print(f"卡牌版本: {status['cards_version'] or '未同步'}")
        print(f"卡牌数量: {status['cards_count']}")
        return

    # 执行同步
    if args.skill:
        # 同步裁判技能到服务器（SSH）
        result = sync.sync_skill_to_server()
        print("\n=== 同步结果 ===")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return
    elif args.rules:
        result = await sync.sync_rules(args.force)
    elif args.cards:
        result = await sync.sync_cards(args.force)
    else:
        result = await sync.sync_all(args.force)

    # 输出结果
    print("\n=== 同步结果 ===")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
