#!/usr/bin/env python3
"""
MTG 卡牌服务测试脚本

测试卡牌查询功能，验证 MTGJSON 数据集成。
"""

import sys
import os

# 添加 backend 目录到 Python 路径
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_dir)

from services.card_service import CardService
from services.card_downloader import CardDownloader


def test_database_connection():
    """测试数据库连接"""
    print("\n" + "=" * 60)
    print("1️⃣  测试数据库连接")
    print("=" * 60)

    service = CardService()

    # 获取统计信息
    stats = service.get_statistics()

    if "error" in stats:
        print(f"✗ 数据库连接失败: {stats['error']}")
        print("\n💡 请先运行下载脚本:")
        print("   python3 download_cards.py")
        return False

    print(f"✓ 数据库连接成功")
    print(f"  - 总卡牌数: {stats['total_cards']:,}")
    print(f"  - 系列数: {stats['total_sets']}")
    print(f"  - 数据库大小: {stats['database_size_mb']:.2f} MB")
    print(f"  - 路径: {stats['database_path']}")

    return True


def test_search_by_name():
    """测试按名称搜索"""
    print("\n" + "=" * 60)
    print("2️⃣  测试按名称搜索")
    print("=" * 60)

    service = CardService()

    test_names = [
        "Black Lotus",
        "Lightning Bolt",
        "Ancestral Recall",
        "Time Walk",
        "Mox Jet"
    ]

    for name in test_names:
        print(f"\n🔍 搜索: '{name}'")
        cards = service.search_cards_by_name(name, limit=3)

        if not cards:
            print(f"  ✗ 未找到结果")
        else:
            print(f"  ✓ 找到 {len(cards)} 张卡牌")
            for i, card in enumerate(cards, 1):
                print(f"\n  [{i}] {card['name']}")
                print(f"      类型: {card['type']}")
                if card['mana_cost']:
                    print(f"      费用: {card['mana_cost']}")
                if card['text']:
                    text_preview = card['text'][:60] + "..." if len(card['text']) > 60 else card['text']
                    print(f"      文本: {text_preview}")


def test_search_by_keywords():
    """测试按关键词搜索"""
    print("\n" + "=" * 60)
    print("3️⃣  测试按关键词异能搜索")
    print("=" * 60)

    service = CardService()

    test_keywords = [
        ["Flying"],
        ["Trample"],
        ["First Strike"],
        ["Haste"],
        ["Deathtouch"]
    ]

    for keywords in test_keywords:
        print(f"\n🔍 搜索关键词: {keywords}")
        cards = service.get_cards_by_keywords(keywords, limit=3)

        if not cards:
            print(f"  ✗ 未找到结果")
        else:
            print(f"  ✓ 找到 {len(cards)} 张卡牌")
            for card in cards:
                print(f"  - {card['name']}")


def test_get_keywords():
    """测试获取关键词列表"""
    print("\n" + "=" * 60)
    print("4️⃣  测试获取关键词异能列表")
    print("=" * 60)

    service = CardService()

    keywords = service.get_keywords_list()

    if not keywords:
        print("✗ 未找到关键词数据")
        print("\n💡 请检查 Keywords.json 文件是否存在")
    else:
        print(f"✓ 共找到 {len(keywords)} 个关键词异能")
        print(f"\n  前 20 个关键词:")
        for i, kw in enumerate(keywords[:20], 1):
            print(f"  {i:2d}. {kw}")


def test_vectorization_data():
    """测试向量化数据获取"""
    print("\n" + "=" * 60)
    print("5️⃣  测试获取向量化数据")
    print("=" * 60)

    service = CardService()

    cards = service.get_card_text_for_vectorization(limit=5)

    if not cards:
        print("✗ 未获取到数据")
    else:
        print(f"✓ 成功获取 {len(cards)} 张卡牌的向量化数据")
        print(f"\n  示例数据:")
        for card in cards:
            print(f"\n  卡牌: {card['name']}")
            print(f"    UUID: {card['id']}")
            print(f"    类型: {card['type']}")
            if card['text']:
                text_preview = card['text'][:40] + "..." if len(card['text']) > 40 else card['text']
                print(f"    文本: {text_preview}")


def test_download_status():
    """测试下载状态"""
    print("\n" + "=" * 60)
    print("📊 下载状态检查")
    print("=" * 60)

    downloader = CardDownloader()
    status = downloader.get_status()

    print(f"  数据目录: {status['data_dir']}")
    print(f"  数据库: {'✓ 存在' if status['database_exists'] else '✗ 不存在'}")
    if status['database_size']:
        print(f"  数据库大小: {status['database_size']:.2f} MB")
        print(f"  数据库路径: {status['database_path']}")
    print(f"  关键词: {'✓ 存在' if status['keywords_exists'] else '✗ 不存在'}")
    if status['keywords_exists']:
        print(f"  关键词路径: {status['keywords_path']}")


def main():
    """主函数"""
    print("=" * 60)
    print("🃏 MTG 卡牌服务测试")
    print("=" * 60)

    # 检查下载状态
    test_download_status()

    # 测试数据库连接
    if not test_database_connection():
        return

    # 运行其他测试
    test_search_by_name()
    test_search_by_keywords()
    test_get_keywords()
    test_vectorization_data()

    print("\n" + "=" * 60)
    print("✅ 所有测试完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
