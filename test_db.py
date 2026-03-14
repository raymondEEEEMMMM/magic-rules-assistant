#!/usr/bin/env python3
"""测试数据库是否正常"""
import sys
sys.path.insert(0, '/Users/lianghaoming/cbworkplace/functions/magic-rules-api/backend')

from database import RuleDatabase

try:
    db = RuleDatabase('/Users/lianghaoming/cbworkplace/data/magic_rules.db')
    print(f"数据库路径: {db.db_path}")
    
    # 测试查询
    rules = db.search_by_keywords(['combat'])
    print(f"搜索 'combat': {len(rules)} 条规则")
    
    keywords = db.get_all_keywords()
    print(f"关键词数量: {len(keywords)}")
    print(f"示例关键词: {keywords[:5] if keywords else '无'}")
    
    # 测试关键词查询
    kw_ability = db.get_keyword_ability('Flying')
    print(f"查询 'Flying': {kw_ability['keyword_name'] if kw_ability else '未找到'}")
    
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
