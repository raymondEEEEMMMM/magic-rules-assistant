#!/usr/bin/env python3
"""
MTG 卡牌数据下载脚本

快速下载 MTGJSON 卡牌数据并集成到规则系统。
"""

import sys
import os

# 添加 backend 目录到 Python 路径
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_dir)

from services.card_downloader import CardDownloader


def main():
    """主函数"""
    print("=" * 60)
    print("🃏 MTG 卡牌数据下载")
    print("=" * 60)

    # 创建下载器
    downloader = CardDownloader()

    # 查看当前状态
    print("\n📊 当前状态:")
    status = downloader.get_status()
    print(f"   数据目录: {status['data_dir']}")
    print(f"   数据库: {'✓ 存在' if status['database_exists'] else '✗ 不存在'}")
    if status['database_size']:
        print(f"   数据库大小: {status['database_size']:.2f} MB")
    print(f"   关键词: {'✓ 存在' if status['keywords_exists'] else '✗ 不存在'}")

    # 询问是否下载
    if status['database_exists'] and status['keywords_exists']:
        print("\n⚠️  数据文件已存在。")
        force = input("是否强制重新下载? (y/N): ").strip().lower() == 'y'
    else:
        print("\n📥 开始下载数据...")
        force = False

    # 下载文件
    print("\n" + "=" * 60)
    result = downloader.download_all(force=force)

    if result["success"]:
        print("\n🎉 所有文件下载成功！")

        # 显示下载结果
        print("\n📊 下载结果:")
        for r in result["results"]:
            if r["success"]:
                print(f"  ✓ {r['message']}")
            else:
                print(f"  ✗ {r['message']}")

        # 显示文件信息
        print("\n📁 文件位置:")
        status = downloader.get_status()
        if status['database_path']:
            print(f"  - 卡牌数据库: {status['database_path']}")
        if status['keywords_path']:
            print(f"  - 关键词文件: {status['keywords_path']}")

        print("\n💡 下一步:")
        print("  1. 查询卡牌: python3 test_card_service.py")
        print("  2. 集成到规则系统: 参考 docs/MTGJSON卡牌数据需求分析.md")
    else:
        print("\n⚠️  部分文件下载失败:")
        for r in result["results"]:
            if not r["success"]:
                print(f"  ✗ {r['message']}")
        print(f"\n📊 成功: {result['success_count']}, 失败: {result['fail_count']}")


if __name__ == "__main__":
    main()
