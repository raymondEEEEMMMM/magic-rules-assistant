"""
定时任务调度器
用于定时下载和更新万智牌规则
"""
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from typing import Optional, Callable
import asyncio

from .rule_downloader import RuleDownloader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RuleScheduler:
    """规则定时任务调度器"""

    def __init__(self):
        """初始化调度器"""
        self.scheduler = AsyncIOScheduler()
        self.downloader = RuleDownloader()
        self.update_callback: Optional[Callable] = None

    def start(self):
        """启动调度器"""
        logger.info("启动规则更新调度器...")

        # 添加定时任务：每天凌晨3点检查更新
        self.scheduler.add_job(
            self._scheduled_update,
            CronTrigger(hour=3, minute=0),
            id='rules_update',
            name='定时更新万智牌规则',
            replace_existing=True
        )

        # 添加每周一上午10点的全面检查
        self.scheduler.add_job(
            self._scheduled_full_check,
            CronTrigger(day_of_week='mon', hour=10, minute=0),
            id='rules_full_check',
            name='每周全面检查规则',
            replace_existing=True
        )

        self.scheduler.start()
        logger.info("调度器启动成功")
        logger.info("已添加定时任务:")
        logger.info("  - 每天03:00: 检查规则更新")
        logger.info("  - 每周一10:00: 全面检查规则")

    def stop(self):
        """停止调度器"""
        logger.info("停止调度器...")
        self.scheduler.shutdown()
        logger.info("调度器已停止")

    def set_update_callback(self, callback: Callable):
        """设置更新回调函数"""
        self.update_callback = callback

    async def _scheduled_update(self):
        """定时更新任务"""
        logger.info("=" * 50)
        logger.info("执行定时规则更新任务")
        logger.info(f"时间: {datetime.now()}")
        logger.info("=" * 50)

        try:
            # 下载规则
            result = self.downloader.download_rules()

            if result["success"]:
                logger.info(f"✓ 规则更新成功")
                logger.info(f"  版本: {result.get('version')}")
                logger.info(f"  日期: {result.get('date')}")

                # 调用回调函数
                if self.update_callback:
                    await self.update_callback(result)
            else:
                logger.warning(f"✗ 规则更新失败: {result.get('message')}")

        except Exception as e:
            logger.error(f"定时任务执行失败: {e}", exc_info=True)

    async def _scheduled_full_check(self):
        """全面检查任务"""
        logger.info("=" * 50)
        logger.info("执行每周全面规则检查")
        logger.info(f"时间: {datetime.now()}")
        logger.info("=" * 50)

        try:
            # 强制下载最新规则
            result = self.downloader.download_rules(force=True)

            if result["success"]:
                logger.info(f"✓ 全面检查完成")

                # 解析规则
                parse_result = self.downloader.parse_rules()
                if parse_result["success"]:
                    logger.info(f"  规则条目: {len(parse_result['rules'])}")
                    logger.info(f"  关键词异能: {len(parse_result['keyword_abilities'])}")
                    logger.info(f"  术语表: {len(parse_result['glossary'])}")

                # 调用回调函数
                if self.update_callback:
                    await self.update_callback(result)
            else:
                logger.warning(f"✗ 全面检查失败: {result.get('message')}")

        except Exception as e:
            logger.error(f"全面检查执行失败: {e}", exc_info=True)

    async def update_now(self) -> dict:
        """立即执行更新"""
        logger.info("手动触发规则更新...")
        try:
            # 在同步环境中运行
            result = await asyncio.to_thread(self.downloader.download_rules)
            return result
        except Exception as e:
            logger.error(f"手动更新失败: {e}")
            return {
                "success": False,
                "message": f"更新失败: {str(e)}"
            }

    def get_jobs(self) -> list:
        """获取所有任务信息"""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run_time": job.next_run_time.strftime("%Y-%m-%d %H:%M:%S") if job.next_run_time else None
            })
        return jobs

    def get_status(self) -> dict:
        """获取调度器状态"""
        return {
            "running": self.scheduler.running,
            "jobs_count": len(self.scheduler.get_jobs()),
            "jobs": self.get_jobs()
        }


# 全局调度器实例
rule_scheduler = RuleScheduler()


async def on_rules_update(result: dict):
    """
    规则更新时的回调函数示例

    Args:
        result: 更新结果
    """
    logger.info("规则更新回调被触发")
    logger.info(f"更新结果: {result}")

    # 这里可以添加更新后的处理逻辑
    # 例如：重新解析规则、更新向量数据库、发送通知等

    # 示例：如果规则有更新，重新解析
    if result.get("success") and result.get("file_path"):
        try:
            downloader = RuleDownloader()
            parse_result = await asyncio.to_thread(downloader.parse_rules)

            if parse_result["success"]:
                logger.info("规则重新解析完成")
                # 可以在这里更新数据库
        except Exception as e:
            logger.error(f"重新解析规则失败: {e}")


if __name__ == "__main__":
    # 测试调度器
    import asyncio

    async def test():
        scheduler = RuleScheduler()
        scheduler.set_update_callback(on_rules_update)

        # 启动调度器
        scheduler.start()

        # 显示任务信息
        print("\n当前任务:")
        for job in scheduler.get_jobs():
            print(f"  - {job['name']}: 下次运行 {job['next_run_time']}")

        # 手动触发一次更新
        print("\n手动触发更新...")
        result = await scheduler.update_now()
        print(f"更新结果: {result}")

        # 保持运行一段时间
        print("\n调度器运行中... (Ctrl+C 停止)")
        try:
            await asyncio.sleep(30)  # 运行30秒
        except KeyboardInterrupt:
            pass

        scheduler.stop()
        print("\n调度器已停止")

    asyncio.run(test())
