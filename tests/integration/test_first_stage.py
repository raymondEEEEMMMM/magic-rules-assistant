"""
测试脚本 - 验证第一阶段功能
"""
import sys
sys.path.append('./backend')

from database import RuleDatabase
from services import RuleService
from wechat import MessageHandler

def test_database():
    """测试数据库"""
    print("=" * 50)
    print("📊 测试数据库功能")
    print("=" * 50)

    db = RuleDatabase()

    # 测试关键词异能查询
    print("\n1️⃣ 测试关键词异能查询: '飞行'")
    ability = db.get_keyword_ability("飞行")
    if ability:
        print(f"✓ 找到: {ability['keyword_name']}")
        print(f"  描述: {ability['description'][:50]}...")
    else:
        print("✗ 未找到")

    # 测试卡牌查询
    print("\n2️⃣ 测试卡牌查询: '黑莲花'")
    card = db.get_card_rule("黑莲花")
    if card:
        print(f"✓ 找到: {card['card_name']}")
        print(f"  类型: {card['card_type']}")
        print(f"  规则: {card['oracle_text']}")
    else:
        print("✗ 未找到")

    # 测试规则搜索
    print("\n3️⃣ 测试规则搜索: '飞行'")
    rules = db.search_by_keywords(["飞行"])
    if rules:
        print(f"✓ 找到 {len(rules)} 条规则")
        for rule in rules[:2]:
            print(f"  - {rule['rule_number']}: {rule['rule_title']}")
    else:
        print("✗ 未找到")

    # 测试问答模板搜索
    print("\n4️⃣ 测试问答模板搜索: '堆栈'")
    qa_list = db.search_qa_templates(["堆栈"])
    if qa_list:
        print(f"✓ 找到 {len(qa_list)} 条问答")
        for qa in qa_list[:1]:
            print(f"  - Q: {qa['question']}")
    else:
        print("✗ 未找到")

def test_rule_service():
    """测试规则服务"""
    print("\n" + "=" * 50)
    print("🔧 测试规则服务")
    print("=" * 50)

    db = RuleDatabase()
    service = RuleService(db)

    # 测试综合搜索
    print("\n1️⃣ 测试综合搜索: '飞行'")
    results = service.search_rules("飞行")
    print(f"✓ 规则数: {len(results['rules'])}")
    print(f"✓ 异能数: {len(results['keyword_abilities'])}")
    print(f"✓ 卡牌数: {len(results['cards'])}")
    print(f"✓ 问答数: {len(results['qa_templates'])}")

    # 测试格式化响应
    print("\n2️⃣ 测试格式化响应:")
    response = service.format_response(results)
    print(response[:200] + "...")

def test_message_handler():
    """测试消息处理器"""
    print("\n" + "=" * 50)
    print("💬 测试消息处理器")
    print("=" * 50)

    db = RuleDatabase()
    service = RuleService(db)
    handler = MessageHandler(service)

    # 测试不同的消息类型
    test_messages = [
        ("飞行", "普通查询"),
        ("卡牌:黑莲花", "卡牌查询"),
        ("异能:践踏", "异能查询"),
        ("/help", "帮助命令"),
        ("/start", "开始命令"),
    ]

    for message, msg_type in test_messages:
        print(f"\n{msg_type}: '{message}'")
        response = handler.handle_text_message(message)
        print("—" * 40)
        print(response[:150] + "...")

def test_api():
    """测试 API 端点（需要服务运行）"""
    print("\n" + "=" * 50)
    print("🌐 API 测试说明")
    print("=" * 50)
    print("\n启动服务后，可以使用以下命令测试 API:")
    print("\n1. 搜索规则:")
    print("   curl 'http://localhost:8000/api/search?q=飞行'")
    print("\n2. 查询卡牌:")
    print("   curl 'http://localhost:8000/api/card?n=黑莲花'")
    print("\n3. 查询异能:")
    print("   curl 'http://localhost:8000/api/keyword?k=践踏'")
    print("\n4. 服务状态:")
    print("   curl 'http://localhost:8000/'")

def main():
    """主测试函数"""
    print("\n" + "=" * 50)
    print("🎯 万智牌规则问答 - 第一阶段功能测试")
    print("=" * 50)

    try:
        # 运行各项测试
        test_database()
        test_rule_service()
        test_message_handler()
        test_api()

        print("\n" + "=" * 50)
        print("✅ 所有测试完成！")
        print("=" * 50)

        print("\n📝 下一步操作:")
        print("1. 启动服务: python3 backend/main.py")
        print("2. 访问 API 文档: http://localhost:8000/docs")
        print("3. 测试 API 端点")
        print("4. 配置微信公众号（如需）")

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
