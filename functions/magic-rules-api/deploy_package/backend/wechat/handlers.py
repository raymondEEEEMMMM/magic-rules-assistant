from typing import Dict, Optional
from services import RuleService

class MessageHandler:
    def __init__(self, rule_service: RuleService):
        self.rule_service = rule_service

    def handle_text_message(self, user_message: str) -> str:
        """处理文本消息"""
        # 移除前后空格
        message = user_message.strip()

        # 检查是否是命令
        if message.startswith("/"):
            return self._handle_command(message)

        # 检查是否是卡牌查询
        if message.startswith("卡牌:") or message.startswith("card:"):
            card_name = message.split(":", 1)[1].strip()
            return self._handle_card_query(card_name)

        # 检查是否是关键词异能查询
        if message.startswith("异能:") or message.startswith("ability:"):
            keyword = message.split(":", 1)[1].strip()
            return self._handle_keyword_query(keyword)

        # 默认进行规则搜索
        return self._handle_rule_search(message)

    def _handle_command(self, command: str) -> str:
        """处理命令"""
        cmd = command.lower()

        if cmd == "/help" or cmd == "/帮助":
            return self._get_help_message()

        elif cmd == "/start":
            return self._get_welcome_message()

        else:
            return "未知命令。输入 /help 查看可用命令。"

    def _handle_card_query(self, card_name: str) -> str:
        """处理卡牌查询"""
        card_rule = self.rule_service.get_card_rule(card_name)

        if card_rule:
            response = f"🎴 {card_rule['card_name']}\n"
            response += f"类型: {card_rule['card_type']}\n"
            response += f"\n规则文本:\n{card_rule['oracle_text']}"

            if card_rule['related_rules']:
                response += f"\n\n相关规则: {', '.join(card_rule['related_rules'])}"

            return response
        else:
            return f"未找到卡牌: {card_name}\n\n请检查卡牌名称是否正确，或尝试简化名称。"

    def _handle_keyword_query(self, keyword: str) -> str:
        """处理关键词异能查询"""
        ability = self.rule_service.get_keyword_ability(keyword)

        if ability:
            response = f"📌 {ability['keyword_name']}\n"
            response += f"{ability['description']}\n"
            response += f"\n完整规则:\n{ability['full_text']}"

            if ability['examples']:
                response += f"\n\n示例:\n"
                for i, example in enumerate(ability['examples'], 1):
                    response += f"{i}. {example}\n"

            return response
        else:
            return f"未找到关键词异能: {keyword}\n\n请检查关键词名称是否正确。"

    def _handle_rule_search(self, query: str) -> str:
        """处理规则搜索"""
        search_results = self.rule_service.search_rules(query)
        return self.rule_service.format_response(search_results)

    def _get_help_message(self) -> str:
        """获取帮助信息"""
        help_text = """
🃏 万智牌规则助手使用指南

【基础功能】
• 直接输入问题: 我会搜索相关规则
• 输入卡牌名: 查询卡牌规则文本
• 输入异能名: 查询关键词异能解释

【快捷命令】
• 卡牌:卡牌名称 - 快速查询卡牌
• 异能:异能名称 - 快速查询异能
• /help - 显示此帮助信息
• /start - 显示欢迎信息

【示例】
• "飞行" 或 "异能:飞行"
• "黑莲花" 或 "卡牌:黑莲花"
• "先攻是什么"
• "堆栈怎么工作"

如需更多帮助，请关注我们的公众号获取最新资讯！
"""
        return help_text

    def _get_welcome_message(self) -> str:
        """获取欢迎信息"""
        welcome_text = """
🎉 欢迎使用万智牌规则助手！

我是你的专属规则顾问，随时为你解答万智牌相关问题。

【我能帮你做什么】
✓ 查询卡牌规则文本
✓ 解释关键词异能
✓ 搜索综合规则
✓ 解答规则疑问

【快速开始】
• 输入卡牌名称查询规则
• 输入"飞行"、"践踏"等查询异能
• 输入问题，如"先攻是什么"

输入 /help 查看详细使用指南

祝你游戏愉快！🎴
"""
        return welcome_text

    def handle_event(self, event_type: str) -> Optional[str]:
        """处理事件消息"""
        if event_type == "subscribe":
            return self._get_welcome_message()
        elif event_type == "unsubscribe":
            return None  # 取消关注不需要回复
        else:
            return None
