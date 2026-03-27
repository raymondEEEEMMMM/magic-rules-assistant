"""
日志服务 - 统一日志记录，支持本地存储和 MySQL 数据库
"""
import os
import json
from datetime import datetime
from typing import Any, Dict, Optional


class LogService:
    """日志服务类"""

    def __init__(self):
        self.is_cloud = bool(os.getenv("SCF_FUNCTION_NAME") or os.getenv("TENCENTCLOUD_RUNENV"))
        self._db = None

    def _get_db(self):
        """获取数据库连接"""
        if self._db is not None:
            return self._db

        try:
            from backend.database import RuleDatabase
            self._db = RuleDatabase()
            return self._db
        except Exception as e:
            print(f"[LogService] 数据库连接失败: {e}")
            return None

    def _ensure_log_table(self) -> bool:
        """确保日志表存在"""
        db = self._get_db()
        if not db:
            return False

        try:
            # 创建日志表（如果不存在）
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS ai_judge_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                service VARCHAR(50) NOT NULL,
                level VARCHAR(20) NOT NULL,
                message TEXT,
                data JSON,
                INDEX idx_service (service),
                INDEX idx_level (level),
                INDEX idx_timestamp (timestamp)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """
            return db._execute_write_sql(create_table_sql)
        except Exception as e:
            print(f"[LogService] 创建日志表失败: {e}")
            return False

    def _get_local_log_path(self) -> str:
        """获取本地日志目录路径"""
        # 本地环境：项目根目录/logs
        # 云函数环境：/tmp/logs（可写临时目录）
        if self.is_cloud:
            log_dir = "/tmp/logs"
        else:
            # 项目根目录
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            log_dir = os.path.join(project_root, "logs")

        if not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        return log_dir

    def _save_to_local(self, log_data: Dict[str, Any]) -> bool:
        """保存日志到本地文件"""
        try:
            log_dir = self._get_local_log_path()
            date_str = datetime.now().strftime('%Y%m%d')
            log_file = os.path.join(log_dir, f"ai_judge_{date_str}.log")

            # 格式化日志内容
            log_line = json.dumps(log_data, ensure_ascii=False)

            # 追加写入
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(log_line + '\n')

            return True
        except Exception as e:
            print(f"[LogService] 本地日志保存失败: {e}")
            return False

    def _save_to_database(self, log_data: Dict[str, Any]) -> bool:
        """保存日志到 MySQL 数据库"""
        db = self._get_db()
        if not db:
            return False

        try:
            # 确保日志表存在
            self._ensure_log_table()

            # 插入日志记录
            insert_sql = """
            INSERT INTO ai_judge_logs (service, level, message, data)
            VALUES (%s, %s, %s, %s)
            """
            success = db._execute_write_sql(insert_sql, (
                log_data['service'],
                log_data['level'],
                log_data['message'],
                json.dumps(log_data.get('data', {}), ensure_ascii=False)
            ))

            if success:
                print(f"[LogService] 数据库日志已保存")
            return success
        except Exception as e:
            print(f"[LogService] 数据库日志保存失败: {e}")
            return False

    def log(self,
            service: str,
            level: str,
            message: str,
            data: Optional[Dict[str, Any]] = None,
            save_local: bool = True,
            save_database: bool = True) -> bool:
        """
        记录日志

        Args:
            service: 服务名称（如 'ai_judge', 'card_service'）
            level: 日志级别（info, warning, error, debug）
            message: 日志消息
            data: 额外的日志数据
            save_local: 是否保存到本地文件
            save_database: 是否保存到数据库

        Returns:
            bool: 是否保存成功
        """
        # 构建日志数据
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "service": service,
            "level": level,
            "message": message,
            "data": data or {}
        }

        # 打印到控制台（云函数会收集 stdout）
        print(f"[{service.upper()}] {level.upper()}: {message}")

        success = True

        # 本地文件存储
        if save_local:
            success = self._save_to_local(log_data) and success

        # 数据库存储
        if save_database:
            success = self._save_to_database(log_data) and success

        return success


# 全局日志服务实例
log_service = LogService()


# 便捷函数
def log_info(service: str, message: str, data: Dict = None):
    """记录 info 级别日志"""
    return log_service.log(service, "info", message, data)


def log_warning(service: str, message: str, data: Dict = None):
    """记录 warning 级别日志"""
    return log_service.log(service, "warning", message, data)


def log_error(service: str, message: str, data: Dict = None):
    """记录 error 级别日志"""
    return log_service.log(service, "error", message, data)


def log_debug(service: str, message: str, data: Dict = None):
    """记录 debug 级别日志"""
    return log_service.log(service, "debug", message, data)
