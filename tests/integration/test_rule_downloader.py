"""
测试规则下载功能
"""
import sys
import os

# 添加后端路径
sys.path.append('./backend')

from services.rule_downloader import RuleDownloader

def test_download():
    """测试下载功能"""
    print("=" * 60)
    print("📥 测试规则下载功能")
    print("=" * 60)

    downloader = RuleDownloader()

    print("\n1️⃣ 开始下载规则...")
    result = downloader.download_rules(force=True)

    if result["success"]:
        print(f"✅ 下载成功!")
        print(f"   版本: {result.get('version')}")
        print(f"   日期: {result.get('date')}")
        print(f"   文件: {result.get('file_path')}")
        print(f"   大小: {result.get('size', 0) / 1024:.2f} KB")
    else:
        print(f"❌ 下载失败: {result.get('message')}")
        return False

    return True

def test_parse():
    """测试解析功能"""
    print("\n" + "=" * 60)
    print("📊 测试规则解析功能")
    print("=" * 60)

    downloader = RuleDownloader()

    print("\n2️⃣ 开始解析规则...")
    result = downloader.parse_rules()

    if not result["success"]:
        print(f"❌ 解析失败: {result.get('message')}")
        return False

    print(f"✅ 解析成功!")
    print(f"   规则条目: {len(result['rules'])}")
    print(f"   关键词异能: {len(result['keyword_abilities'])}")
    print(f"   术语表: {len(result['glossary'])}")

    # 显示示例
    if result['rules']:
        print(f"\n📝 规则示例 (前3条):")
        for i, rule in enumerate(result['rules'][:3], 1):
            print(f"\n   {i}. {rule['rule_number']}")
            print(f"      {rule['content'][:100]}...")

    if result['keyword_abilities']:
        print(f"\n🔑 关键词异能示例 (前3个):")
        for i, ka in enumerate(result['keyword_abilities'][:3], 1):
            print(f"\n   {i}. {ka['keyword_name']}")
            print(f"      {ka['description'][:80]}...")

    if result['glossary']:
        print(f"\n📚 术语表示例 (前3个):")
        for i, term in enumerate(result['glossary'][:3], 1):
            print(f"\n   {i}. {term['term']}")
            print(f"      {term['definition'][:80]}...")

    return True

def test_vectorization():
    """测试向量化数据准备"""
    print("\n" + "=" * 60)
    print("🤖 测试向量化数据准备")
    print("=" * 60)

    downloader = RuleDownloader()

    print("\n3️⃣ 准备向量化数据...")
    result = downloader.get_rules_for_vectorization()

    if not result["success"]:
        print(f"❌ 准备失败: {result.get('message')}")
        return False

    print(f"✅ 数据准备成功!")
    print(f"   总文本数: {result['total_count']}")
    print(f"   数据类型: 规则、关键词异能、术语表")

    # 显示数据分布
    type_counts = {}
    for meta in result['metadata']:
        t = meta['type']
        type_counts[t] = type_counts.get(t, 0) + 1

    print(f"\n   数据分布:")
    for t, count in type_counts.items():
        print(f"      - {t}: {count}")

    # 显示示例
    print(f"\n📄 文本示例 (前3个):")
    for i in range(min(3, len(result['texts']))):
        print(f"\n   {i+1}. 类型: {result['metadata'][i]['type']}")
        print(f"      文本: {result['texts'][i][:100]}...")

    return True

def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("🎯 万智牌规则下载功能测试")
    print("=" * 60)

    success = True

    # 测试下载
    if not test_download():
        success = False

    # 测试解析
    if success and not test_parse():
        success = False

    # 测试向量化
    if success and not test_vectorization():
        success = False

    # 总结
    print("\n" + "=" * 60)
    if success:
        print("✅ 所有测试通过!")
        print("\n📌 后续步骤:")
        print("1. 启动服务: python3 backend/main.py")
        print("2. 访问API文档: http://localhost:8000/docs")
        print("3. 测试规则更新API")
        print("4. 集成向量数据库进行语义搜索")
    else:
        print("❌ 部分测试失败，请检查错误信息")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    main()
