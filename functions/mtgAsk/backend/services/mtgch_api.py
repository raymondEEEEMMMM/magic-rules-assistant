"""
MTGCH 汉化API服务

提供对 MTGCH 中文万智牌API的访问接口。
API文档: https://mtgch.com/api/v1/docs
"""

import requests
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class MTGCHAPIClient:
    """MTGCH API 客户端"""

    BASE_URL = "https://mtgch.com/api/v1"

    def __init__(self, timeout: int = 10):
        """
        初始化客户端

        Args:
            timeout: 请求超时时间（秒）
        """
        self.timeout = timeout
        self.session = requests.Session()

    def search_cards(
        self,
        query: str,
        page: int = 1,
        page_size: int = 20,
        priority_chinese: bool = True,
        order: Optional[str] = None,
        unique: Optional[str] = None
    ) -> Dict:
        """
        搜索卡牌

        Args:
            query: 查询字符串
            page: 页码（默认1）
            page_size: 每页数量（默认20，最大100）
            priority_chinese: 是否优先中文版本（默认True）
            order: 排序字段（如 name, -mv, rarity）
            unique: 去重方式（scryfall_id, oracle_id, illustration_id）

        Returns:
            API响应数据
        """
        params = {
            "q": query,
            "page": page,
            "page_size": page_size,
            "priority_chinese": priority_chinese
        }

        if order:
            params["order"] = order
        if unique:
            params["unique"] = unique

        try:
            response = self.session.get(
                f"{self.BASE_URL}/result",
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"搜索卡牌失败: {e}")
            return {"error": str(e)}

    def get_card_by_id(self, card_id: str) -> Optional[Dict]:
        """
        通过UUID获取单张卡牌详情

        Args:
            card_id: 卡牌UUID

        Returns:
            卡牌详情，如果未找到返回None
        """
        try:
            response = self.session.get(
                f"{self.BASE_URL}/card/{card_id}/",
                timeout=self.timeout
            )
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"获取卡牌详情失败: {e}")
            return None

    def get_card_by_set_and_number(
        self,
        set_code: str,
        collector_number: str
    ) -> Optional[Dict]:
        """
        由系列代码和收集编号获取单张卡牌

        Args:
            set_code: 系列代码（如 MKM, MOM）
            collector_number: 收集编号

        Returns:
            卡牌详情，如果未找到返回None
        """
        try:
            response = self.session.get(
                f"{self.BASE_URL}/card/{set_code}/{collector_number}/",
                timeout=self.timeout
            )
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"获取卡牌详情失败: {e}")
            return None

    def get_card_versions(self, card_id: str, limit: int = 10) -> List[Dict]:
        """
        通过UUID查询该卡所有版本

        Args:
            card_id: 卡牌UUID
            limit: 返回数量上限（最大100）

        Returns:
            版本列表
        """
        params = {"limit": min(limit, 100)}

        try:
            response = self.session.get(
                f"{self.BASE_URL}/versions/{card_id}/",
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"获取卡牌版本失败: {e}")
            return []

    def get_random_card(self) -> Optional[Dict]:
        """
        随机获取一张卡牌

        Returns:
            卡牌详情，如果失败返回None
        """
        try:
            response = self.session.get(
                f"{self.BASE_URL}/random",
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"获取随机卡牌失败: {e}")
            return None

    def get_adjacent_card(
        self,
        set_code: str,
        collector_number: str,
        direction: str = "next"
    ) -> Optional[Dict]:
        """
        获取相邻卡牌（上一张或下一张）

        Args:
            set_code: 系列代码
            collector_number: 收集编号
            direction: 方向（next 或 prev）

        Returns:
            卡牌详情，如果未找到返回None
        """
        if direction not in ["next", "prev"]:
            raise ValueError("direction 必须是 'next' 或 'prev'")

        params = {
            "set": set_code,
            "collector_number": collector_number
        }

        try:
            response = self.session.get(
                f"{self.BASE_URL}/card/{direction}",
                params=params,
                timeout=self.timeout
            )
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"获取相邻卡牌失败: {e}")
            return None

    def autocomplete(
        self,
        query: str,
        size: int = 10,
        is_for_deck: bool = False,
        page: int = 1
    ) -> Dict:
        """
        自动补全搜索

        Args:
            query: 搜索关键词或结构化查询
            size: 每页返回结果数量（最大50）
            is_for_deck: 是否用于卡组构建
            page: 页码

        Returns:
            自动补全结果
        """
        params = {
            "q": query,
            "size": min(size, 50),
            "is_for_deck": is_for_deck,
            "page": page
        }

        try:
            response = self.session.get(
                f"{self.BASE_URL}/autocomplete/",
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"自动补全搜索失败: {e}")
            return {"error": str(e)}

    def get_sets(self) -> List[Dict]:
        """
        获取所有卡牌系列

        Returns:
            系列列表
        """
        try:
            response = self.session.get(
                f"{self.BASE_URL}/sets/",
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"获取系列列表失败: {e}")
            return []

    def get_set_by_code(self, set_code: str) -> Optional[Dict]:
        """
        获取单个系列的详细信息

        Args:
            set_code: 系列代码

        Returns:
            系列详情，如果未找到返回None
        """
        try:
            response = self.session.get(
                f"{self.BASE_URL}/set/{set_code}/",
                timeout=self.timeout
            )
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"获取系列详情失败: {e}")
            return None

    def get_set_cards(
        self,
        set_code: str,
        order: Optional[str] = None,
        unique: str = "scryfall_id",
        priority_chinese: bool = True,
        page: int = 1,
        page_size: int = 20
    ) -> Dict:
        """
        获取特定系列的所有卡牌

        Args:
            set_code: 系列代码
            order: 排序字段
            unique: 去重方式
            priority_chinese: 是否优先中文版本
            page: 页码
            page_size: 每页数量

        Returns:
            分页的卡牌列表
        """
        params = {
            "unique": unique,
            "priority_chinese": priority_chinese,
            "page": page,
            "page_size": page_size
        }

        if order:
            params["order"] = order

        try:
            response = self.session.get(
                f"{self.BASE_URL}/set/{set_code}/cards/",
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"获取系列卡牌失败: {e}")
            return {"error": str(e)}

    def search_cards_by_set(self, set_code: str, page: int = 1) -> Dict:
        """
        通过系列代码搜索卡牌（使用Scryfall API获取图片）

        Args:
            set_code: 系列代码（如 mkm, mom）
            page: 页码

        Returns:
            Scryfall API 响应数据（包含 image_uris）
        """
        params = {
            "q": f"set:{set_code}",
            "page": page
        }
        try:
            response = self.session.get(
                "https://api.scryfall.com/cards/search",
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Scryfall搜索系列卡牌失败: {e}")
            return {"error": str(e), "data": [], "total_cards": 0, "has_more": False}

    def search_scryfall(self, query: str, page: int = 1) -> Dict:
        """
        通用的 Scryfall 搜索接口

        Args:
            query: Scryfall 搜索语法（如 "set:sld+date:2026-04"）
            page: 页码

        Returns:
            Scryfall API 响应数据
        """
        params = {
            "q": query,
            "page": page
        }
        try:
            response = self.session.get(
                "https://api.scryfall.com/cards/search",
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Scryfall搜索失败: {e}")
            return {"error": str(e), "data": [], "total_cards": 0, "has_more": False}

    def close(self):
        """关闭会话"""
        self.session.close()

    def __enter__(self):
        """支持上下文管理器"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文时关闭会话"""
        self.close()


def format_card_info(card: Dict) -> str:
    """
    格式化卡牌信息为可读文本

    Args:
        card: 卡牌数据

    Returns:
        格式化后的文本
    """
    if not card:
        return "未找到卡牌"

    lines = []

    # 中文名称（优先）
    name = card.get("name", "未知名称")
    lines.append(f"📛 名称: {name}")

    # 英文名称
    name_en = card.get("name_en")
    if name_en and name_en != name:
        lines.append(f"   ({name_en})")

    # 法力费用
    mana_cost = card.get("mana_cost")
    if mana_cost:
        lines.append(f"💎 法力费用: {mana_cost}")

    # 类型行
    type_line = card.get("type_line")
    if type_line:
        lines.append(f"🏷️  类型: {type_line}")

    # 稀有度
    rarity = card.get("rarity")
    if rarity:
        rarity_map = {
            "C": "普通",
            "U": "非普通",
            "R": "稀有",
            "M": "秘稀",
            "S": "特别稀有"
        }
        lines.append(f"⭐ 稀有度: {rarity_map.get(rarity, rarity)}")

    # 规则文本
    oracle_text = card.get("oracle_text")
    if oracle_text:
        lines.append(f"📜 规则文本:\n{oracle_text}")

    # 背景叙述
    flavor_text = card.get("flavor_text")
    if flavor_text:
        lines.append(f"💭 背景叙述:\n{flavor_text}")

    # 力量/防御
    power = card.get("power")
    toughness = card.get("toughness")
    if power is not None and toughness is not None:
        lines.append(f"⚔️ 力量/防御: {power}/{toughness}")

    # 忠诚度（鹏洛客）
    loyalty = card.get("loyalty")
    if loyalty:
        lines.append(f"🎯 忠诚度: {loyalty}")

    # 系列和编号
    set_code = card.get("set_code")
    collector_number = card.get("collector_number")
    if set_code or collector_number:
        lines.append(f"📚 系列编号: {set_code or '?'} #{collector_number or '?'}")

    return "\n".join(lines)


if __name__ == "__main__":
    # 测试代码
    print("🔍 MTGCH API 测试")
    print("=" * 60)

    with MTGCHAPIClient() as client:
        # 测试搜索
        print("\n1️⃣ 搜索测试: '闪电风暴'")
        result = client.search_cards("闪电风暴", page_size=1)
        if "items" in result and result["items"]:
            card = result["items"][0]
            print(format_card_info(card))
        else:
            print("搜索失败")

        # 测试自动补全
        print("\n2️⃣ 自动补全测试: '闪电'")
        result = client.autocomplete("闪电", size=3)
        if "items" in result:
            for item in result["items"][:3]:
                print(f"  - {item.get('name', '未知')}")
        else:
            print("自动补全失败")

        # 测试获取系列列表
        print("\n3️⃣ 系列列表测试")
        sets = client.get_sets()
        if sets:
            print(f"找到 {len(sets)} 个系列，前5个:")
            for s in sets[:5]:
                print(f"  - {s.get('name', s.get('code', '未知'))}")

        # 测试随机卡牌
        print("\n4️⃣ 随机卡牌测试")
        card = client.get_random_card()
        if card:
            print(format_card_info(card))
        else:
            print("获取随机卡牌失败")

    print("\n" + "=" * 60)
    print("✓ 测试完成")
