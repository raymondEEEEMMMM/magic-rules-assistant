import sqlite3
import json
import os
from typing import List, Dict, Optional
from config import Config

class RuleDatabase:
    def __init__(self, db_path: str = None):
        # 优先使用传入的路径，然后尝试环境变量，最后使用默认配置
        if db_path is None:
            db_path = os.environ.get('DATABASE_PATH') or Config.DATABASE_PATH
        self.db_path = db_path
        self._init_database()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_database(self):
        """初始化数据库表结构"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # 创建规则表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rule_number TEXT UNIQUE NOT NULL,
            rule_title TEXT NOT NULL,
            rule_content TEXT NOT NULL,
            category TEXT,
            keywords TEXT
        )
        """)

        # 创建关键词异能表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS keyword_abilities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            keyword_name TEXT UNIQUE NOT NULL,
            description TEXT NOT NULL,
            full_text TEXT NOT NULL,
            examples TEXT
        )
        """)

        # 创建卡牌规则表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS card_rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            card_name TEXT UNIQUE NOT NULL,
            card_type TEXT,
            oracle_text TEXT NOT NULL,
            related_rules TEXT
        )
        """)

        # 创建问答模板表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS qa_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            keywords TEXT,
            category TEXT
        )
        """)

        conn.commit()
        conn.close()

    def insert_rule(self, rule_number: str, rule_title: str, rule_content: str,
                   category: str = None, keywords: List[str] = None):
        """插入规则"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
            INSERT INTO rules (rule_number, rule_title, rule_content, category, keywords)
            VALUES (?, ?, ?, ?, ?)
            """, (rule_number, rule_title, rule_content, category,
                  json.dumps(keywords) if keywords else None))
            conn.commit()
        except sqlite3.IntegrityError:
            pass  # 规则已存在
        finally:
            conn.close()

    def insert_keyword_ability(self, keyword_name: str, description: str,
                              full_text: str, examples: List[str] = None):
        """插入关键词异能"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
            INSERT INTO keyword_abilities (keyword_name, description, full_text, examples)
            VALUES (?, ?, ?, ?)
            """, (keyword_name, description, full_text,
                  json.dumps(examples) if examples else None))
            conn.commit()
        except sqlite3.IntegrityError:
            pass
        finally:
            conn.close()

    def insert_card_rule(self, card_name: str, card_type: str,
                        oracle_text: str, related_rules: List[str] = None):
        """插入卡牌规则"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
            INSERT INTO card_rules (card_name, card_type, oracle_text, related_rules)
            VALUES (?, ?, ?, ?)
            """, (card_name, card_type, oracle_text,
                  json.dumps(related_rules) if related_rules else None))
            conn.commit()
        except sqlite3.IntegrityError:
            pass
        finally:
            conn.close()

    def insert_qa_template(self, question: str, answer: str,
                         keywords: List[str] = None, category: str = None):
        """插入问答模板"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
            INSERT INTO qa_templates (question, answer, keywords, category)
            VALUES (?, ?, ?, ?)
            """, (question, answer,
                  json.dumps(keywords) if keywords else None, category))
            conn.commit()
        except sqlite3.IntegrityError:
            pass
        finally:
            conn.close()

    def search_by_keywords(self, keywords: List[str]) -> List[Dict]:
        """根据关键词搜索规则"""
        conn = self._get_connection()
        cursor = conn.cursor()

        results = []
        for keyword in keywords:
            cursor.execute("""
            SELECT rule_number, rule_title, rule_content, category
            FROM rules WHERE rule_content LIKE ? OR rule_title LIKE ? OR keywords LIKE ?
            LIMIT 10
            """, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"))

            rows = cursor.fetchall()
            for row in rows:
                results.append({
                    "rule_number": row[0],
                    "rule_title": row[1],
                    "rule_content": row[2],
                    "category": row[3]
                })

        conn.close()
        return results

    def get_keyword_ability(self, keyword_name: str) -> Optional[Dict]:
        """获取关键词异能"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
        SELECT keyword_name, description, full_text, examples
        FROM keyword_abilities WHERE keyword_name LIKE ?
        """, (f"%{keyword_name}%",))

        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                "keyword_name": row[0],
                "description": row[1],
                "full_text": row[2],
                "examples": json.loads(row[3]) if row[3] else None
            }
        return None

    def get_card_rule(self, card_name: str) -> Optional[Dict]:
        """获取卡牌规则"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
        SELECT card_name, card_type, oracle_text, related_rules
        FROM card_rules WHERE card_name LIKE ?
        """, (f"%{card_name}%",))

        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                "card_name": row[0],
                "card_type": row[1],
                "oracle_text": row[2],
                "related_rules": json.loads(row[3]) if row[3] else None
            }
        return None

    def search_qa_templates(self, keywords: List[str]) -> List[Dict]:
        """搜索问答模板"""
        conn = self._get_connection()
        cursor = conn.cursor()

        results = []
        for keyword in keywords:
            cursor.execute("""
            SELECT question, answer, category
            FROM qa_templates WHERE question LIKE ? OR answer LIKE ? OR keywords LIKE ?
            LIMIT 5
            """, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"))

            rows = cursor.fetchall()
            for row in rows:
                results.append({
                    "question": row[0],
                    "answer": row[1],
                    "category": row[2]
                })

        conn.close()
        return results
