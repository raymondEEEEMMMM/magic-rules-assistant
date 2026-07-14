from typing import List, Dict, Optional
import re
from database import RuleDatabase

class RuleService:
    def __init__(self, db: RuleDatabase):
        self.db = db

    def search_rules(self, query: str) -> Dict:
        """
        综合搜索规则
        """
        # 提取关键词
        keywords = self._extract_keywords(query)

        results = {
            "query": query,
            "rules": [],
            "keyword_abilities": [],
            "cards": [],
            "qa_templates": []
        }

        # 1. 搜索关键词异能
        for keyword in keywords:
            keyword_ability = self.db.get_keyword_ability(keyword)
            if keyword_ability:
                results["keyword_abilities"].append(keyword_ability)

        # 2. 文本搜索规则
        rules = self.db.search_by_keywords(keywords)
        if rules:
            results["rules"] = rules

        # 3. 搜索卡牌
        for keyword in keywords:
            card_rule = self.db.get_card_rule(keyword)
            if card_rule:
                results["cards"].append(card_rule)
                break  # 只返回最匹配的一个

        # 4. 搜索问答模板
        qa_templates = self.db.search_qa_templates(keywords)
        if qa_templates:
            results["qa_templates"] = qa_templates[:2]

        return results

    def _extract_rule_number(self, rule_ref: str) -> Optional[str]:
        """从规则引用中提取规则编号，如 'Rule 702.9' -> '702.9' 或 '规则702.9' -> '702.9'"""
        # 匹配 702.9, 101.1a 等格式
        match = re.search(r'(\d+(?:\.\d+)?[a-z]?)', rule_ref)
        return match.group(1) if match else None

    def get_keyword_ability(self, keyword: str) -> Optional[Dict]:
        """获取关键词异能"""
        return self.db.get_keyword_ability(keyword)

    def get_card_rule(self, card_name: str) -> Optional[Dict]:
        """获取卡牌规则"""
        return self.db.get_card_rule(card_name)

    def _extract_keywords(self, query: str) -> List[str]:
        """从查询中提取关键词"""
        # 简单实现：按空格分词
        # TODO: 后续可以用jieba等分词工具优化
        keywords = query.split()
        # 过滤掉常见停用词
        stop_words = {"的", "是", "在", "有", "和", "与", "了", "呢", "吗", "什么", "怎么", "如何"}
        keywords = [k for k in keywords if k not in stop_words and len(k) > 1]
        return keywords[:5]  # 限制关键词数量

    def format_response(self, search_results: Dict) -> str:
        """格式化搜索结果为可读文本"""
        response = []

        if search_results["keyword_abilities"]:
            ability = search_results["keyword_abilities"][0]
            response.append(f"📌 {ability['keyword_name']}")
            response.append(f"{ability['description']}")
            response.append(f"\n完整规则:\n{ability['full_text']}")

        elif search_results["cards"]:
            card = search_results["cards"][0]
            response.append(f"🎴 {card['card_name']}")
            response.append(f"类型: {card['card_type']}")
            response.append(f"\n规则文本:\n{card['oracle_text']}")

        elif search_results["qa_templates"]:
            qa = search_results["qa_templates"][0]
            response.append(f"❓ {qa['question']}")
            response.append(f"\n{qa['answer']}")

        elif search_results["rules"]:
            rule = search_results["rules"][0]
            response.append(f"📖 规则 {rule['rule_number']}: {rule['rule_title']}")
            response.append(f"\n{rule['rule_content']}")

        else:
            response.append("抱歉，没有找到相关规则。")
            response.append("\n您可以:")
            response.append("1. 输入卡牌名称查询卡牌规则")
            response.append("2. 输入关键词异能（如：飞行、践踏）")
            response.append("3. 描述规则问题，我会尽力帮助您")

        return "\n".join(response)
