#!/usr/bin/env python3
"""
CloudBase MySQL 数据库访问层
区分本地调试和云端服务的连接方式
"""
import os
import re
import json
from typing import List, Dict, Optional

class RuleDatabase:
    """规则数据库访问类 - CloudBase MySQL 版本"""
    
    def __init__(self):
        self.db_type = 'mysql'
        self.env_id = os.environ.get('TCB_ENV_ID', 'magic-rules-assistant-0a1904c329')
        
        # 本地调试时加载 .env.local
        if not self._is_cloud_function():
            self._load_local_env()
        
        # 检测运行环境
        self.is_cloud_function = self._is_cloud_function()
        print(f"RuleDatabase initialized for env: {self.env_id}, is_cloud_function: {self.is_cloud_function}")
        
        # 根据环境选择连接配置
        if self.is_cloud_function:
            # 云端环境：使用内网地址
            self.mysql_host = os.environ.get('MYSQL_HOST', '172.17.0.5')
            self.mysql_port = int(os.environ.get('MYSQL_PORT', '3306'))
        else:
            # 本地调试：使用外网地址
            self.mysql_host = os.environ.get('MYSQL_HOST', 'sh-cynosdbmysql-grp-5ydpqjru.sql.tencentcdb.com')
            self.mysql_port = int(os.environ.get('MYSQL_PORT', '27987'))
        
        self.mysql_user = os.environ.get('MYSQL_USER', 'mtgask')
        self.mysql_password = os.environ.get('MYSQL_PASSWORD', 'Ray19940211')
        self.mysql_database = os.environ.get('MYSQL_DATABASE', f"{self.env_id}")
        
        print(f"MySQL config: host={self.mysql_host}, port={self.mysql_port}, user={self.mysql_user}, db={self.mysql_database}")
        print(f"Password configured: {'Yes' if self.mysql_password else 'No'}")
    
    def _load_local_env(self):
        """加载本地 .env.local 文件"""
        env_file = os.path.join(os.path.dirname(__file__), '.env.local')
        if os.path.exists(env_file):
            print(f"Loading local environment from: {env_file}")
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
                        print(f"  Loaded: {key.strip()}")
    
    def _is_cloud_function(self) -> bool:
        """
        检测是否在云函数环境中运行
        """
        # 云函数环境检测方法
        cloud_env_indicators = [
            'SCF_FUNCTION_NAME',  # 腾讯云云函数
            'TENCENTCLOUD_RUNENV',  # 腾讯云运行环境
            'FC_REQUEST_ID',  # 阿里云函数计算
            'AWS_LAMBDA_FUNCTION_VERSION',  # AWS Lambda
        ]
        
        for indicator in cloud_env_indicators:
            if os.environ.get(indicator):
                return True
        
        return False
    
    def _execute_read_sql(self, sql: str) -> List[Dict]:
        """
        执行只读 SQL 查询
        使用 pymysql 连接数据库
        """
        try:
            import pymysql
            
            # 如果没有配置密码，返回空结果
            if not self.mysql_password:
                print("Warning: MySQL password not configured")
                return []
            
            conn = pymysql.connect(
                host=self.mysql_host,
                port=self.mysql_port,
                user=self.mysql_user,
                password=self.mysql_password,
                database=self.mysql_database,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor,
                connect_timeout=10
            )
            
            try:
                with conn.cursor() as cursor:
                    cursor.execute(sql)
                    results = cursor.fetchall()
                    return results
            finally:
                conn.close()
        except ImportError:
            print("Warning: pymysql not installed")
            return []
        except Exception as e:
            print(f"Database query error: {e}")
            import traceback
            traceback.print_exc()
            return []

    def _execute_write_sql(self, sql: str, params: tuple = None) -> bool:
        """
        执行写操作 SQL（INSERT, UPDATE, DELETE）
        """
        try:
            import pymysql

            # 如果没有配置密码，返回失败
            if not self.mysql_password:
                print("Warning: MySQL password not configured")
                return False

            conn = pymysql.connect(
                host=self.mysql_host,
                port=self.mysql_port,
                user=self.mysql_user,
                password=self.mysql_password,
                database=self.mysql_database,
                charset='utf8mb4',
                connect_timeout=10
            )

            try:
                with conn.cursor() as cursor:
                    if params:
                        cursor.execute(sql, params)
                    else:
                        cursor.execute(sql)
                    conn.commit()
                    return True
            finally:
                conn.close()
        except ImportError:
            print("Warning: pymysql not installed")
            return False
        except Exception as e:
            print(f"Database write error: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _format_rule_content(self, content: str, max_length: int = 300) -> str:
        """格式化规则内容：去除HTML标签，限制长度"""
        if not content:
            return ""

        # 去除 HTML 标签
        content = re.sub(r'<[^>]+>', '', content)
        # 清理多余空白
        content = re.sub(r'\s+', ' ', content).strip()

        # 限制长度
        if len(content) > max_length:
            content = content[:max_length] + "..."

        return content

    def search_by_keywords(self, keywords: List[str]) -> List[Dict]:
        """根据关键词搜索规则 - 使用 rules_v2 表"""
        all_results = []
        seen = set()  # 去重

        # 检测语言
        is_chinese = any(bool(re.search(r'[\u4e00-\u9fff]', k)) for k in keywords)

        for keyword in keywords:
            # 使用 LIKE 查询
            escaped_keyword = keyword.replace('%', '\\%').replace("'", "\\'")

            # 根据语言选择搜索字段
            if is_chinese:
                sql = f"""SELECT rule_number, rule_title_cn as rule_title, rule_content_cn as rule_content,
                    category, rule_title_en, rule_content_en
                    FROM rules_v2
                    WHERE rule_content_cn LIKE '%{escaped_keyword}%'
                       OR rule_title_cn LIKE '%{escaped_keyword}%'
                    LIMIT 10"""
            else:
                sql = f"""SELECT rule_number, rule_title_en as rule_title, rule_content_en as rule_content,
                    category, rule_title_cn, rule_content_cn
                    FROM rules_v2
                    WHERE rule_content_en LIKE '%{escaped_keyword}%'
                       OR rule_title_en LIKE '%{escaped_keyword}%'
                    LIMIT 10"""

            results = self._execute_read_sql(sql)

            for result in results:
                # 使用规则号去重
                rule_key = result.get('rule_number')
                if rule_key and rule_key not in seen:
                    # 格式化内容
                    formatted_result = {
                        'rule_number': result.get('rule_number'),
                        'rule_title': result.get('rule_title', ''),
                        'rule_content': self._format_rule_content(result.get('rule_content', '')),
                        'category': result.get('category'),
                    }
                    # 添加另一种语言的内容（可选）
                    if is_chinese and result.get('rule_title_en'):
                        formatted_result['rule_title_en'] = result.get('rule_title_en')
                    elif not is_chinese and result.get('rule_title_cn'):
                        formatted_result['rule_title_cn'] = result.get('rule_title_cn')

                    all_results.append(formatted_result)
                    seen.add(rule_key)

        return all_results
    
    def get_keyword_ability(self, keyword_name: str) -> Optional[Dict]:
        """获取关键词异能 - 使用 keyword_abilities_v2 表"""
        escaped_keyword = keyword_name.replace('%', '\\%').replace("'", "\\'")

        # 尝试通过中文名或英文名匹配
        sql = f"""SELECT
            keyword_cn, keyword_en,
            description_cn, description_en,
            rule_ref_cn, rule_ref_en
        FROM keyword_abilities_v2
        WHERE keyword_cn LIKE '%{escaped_keyword}%'
           OR keyword_en LIKE '%{escaped_keyword}%'
        LIMIT 1"""

        results = self._execute_read_sql(sql)
        if not results:
            return None

        record = results[0]

        # 检测输入是中文还是英文，返回对应语言的数据
        is_chinese = bool(re.search(r'[\u4e00-\u9fff]', keyword_name))

        # 格式化描述（去除HTML标签）
        desc_cn = self._format_rule_content(record['description_cn'] or '', max_length=500)
        desc_en = self._format_rule_content(record['description_en'] or '', max_length=500)

        if is_chinese:
            return {
                "keyword_name": record['keyword_cn'],
                "description": desc_cn,
                "full_text": record['rule_ref_cn'],
                "keyword_en": record['keyword_en'],
                "description_en": desc_en,
                "rule_ref_en": record['rule_ref_en']
            }
        else:
            return {
                "keyword_name": record['keyword_en'],
                "description": desc_en,
                "full_text": record['rule_ref_en'],
                "keyword_cn": record['keyword_cn'],
                "description_cn": desc_cn,
                "rule_ref_cn": record['rule_ref_cn']
            }
    
    def get_rule_by_number(self, rule_number: str) -> Optional[Dict]:
        """根据规则编号获取完整规则内容"""
        escaped = rule_number.replace('%', '\\%').replace("'", "\\'")

        # 先尝试精确匹配
        sql = f"""SELECT
            rule_number, rule_title_cn, rule_title_en,
            rule_content_cn, rule_content_en, category
            FROM rules_v2
            WHERE rule_number = '{escaped}'
            LIMIT 1"""

        results = self._execute_read_sql(sql)
        if results:
            record = results[0]
            return {
                'rule_number': record['rule_number'],
                'rule_title_cn': record['rule_title_cn'],
                'rule_title_en': record['rule_title_en'],
                'rule_content_cn': record['rule_content_cn'],
                'rule_content_en': record['rule_content_en'],
                'category': record['category']
            }

        # 如果没找到，尝试模糊匹配（如 702.9 匹配 702.9, 702.9a 等）
        sql = f"""SELECT
            rule_number, rule_title_cn, rule_title_en,
            rule_content_cn, rule_content_en, category
            FROM rules_v2
            WHERE rule_number LIKE '{escaped}%'
            LIMIT 1"""

        results = self._execute_read_sql(sql)
        if not results:
            return None

        record = results[0]
        return {
            'rule_number': record['rule_number'],
            'rule_title_cn': record['rule_title_cn'],
            'rule_title_en': record['rule_title_en'],
            'rule_content_cn': record['rule_content_cn'],
            'rule_content_en': record['rule_content_en'],
            'category': record['category']
        }

    def get_card_rule(self, card_name: str) -> Optional[Dict]:
        """获取卡牌规则（当前MySQL中暂无此表，返回空）"""
        return None
    
    def search_qa_templates(self, keywords: List[str]) -> List[Dict]:
        """搜索问答模板（当前MySQL中暂无此表，返回空）"""
        return []

    # ==================== AI Agent Pool 管理 ====================

    def ensure_agent_pool_table(self) -> bool:
        """确保 ai_agent_pool 表存在"""
        sql = """CREATE TABLE IF NOT EXISTS ai_agent_pool (
            id              INT AUTO_INCREMENT PRIMARY KEY,
            openid          VARCHAR(128) UNIQUE NOT NULL COMMENT '微信 openid',
            agent_name      VARCHAR(128) NOT NULL COMMENT 'OpenCLAW Agent 名称',
            created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            last_used_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            is_idle         BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否标记为可回收',
            idle_since      DATETIME NULL COMMENT '开始空闲时间',
            message_count   INT UNSIGNED NOT NULL DEFAULT 0,
            INDEX idx_openid (openid),
            INDEX idx_last_used (last_used_at),
            INDEX idx_is_idle (is_idle)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""
        return self._execute_write_sql(sql)

    def get_agent_by_openid(self, openid: str) -> Optional[Dict]:
        """根据 openid 获取绑定的 Agent 信息"""
        sql = "SELECT * FROM ai_agent_pool WHERE openid = %s LIMIT 1"
        results = self._execute_read_sql_with_params(sql, (openid,))
        return results[0] if results else None

    def create_agent(self, openid: str, agent_name: str) -> bool:
        """创建新的 Agent 绑定"""
        sql = "INSERT INTO ai_agent_pool (openid, agent_name) VALUES (%s, %s)"
        return self._execute_write_sql_with_params(sql, (openid, agent_name))

    def update_agent_last_used(self, openid: str) -> bool:
        """更新 Agent 最后使用时间"""
        sql = """UPDATE ai_agent_pool
                 SET last_used_at = NOW(), is_idle = FALSE, idle_since = NULL, message_count = message_count + 1
                 WHERE openid = %s"""
        return self._execute_write_sql_with_params(sql, (openid,))

    def mark_agent_idle(self, openid: str) -> bool:
        """标记 Agent 为空闲"""
        sql = """UPDATE ai_agent_pool
                 SET is_idle = TRUE, idle_since = NOW()
                 WHERE openid = %s"""
        return self._execute_write_sql_with_params(sql, (openid,))

    def get_active_agent_count(self) -> int:
        """获取当前活跃 Agent 数量"""
        sql = "SELECT COUNT(*) as count FROM ai_agent_pool WHERE is_idle = FALSE"
        results = self._execute_read_sql_with_params(sql, None)
        return results[0]['count'] if results else 0

    def get_idle_agents_older_than(self, minutes: int) -> List[Dict]:
        """获取空闲时间超过指定分钟的 Agent"""
        sql = """SELECT * FROM ai_agent_pool
                 WHERE is_idle = TRUE AND idle_since IS NOT NULL
                 AND TIMESTAMPDIFF(MINUTE, idle_since, NOW()) >= %s
                 ORDER BY idle_since ASC"""
        return self._execute_read_sql_with_params(sql, (minutes,))

    def delete_agent_by_openid(self, openid: str) -> bool:
        """删除 Agent 绑定"""
        sql = "DELETE FROM ai_agent_pool WHERE openid = %s"
        return self._execute_write_sql_with_params(sql, (openid,))

    def get_lru_agent(self, exclude_openids: List[str] = None) -> Optional[Dict]:
        """获取最久未使用的 Agent（用于 LRU 回收）"""
        if exclude_openids:
            placeholders = ','.join(['%s'] * len(exclude_openids))
            sql = f"""SELECT * FROM ai_agent_pool
                     WHERE openid NOT IN ({placeholders})
                     ORDER BY last_used_at ASC LIMIT 1"""
            results = self._execute_read_sql_with_params(sql, tuple(exclude_openids))
        else:
            sql = "SELECT * FROM ai_agent_pool ORDER BY last_used_at ASC LIMIT 1"
            results = self._execute_read_sql_with_params(sql, None)
        return results[0] if results else None

    def _execute_read_sql_with_params(self, sql: str, params: tuple) -> List[Dict]:
        """执行带参数的只读 SQL 查询"""
        try:
            import pymysql

            if not self.mysql_password:
                return []

            conn = pymysql.connect(
                host=self.mysql_host,
                port=self.mysql_port,
                user=self.mysql_user,
                password=self.mysql_password,
                database=self.mysql_database,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor,
                connect_timeout=10
            )

            try:
                with conn.cursor() as cursor:
                    cursor.execute(sql, params)
                    return cursor.fetchall()
            finally:
                conn.close()
        except Exception as e:
            print(f"Database query error: {e}")
            return []

    def _execute_write_sql_with_params(self, sql: str, params: tuple) -> bool:
        """执行带参数的写操作 SQL"""
        try:
            import pymysql

            if not self.mysql_password:
                return False

            conn = pymysql.connect(
                host=self.mysql_host,
                port=self.mysql_port,
                user=self.mysql_user,
                password=self.mysql_password,
                database=self.mysql_database,
                charset='utf8mb4',
                connect_timeout=10
            )

            try:
                with conn.cursor() as cursor:
                    cursor.execute(sql, params)
                    conn.commit()
                    return True
            finally:
                conn.close()
        except Exception as e:
            print(f"Database write error: {e}")
            return False
