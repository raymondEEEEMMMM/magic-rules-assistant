#!/usr/bin/env python3
"""本地测试规则搜索功能"""
import sys
import os

# 添加路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'functions', 'magic-rules-api', 'backend'))

from database import RuleDatabase
from services import RuleService

def test_search():
    print("=== 测试规则搜索 ===")
    
    # 初始化数据库
    db = RuleDatabase('/Users/lianghaoming/cbworkplace/data/magic_rules.db')
    print(f"数据库路径: {db.db_path}")
    
    # 测试规则搜索
    rule_service = RuleService(db)
    results = rule_service.search_rules('combat')
    
    print(f"\n搜索 'combat' 结果:")
    print(f"- 规则数: {len(results.get('rules', []))}")
    print(f"- 关键词异能: {len(results.get('keyword_abilities', []))}")
    print(f"- 卡牌: {len(results.get('cards', []))}")
    print(f"- 问答模板: {len(results.get('qa_templates', []))}")
    
    # 显示第一条规则
    if results.get('rules'):
        rule = results['rules'][0]
        print(f"\n示例规则: {rule['rule_number']} - {rule['rule_title']}")
    
    # 测试关键词查询
    print("\n=== 测试关键词查询 ===")
    kw = rule_service.get_keyword_ability('Flying')
    if kw:
        print(f"找到关键词: {kw['keyword_name']}")
        print(f"描述: {kw['description'][:100]}...")
    else:
        print("未找到关键词 'Flying'")

if __name__ == '__main__':
    test_search()
