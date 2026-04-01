#!/usr/bin/env python3
"""
导入规则数据到 rules_v2 表
解析中文规则文件 1.md~9.md，提取规则编号、标题和内容
"""
import re
import os
import sys

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pymysql


def get_mysql_connection():
    """获取MySQL连接"""
    host = os.environ.get('MYSQL_HOST', 'sh-cynosdbmysql-grp-5ydpqjru.sql.tencentcdb.com')
    port = int(os.environ.get('MYSQL_PORT', '27987'))
    user = os.environ.get('MYSQL_USER', 'mtgask')
    password = os.environ.get('MYSQL_PASSWORD', '')
    database = os.environ.get('MYSQL_DATABASE', 'magic-rules-assistant-0a1904c329')

    return pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )


def parse_rule_section(section):
    """解析单个规则章节

    支持两种格式:
    1. <span id='cr702-9'>702.9. 飞行 Flying</span> (关键词异能章节标题)
    2. <b id='cr603-1'>603.1.</b> 内容 (普通规则条目)
    """
    if not section.strip():
        return None

    # 尝试匹配 <span id='cr702-9'> 格式 (章节标题/关键词异能)
    span_match = re.search(r'<span id=[\'"]?cr(\d+(?:\.\d+)?)[^\'">]*[\'"]?\s*>(\d+(?:\.\d+)?)\.\s*([^<]+)</span>', section)
    if span_match:
        rule_number = span_match.group(2)
        title_part = span_match.group(3).strip()
        title_cn, title_en = split_title(title_part)
        # 内容从剩余部分提取
        content_cn, content_en = extract_content(section)
        return {
            'rule_number': rule_number,
            'rule_title_cn': title_cn,
            'rule_title_en': title_en,
            'rule_content_cn': content_cn,
            'rule_content_en': content_en
        }

    # 尝试匹配 <b id='cr603-1'> 格式 (普通规则)
    b_match = re.search(r'<b id=[\'"]?cr(\d+(?:\.\d+)?)[^\'">]*[\'"]?\s*>(\d+(?:\.\d+)?)\.\s*</b>', section)
    if b_match:
        rule_number = b_match.group(2)
        # 标题为空（普通规则条目没有独立标题）
        title_cn = ''
        title_en = ''
        # 内容紧跟在 </b> 后面
        content_cn, content_en = extract_content(section)
        return {
            'rule_number': rule_number,
            'rule_title_cn': title_cn,
            'rule_title_en': title_en,
            'rule_content_cn': content_cn,
            'rule_content_en': content_en
        }

    return None


def split_title(title_part):
    """分离中英文标题"""
    title_cn = ''
    title_en = ''
    cn_en_match = re.match(r'([\u4e00-\u9fff]+)\s+([A-Za-z\s]+)', title_part)
    if cn_en_match:
        title_cn = cn_en_match.group(1).strip()
        title_en = cn_en_match.group(2).strip()
    else:
        if re.search(r'[\u4e00-\u9fff]', title_part):
            title_cn = title_part
        else:
            title_en = title_part
    return title_cn, title_en


def extract_content(section):
    """从章节中提取中英文内容

    格式示例:
    <b id='cr100-1'>100.1.</b> 这些万智牌规则适用于...   \n
    <b>100.1.</b> These Magic rules...

    中文内容在 <b id='crXXX'>...</b> 标签后面的行
    英文内容在 <b>XXX.</b> 标签后面的行
    """
    cn_lines = []
    en_lines = []

    lines = section.split('\n')
    for line in lines:
        # 跳过标题行
        if line.startswith('#') or '<span' in line:
            continue

        # 提取 <b id='crXXX'>...</b>后面的中文内容
        # 格式: <b id='cr100-1'>100.1.</b> 中文内容
        match = re.match(r'<b[^>]*>[^<]*</b>\s*(.+)$', line)
        if match:
            text = match.group(1).strip()
            text = re.sub(r'<[^>]+>', '', text)  # 去掉残余标签
            text = re.sub(r'\s+', ' ', text).strip()
            if text:
                # 判断是中文还是英文
                if re.search(r'[\u4e00-\u9fff]', text):
                    cn_lines.append(text)
                else:
                    en_lines.append(text)

    return ' '.join(cn_lines), ' '.join(en_lines)


def parse_rule_file(filepath):
    """解析规则文件

    文件格式:
    - ## <span id='cr100'>100.</span> 章节标题 (章节头)
      <b id='cr100-1'>100.1.</b> 中文内容 (规则条目)
      <b>100.1.</b> English content
      <b id='cr100-1a'>100.1a</b> 中文内容 (子规则)
      <b>100.1a</b> English content
    """
    rules = []

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 按 ## 分割章节（## 是二级标题）
    sections = re.split(r'^## ', content, flags=re.MULTILINE)

    for section in sections:
        if not section.strip():
            continue

        # 从章节中提取所有规则
        # 匹配 <span id='cr...'> 或 <b id='cr...'> 格式
        # 分割每个规则条目
        rule_blocks = re.split(r'(?=<(?:span|b) id=[\'"]?cr)', section)

        for block in rule_blocks:
            if not block.strip():
                continue
            rule = parse_rule_section(block)
            if rule:
                rules.append(rule)

    return rules


def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    rules_dir = os.path.join(base_dir, 'data/magic-comp-rules-zh-cn-agent/markdown')

    all_rules = []

    # 遍历 1.md ~ 9.md
    for i in range(1, 10):
        filepath = os.path.join(rules_dir, f'{i}.md')
        print(f"解析文件: {filepath}")

        if not os.path.exists(filepath):
            print(f"  文件不存在，跳过")
            continue

        rules = parse_rule_file(filepath)
        print(f"  解析到 {len(rules)} 条规则")
        all_rules.extend(rules)

    print(f"\n共解析 {len(all_rules)} 条规则")

    # 连接数据库
    conn = get_mysql_connection()

    try:
        with conn.cursor() as cursor:
            # 批量插入
            insert_count = 0
            for rule in all_rules:
                try:
                    cursor.execute("""
                        INSERT IGNORE INTO rules_v2
                        (rule_number, rule_title_cn, rule_title_en, rule_content_cn, rule_content_en)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (
                        rule['rule_number'],
                        rule['rule_title_cn'],
                        rule['rule_title_en'],
                        rule['rule_content_cn'],
                        rule['rule_content_en']
                    ))
                    insert_count += 1
                except Exception as e:
                    print(f"  插入失败: {rule['rule_number']} - {e}")

            conn.commit()
            print(f"\n成功插入 {insert_count} 条规则")

            # 显示一些示例
            print("\n示例数据:")
            cursor.execute("SELECT rule_number, rule_title_cn, rule_title_en FROM rules_v2 LIMIT 5")
            for row in cursor.fetchall():
                print(f"  {row['rule_number']}: {row['rule_title_cn']} / {row['rule_title_en']}")

    finally:
        conn.close()


if __name__ == '__main__':
    main()
