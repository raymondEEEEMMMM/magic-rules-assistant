"""
更新万智牌规则
"""
import sys
sys.path.append('./backend')

from services.rule_downloader import RuleDownloader

def main():
    """主函数"""
    print("=" * 60)
    print("🔄 万智牌规则更新工具")
    print("=" * 60)

    downloader = RuleDownloader()

    # 下载规则
    print("\n📥 开始下载最新规则...")
    result = downloader.download_rules(force=True)

    if result["success"]:
        print(f"\n✅ 规则下载成功!")
        print(f"   版本: {result.get('version')}")
        print(f"   日期: {result.get('date')}")
        print(f"   大小: {result.get('size', 0) / 1024:.2f} KB")

        # 解析规则
        print(f"\n📊 开始解析规则...")
        parse_result = downloader.parse_rules()

        if parse_result["success"]:
            print(f"✅ 解析成功!")
            print(f"   规则条目: {len(parse_result['rules'])}")
            print(f"   关键词异能: {len(parse_result['keyword_abilities'])}")
            print(f"   术语表: {len(parse_result['glossary'])}")

            # 显示一些示例
            if parse_result['rules']:
                print(f"\n📝 规则示例:")
                for i, rule in enumerate(parse_result['rules'][:3], 1):
                    print(f"   {i}. {rule['rule_number']}")
                    print(f"      {rule['content'][:80]}...")

            print(f"\n✅ 规则更新完成!")

        else:
            print(f"❌ 解析失败: {parse_result.get('message')}")

    else:
        print(f"❌ 下载失败: {result.get('message')}")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
