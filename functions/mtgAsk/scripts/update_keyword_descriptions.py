#!/usr/bin/env python3
"""
更新关键词描述脚本
从 Magic Comprehensive Rules 文件中提取关键词描述并更新数据库
"""
import os
import re
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def parse_keyword_descriptions(rules_file):
    """从规则文件中解析关键词描述"""
    keyword_descriptions = {}

    with open(rules_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 匹配 702.X. 开头的关键词规则
    # 格式: 702.2a Deathtouch is a static ability.
    pattern = r'(702\.\d+[a-z]?)\s+([A-Z][a-zA-Z\s\-]+?)\s+(.+?)(?=\n702\.\d|\n\d+\. |\Z)'

    matches = re.findall(pattern, content, re.DOTALL)

    for match in matches:
        rule_num = match[0]
        keyword = match[1].strip()
        description = match[2].strip()

        # 清理关键词名称
        keyword = keyword.rstrip('-')

        if keyword and description:
            # 取第一句话作为简要描述
            brief = description.split('.')[0] + '.'
            keyword_descriptions[keyword] = {
                'rule_num': rule_num,
                'brief': brief,
                'full': description[:500]  # 限制长度
            }

    return keyword_descriptions

def main():
    rules_file = os.path.join(
        os.path.dirname(__file__),
        'backend', 'data', 'rules',
        'MagicCompRules 20260227.txt'
    )

    if not os.path.exists(rules_file):
        print(f"规则文件不存在: {rules_file}")
        return

    print(f"正在解析规则文件: {rules_file}")
    keyword_descriptions = parse_keyword_descriptions(rules_file)

    print(f"找到 {len(keyword_descriptions)} 个关键词描述")

    # 显示前10个关键词
    print("\n前10个关键词描述示例:")
    for i, (keyword, info) in enumerate(list(keyword_descriptions.items())[:10]):
        print(f"  {keyword}: {info['brief'][:80]}...")

    # 保存到文件供后续使用
    output_file = os.path.join(
        os.path.dirname(__file__),
        'backend', 'data', 'keyword_descriptions.json'
    )

    import json
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(keyword_descriptions, f, ensure_ascii=False, indent=2)

    print(f"\n关键词描述已保存到: {output_file}")

if __name__ == '__main__':
    main()
