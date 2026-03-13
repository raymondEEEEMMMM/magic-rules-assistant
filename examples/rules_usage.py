"""
规则下载功能使用示例
"""
import sys
sys.path.append('../backend')

from services.rule_downloader import RuleDownloader

def example_1_download_rules():
    """示例1: 下载最新规则"""
    print("\n" + "=" * 60)
    print("示例1: 下载最新规则")
    print("=" * 60)

    downloader = RuleDownloader()

    # 下载规则
    result = downloader.download_rules(force=False)

    if result["success"]:
        print(f"✅ 下载成功!")
        print(f"   版本: {result.get('version')}")
        print(f"   日期: {result.get('date')}")
        print(f"   文件: {result.get('file_path')}")
    else:
        print(f"❌ {result.get('message')}")

def example_2_parse_rules():
    """示例2: 解析规则文件"""
    print("\n" + "=" * 60)
    print("示例2: 解析规则文件")
    print("=" * 60)

    downloader = RuleDownloader()

    # 解析规则
    result = downloader.parse_rules()

    if result["success"]:
        print(f"✅ 解析成功!")
        print(f"   规则条目: {len(result['rules'])}")
        print(f"   关键词异能: {len(result['keyword_abilities'])}")
        print(f"   术语表: {len(result['glossary'])}")

        # 查找特定规则
        print(f"\n🔍 查找死触规则:")
        for ka in result['keyword_abilities']:
            if 'deathtouch' in ka['keyword_name'].lower():
                print(f"   {ka['keyword_name']}")
                print(f"   {ka['description']}")
                break
    else:
        print(f"❌ {result.get('message')}")

def example_3_vectorization_data():
    """示例3: 获取向量化数据"""
    print("\n" + "=" * 60)
    print("示例3: 准备向量化数据")
    print("=" * 60)

    downloader = RuleDownloader()

    # 获取向量化数据
    result = downloader.get_rules_for_vectorization()

    if result["success"]:
        print(f"✅ 数据准备成功!")
        print(f"   总文本数: {result['total_count']}")

        # 显示数据分布
        type_counts = {}
        for meta in result['metadata']:
            t = meta['type']
            type_counts[t] = type_counts.get(t, 0) + 1

        print(f"   数据分布:")
        for t, count in type_counts.items():
            print(f"      - {t}: {count}")

        # 显示前3个文本
        print(f"\n📄 前3个文本:")
        for i in range(min(3, len(result['texts']))):
            print(f"\n   {i+1}. {result['metadata'][i]['type']}")
            print(f"      {result['texts'][i][:100]}...")
    else:
        print(f"❌ {result.get('message')}")

def example_4_search_specific_rule():
    """示例4: 搜索特定规则"""
    print("\n" + "=" * 60)
    print("示例4: 搜索特定规则")
    print("=" * 60)

    downloader = RuleDownloader()

    # 解析规则
    parse_result = downloader.parse_rules()
    if not parse_result["success"]:
        print(f"❌ {parse_result.get('message')}")
        return

    # 搜索包含"flying"的规则
    search_keyword = "flying"

    print(f"🔍 搜索包含 '{search_keyword}' 的规则:")

    # 搜索规则条目
    found_rules = []
    for rule in parse_result['rules']:
        if search_keyword.lower() in rule['content'].lower():
            found_rules.append(rule)

    if found_rules:
        print(f"   找到 {len(found_rules)} 条规则")
        for i, rule in enumerate(found_rules[:3], 1):
            print(f"\n   {i}. {rule['rule_number']}")
            print(f"      {rule['content'][:100]}...")
    else:
        print("   未找到相关规则")

def example_5_check_version():
    """示例5: 检查规则版本"""
    print("\n" + "=" * 60)
    print("示例5: 检查规则版本")
    print("=" * 60)

    downloader = RuleDownloader()

    # 获取本地和在线版本
    local_info = downloader._get_local_rules_info()
    online_info = downloader._get_online_rules_info()

    if local_info:
        print(f"📦 本地版本:")
        print(f"   版本: {local_info.get('version')}")
        print(f"   日期: {local_info.get('date')}")
    else:
        print("📦 本地版本: 未下载")

    if online_info:
        print(f"\n🌐 在线版本:")
        print(f"   版本: {online_info.get('version')}")
        print(f"   日期: {online_info.get('date')}")
    else:
        print("\n🌐 在线版本: 无法获取")

    # 判断是否需要更新
    if local_info and online_info:
        if downloader._is_latest_version(local_info, online_info):
            print(f"\n✅ 本地规则已是最新版本")
        else:
            print(f"\n⚠️ 有新版本可用，建议更新")

def main():
    """运行所有示例"""
    print("\n" + "=" * 60)
    print("🎯 万智牌规则下载功能使用示例")
    print("=" * 60)

    try:
        example_1_download_rules()
        example_2_parse_rules()
        example_3_vectorization_data()
        example_4_search_specific_rule()
        example_5_check_version()

        print("\n" + "=" * 60)
        print("✅ 所有示例运行完成!")
        print("=" * 60 + "\n")

    except Exception as e:
        print(f"\n❌ 运行失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
