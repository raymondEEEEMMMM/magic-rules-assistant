#!/usr/bin/env python3
"""
测试本地 API 返回内容
"""
import sys
sys.path.insert(0, 'backend')

from database import RuleDatabase
from services import RuleService

# 初始化
db = RuleDatabase()
rule_service = RuleService(db)

# 测试关键词查询
keyword = '飞行'
print(f"测试: /api/keyword?k={keyword}")
print("="*60)

result = rule_service.get_keyword_ability(keyword)

print("\n完整返回内容:")
print("-"*60)
print(result)
print()

print("\nJSON 格式:")
print("-"*60)
import json
print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
print()

print("\n字段分析:")
print("-"*60)
if isinstance(result, dict):
    for key, value in result.items():
        print(f"  {key}:")
        if isinstance(value, str):
            print(f"    类型: str, 长度: {len(value)}")
            if len(value) > 100:
                print(f"    内容(前100字符): {value[:100]}...")
            else:
                print(f"    内容: {value}")
        elif isinstance(value, list):
            print(f"    类型: list, 数量: {len(value)}")
            if value:
                print(f"    第一个元素: {value[0]}")
        else:
            print(f"    类型: {type(value).__name__}")
            print(f"    内容: {value}")
    print()
    print(f"总计: {len(result)} 个字段")
else:
    print(f"  返回类型: {type(result)}")
    print(f"  内容: {result}")

print("\n" + "="*60)
print("测试完成")
