#!/usr/bin/env python3
"""
MTGCH API 接入测试脚本
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.services.mtgch_api import MTGCHAPIClient, format_card_info


def test_mtgch_api():
    """测试MTGCH API"""
    print("🔍 MTGCH 汉化 API 测试")
    print("=" * 60)

    with MTGCHAPIClient() as client:

        # 测试1: 搜索卡牌
        print("\n1️⃣ 测试搜索卡牌: '闪电风暴'")
        print("-" * 60)
        result = client.search_cards("闪电风暴", page_size=2)
        if "items" in result and result["items"]:
            print(f"✓ 找到 {len(result['items'])} 张卡牌")
            for i, card in enumerate(result['items'], 1):
                print(f"\n【卡牌 {i}】")
                print(format_card_info(card))
        else:
            print(f"✗ 搜索失败: {result}")

        # 测试2: 搜索英文卡牌
        print("\n\n2️⃣ 测试搜索英文卡牌: 'Black Lotus'")
        print("-" * 60)
        result = client.search_cards("Black Lotus", page_size=1, priority_chinese=True)
        if "items" in result and result["items"]:
            print("✓ 找到1张卡牌")
            print(format_card_info(result["items"][0]))
        else:
            print(f"✗ 搜索失败: {result}")

        # 测试3: 自动补全
        print("\n\n3️⃣ 测试自动补全: '闪电'")
        print("-" * 60)
        result = client.autocomplete("闪电", size=5)
        if "items" in result:
            print(f"✓ 找到 {len(result['items'])} 个建议:")
            for item in result["items"]:
                print(f"  - {item.get('name', '未知')} ({item.get('set_code', '?')})")
        else:
            print(f"✗ 自动补全失败: {result}")

        # 测试4: 随机卡牌
        print("\n\n4️⃣ 测试随机卡牌")
        print("-" * 60)
        card = client.get_random_card()
        if card:
            print("✓ 随机卡牌:")
            print(format_card_info(card))
        else:
            print("✗ 获取随机卡牌失败")

        # 测试5: 通过系列和编号获取卡牌
        print("\n\n5️⃣ 测试通过系列和编号获取卡牌 (MKM/2)")
        print("-" * 60)
        card = client.get_card_by_set_and_number("MKM", "2")
        if card:
            print("✓ 找到卡牌:")
            print(format_card_info(card))
        else:
            print("✗ 未找到卡牌")

        # 测试6: 获取系列列表
        print("\n\n6️⃣ 测试获取系列列表")
        print("-" * 60)
        sets = client.get_sets()
        if sets:
            print(f"✓ 找到 {len(sets)} 个系列，显示前10个:")
            for s in sets[:10]:
                print(f"  - {s.get('name', s.get('code', '未知'))} ({s.get('code', '?')})")
        else:
            print("✗ 获取系列列表失败")

        # 测试7: 获取某系列的所有卡牌
        print("\n\n7️⃣ 测试获取系列卡牌 (MKM, 前3张)")
        print("-" * 60)
        result = client.get_set_cards("MKM", page=1, page_size=3)
        if "items" in result:
            print(f"✓ 找到 {len(result['items'])} 张卡牌:")
            for card in result["items"]:
                print(f"  - {card.get('name', '未知')} #{card.get('collector_number', '?')}")
        else:
            print(f"✗ 获取系列卡牌失败: {result}")

    print("\n" + "=" * 60)
    print("✓ 所有测试完成")


if __name__ == "__main__":
    test_mtgch_api()
