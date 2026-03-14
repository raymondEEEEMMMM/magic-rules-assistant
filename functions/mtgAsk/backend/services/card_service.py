"""
MTG 卡牌查询服务

封装 MTGJSON SQLite 数据库的查询功能，提供统一的卡牌查询接口。
"""

import sqlite3
import json
from typing import List, Dict, Optional
import os


class CardService:
    """MTG 卡牌查询服务"""

    def __init__(self, db_path: str = None):
        """
        初始化卡牌服务

        Args:
            db_path: MTGSQLite 数据库路径。如果为 None，则尝试自动查找。
        """
        self.db_path = db_path
        self.connection = None

    def _get_db_path(self) -> Optional[str]:
        """
        获取数据库路径

        Returns:
            数据库路径，如果找不到则返回 None
        """
        if self.db_path:
            return self.db_path

        # 尝试自动查找
        possible_paths = [
            # 从当前脚本位置向上查找
            os.path.join(os.path.dirname(__file__), "../data/mtg/AllPrintings.sqlite"),
            # 从当前工作目录
            "data/mtg/AllPrintings.sqlite",
            # 从项目根目录
            "../data/mtg/AllPrintings.sqlite",
            # 绝对路径
            "/Users/lianghaoming/cbworkplace/data/mtg/AllPrintings.sqlite",
        ]

        for path in possible_paths:
            abs_path = os.path.abspath(path)
            if os.path.exists(abs_path):
                self.db_path = abs_path
                return abs_path

        return None

    def _get_connection(self):
        """获取数据库连接"""
        if self.connection:
            return self.connection

        db_path = self._get_db_path()
        if not db_path:
            raise ValueError("未找到 MTGSQLite 数据库。请先下载卡牌数据。")

        self.connection = sqlite3.connect(db_path)
        return self.connection

    def close(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            self.connection = None

    def search_cards_by_name(self, name: str, limit: int = 5) -> List[Dict]:
        """
        按卡牌名称搜索

        Args:
            name: 卡牌名称（支持模糊匹配）
            limit: 返回结果数量限制

        Returns:
            卡牌列表
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # MTGSQLite 的 cards 表结构可能不同，使用基本查询
            query = """
            SELECT name, type, text, colors, manaCost, uuid, setCode
            FROM cards
            WHERE name LIKE ?
            LIMIT ?
            """

            cursor.execute(query, (f"%{name}%", limit))
            rows = cursor.fetchall()

            results = []
            for row in rows:
                # 安全解析 JSON
                try:
                    colors = json.loads(row[3]) if row[3] else []
                except (json.JSONDecodeError, TypeError):
                    colors = []

                results.append({
                    "name": row[0],
                    "type": row[1],
                    "text": row[2],
                    "colors": colors,
                    "mana_cost": row[4],
                    "uuid": row[5],
                    "set_code": row[6]
                })

            return results

        except sqlite3.OperationalError as e:
            # 表可能不存在，尝试查看所有表
            print(f"⚠️  查询失败: {e}")
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            print(f"   可用的表: {[t[0] for t in tables]}")
            return []

    def get_card_by_uuid(self, uuid: str) -> Optional[Dict]:
        """
        根据 UUID 获取卡牌

        Args:
            uuid: 卡牌的 UUID

        Returns:
            卡牌信息
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            query = """
            SELECT name, type, text, colors, manaCost, uuid, setCode
            FROM cards
            WHERE uuid = ?
            LIMIT 1
            """

            cursor.execute(query, (uuid,))
            row = cursor.fetchone()

            if row:
                try:
                    colors = json.loads(row[3]) if row[3] else []
                except (json.JSONDecodeError, TypeError):
                    colors = []

                return {
                    "name": row[0],
                    "type": row[1],
                    "text": row[2],
                    "colors": colors,
                    "mana_cost": row[4],
                    "uuid": row[5],
                    "set_code": row[6]
                }

            return None

        except sqlite3.OperationalError:
            return None

    def get_cards_by_keywords(self, keywords: List[str], limit: int = 10) -> List[Dict]:
        """
        根据关键词异能搜索卡牌

        Args:
            keywords: 关键词异能列表
            limit: 返回结果数量限制

        Returns:
            卡牌列表
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # 构建 WHERE 子句
            conditions = []
            params = []

            for keyword in keywords:
                conditions.append("text LIKE ?")
                params.append(f"%{keyword}%")

            query = f"""
            SELECT DISTINCT name, type, text, colors, manaCost, uuid, setCode
            FROM cards
            WHERE {' OR '.join(conditions)}
            LIMIT ?
            """
            params.append(limit)

            cursor.execute(query, params)
            rows = cursor.fetchall()

            results = []
            for row in rows:
                try:
                    colors = json.loads(row[3]) if row[3] else []
                except (json.JSONDecodeError, TypeError):
                    colors = []

                results.append({
                    "name": row[0],
                    "type": row[1],
                    "text": row[2],
                    "colors": colors,
                    "mana_cost": row[4],
                    "uuid": row[5],
                    "set_code": row[6]
                })

            return results

        except sqlite3.OperationalError:
            return []

    def get_card_rulings(self, uuid: str) -> List[Dict]:
        """
        获取卡牌的官方裁定

        Args:
            uuid: 卡牌的 UUID

        Returns:
            裁定列表
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # MTGSQLite 可能有 foreignData 或 rulings 表
            query = """
            SELECT publishedAt, comment
            FROM foreignData
            WHERE cardUuid = ?
            ORDER BY publishedAt DESC
            """

            cursor.execute(query, (uuid,))
            rows = cursor.fetchall()

            rulings = []
            for row in rows:
                rulings.append({
                    "date": row[0],
                    "comment": row[1]
                })

            return rulings

        except sqlite3.OperationalError:
            return []

    def get_keywords_list(self) -> List[str]:
        """
        从 Keywords.json 获取关键词异能列表

        Returns:
            关键词异能名称列表
        """
        # 尝试多个可能路径
        possible_paths = [
            os.path.join(os.path.dirname(__file__), "../data/mtg/Keywords.json"),
            "data/mtg/Keywords.json",
            "/Users/lianghaoming/cbworkplace/data/mtg/Keywords.json",
        ]

        abs_path = None
        for path in possible_paths:
            if os.path.exists(path):
                abs_path = path
                break

        if not abs_path:
            return []

        try:
            with open(abs_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Keywords.json 的结构: {"meta": {...}, "data": {"keywordAbilities": [...]}}
            keywords = data.get("data", {}).get("keywordAbilities", [])
            return keywords

        except Exception as e:
            print(f"⚠️  读取关键词文件失败: {e}")
            return []

    def get_statistics(self) -> Dict:
        """
        获取数据库统计信息

        Returns:
            统计信息字典
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # 获取总卡牌数
            cursor.execute("SELECT COUNT(*) FROM cards")
            total_cards = cursor.fetchone()[0]

            # 获取系列数
            cursor.execute("SELECT COUNT(DISTINCT setCode) FROM cards")
            total_sets = cursor.fetchone()[0]

            # 获取数据库文件大小
            db_size = os.path.getsize(self._get_db_path()) / 1024 / 1024  # MB

            return {
                "total_cards": total_cards,
                "total_sets": total_sets,
                "database_size_mb": db_size,
                "database_path": self._get_db_path()
            }

        except Exception as e:
            return {
                "error": str(e)
            }

    def get_card_text_for_vectorization(self, limit: int = 100) -> List[Dict]:
        """
        获取适合向量化的卡牌文本数据

        Args:
            limit: 返回卡牌数量限制

        Returns:
            卡牌数据列表，包含 name, text, keywords 等字段
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            query = """
            SELECT name, type, text, colors, manaCost, uuid
            FROM cards
            WHERE text IS NOT NULL AND text != ''
            LIMIT ?
            """

            cursor.execute(query, (limit,))
            rows = cursor.fetchall()

            results = []
            for row in rows:
                try:
                    colors = json.loads(row[3]) if row[3] else []
                except (json.JSONDecodeError, TypeError):
                    colors = []

                results.append({
                    "id": row[5],  # uuid
                    "name": row[0],
                    "type": row[1],
                    "text": row[2],
                    "colors": colors,
                    "mana_cost": row[4]
                })

            return results

        except Exception as e:
            print(f"⚠️  获取向量化数据失败: {e}")
            return []


if __name__ == "__main__":
    # 测试卡牌服务
    print("🃏 MTG 卡牌查询服务测试")
    print("=" * 60)

    service = CardService()

    # 检查状态
    stats = service.get_statistics()
    if "error" in stats:
        print(f"✗ {stats['error']}")
        print("\n💡 请先运行 CardDownloader 下载数据:")
        print("   python -m services.card_downloader")
    else:
        print(f"✓ 数据库连接成功")
        print(f"  - 总卡牌数: {stats['total_cards']:,}")
        print(f"  - 系列数: {stats['total_sets']}")
        print(f"  - 数据库大小: {stats['database_size_mb']:.2f} MB")

        # 测试搜索
        print("\n🔍 测试搜索: 'Black Lotus'")
        cards = service.search_cards_by_name("Black Lotus", limit=3)
        for card in cards:
            print(f"  - {card['name']}")
            print(f"    类型: {card['type']}")
            print(f"    文本: {card['text'][:50]}..." if card['text'] and len(card['text']) > 50 else f"    文本: {card['text']}")
            print()

        # 测试关键词搜索
        print("🔍 测试关键词搜索: ['Flying', 'Trample']")
        cards = service.search_cards_by_keywords(["Flying", "Trample"], limit=3)
        for card in cards:
            print(f"  - {card['name']}")

    service.close()
