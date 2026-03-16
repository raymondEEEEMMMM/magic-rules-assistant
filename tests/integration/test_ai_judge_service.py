"""
AI 裁判服务测试
"""
import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../functions/mtgAsk/backend"))

# 优先使用 MINIMAX_API_KEY，否则尝试使用 ANTHROPIC_AUTH_TOKEN
api_key = os.environ.get("MINIMAX_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN", "")
if api_key:
    os.environ["MINIMAX_API_KEY"] = api_key

from services.ai_judge_service import AIJudgeService


def test_ai_judge_opposition_agent():
    """测试案例：EDH 局有2个反对派密探时的搜寻"""
    service = AIJudgeService()

    # 检查是否配置了 API Key
    if not service.api_key:
        print("⚠️ 警告: 未配置 MINIMAX_API_KEY，跳过实际 API 调用测试")
        print("请设置环境变量 MINIMAX_API_KEY 后运行此测试")
        return

    # 测试问题
    question = "EDH 局，场上有 2 个反对派密探（Opposition Agent），某牌手（没有反对派密探）搜寻牌库。"

    print(f"\n{'='*60}")
    print(f"测试问题: {question}")
    print(f"{'='*60}\n")

    result = service.chat(question, session_id="test_opposition_agent")

    print(f"成功: {result['success']}")
    print(f"\n回答:\n{result['reply']}")
    print(f"\n{'='*60}")


def test_ai_judge_tarmogoyf():
    """测试案例：塔莫耶夫 vs 闪电击"""
    service = AIJudgeService()

    if not service.api_key:
        print("⚠️ 警告: 未配置 MINIMAX_API_KEY，跳过测试")
        return

    question = "我场上有塔莫耶夫，对手施放闪电击指定我的塔莫耶夫，能否响应触发敏捷异能在闪电击造成伤害前造成1点伤害？"

    print(f"\n{'='*60}")
    print(f"测试问题: {question}")
    print(f"{'='*60}\n")

    result = service.chat(question, session_id="test_tarmogoyf")

    print(f"成功: {result['success']}")
    print(f"\n回答:\n{result['reply']}")
    print(f"\n{'='*60}")


def test_ai_judge_analyze():
    """测试 analyze 方法"""
    service = AIJudgeService()

    if not service.api_key:
        print("⚠️ 警告: 未配置 MINIMAX_API_KEY，跳过测试")
        return

    result = service.analyze({
        "game_state": "EDH 局，场上有 2 个反对派密探（Opposition Agent）",
        "cards": ["Opposition Agent", "Opposition Agent"],
        "question": "某牌手（没有反对派密探）搜寻牌库会发生什么？"
    })

    print(f"\n{'='*60}")
    print("测试 analyze 方法")
    print(f"{'='*60}\n")
    print(f"成功: {result['success']}")
    print(f"\n分析:\n{result['analysis']}")
    print(f"\n{'='*60}")


if __name__ == "__main__":
    # 先测试 analyze 方法
    test_ai_judge_analyze()

    # 然后测试对话
    test_ai_judge_opposition_agent()

    # 额外测试：经典问题
    test_ai_judge_tarmogoyf()
