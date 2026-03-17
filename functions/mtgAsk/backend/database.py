#!/usr/bin/env python3
"""
CloudBase MySQL 数据库访问层
区分本地调试和云端服务的连接方式
"""
import os
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

    def search_by_keywords(self, keywords: List[str]) -> List[Dict]:
        """根据关键词搜索规则"""
        all_results = []
        seen = set()  # 去重
        
        for keyword in keywords:
            # 使用 LIKE 查询
            escaped_keyword = keyword.replace('%', '\\%').replace("'", "\\'")
            
            sql = f"SELECT rule_number, rule_title, rule_content, category FROM rules WHERE rule_content LIKE '%{escaped_keyword}%' OR rule_title LIKE '%{escaped_keyword}%' LIMIT 10"
            results = self._execute_read_sql(sql)
            
            for result in results:
                # 使用规则号去重
                rule_key = result.get('rule_number')
                if rule_key and rule_key not in seen:
                    all_results.append(result)
                    seen.add(rule_key)
        
        return all_results
    
    def get_keyword_ability(self, keyword_name: str) -> Optional[Dict]:
        """获取关键词异能"""
        escaped_keyword = keyword_name.replace('%', '\\%').replace("'", "\\'")
        sql = f"SELECT keyword_name, description, full_text FROM keyword_abilities WHERE keyword_name LIKE '%{escaped_keyword}%' LIMIT 1"
        results = self._execute_read_sql(sql)
        return results[0] if results else None
    
    def get_card_rule(self, card_name: str) -> Optional[Dict]:
        """获取卡牌规则（当前MySQL中暂无此表，返回空）"""
        return None
    
    def search_qa_templates(self, keywords: List[str]) -> List[Dict]:
        """搜索问答模板（当前MySQL中暂无此表，返回空）"""
        return []
