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
    """解析单个规则章节"""
    if not section.strip():
        return None

    # 匹配规则编号和标题: ### <span id=cr702-9>702.9. 飞行 Flying</span>
    match = re.search(r'<span id=cr(\d+(?:\.\d+)?)[^>]*>(\d+(?:\.\d+)?)\.\s*([^<]+)</span>', section)
    if not match:
        return None

    rule_number = match.group(2)
    title_part = match.group(3).strip()  # 如 "飞行 Flying"

    # 分离中英文标题
    # 格式: "飞行 Flying" 或 "敏捷 Haste"
    title_cn = ''
    title_en = ''

    # 尝试分离中文和英文
    cn_en_match = re.match(r'([\u4e00-\u9fff]+)\s+([A-Za-z\s]+)', title_part)
    if cn_en_match:
        title_cn = cn_en_match.group(1).strip()
        title_en = cn_en_match.group(2).strip()
    else:
        # 如果没有中文，可能是纯英文
        if re.search(r'[\u4e00-\u9fff]', title_part):
            # 有中文但没分离开，当作中文
            title_cn = title_part
        else:
            title_en = title_part

    # 提取规则内容
    lines = section.split('\n')
    content_cn = []
    content_en = []

    # 跟踪当前是中文还是英文（交替）
    last_was_cn = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 跳过标题行
        if line.startswith('#') or '<span' in line:
            continue

        # 跳过规则编号行 (如 702.9a, 702.9b)
        if re.match(r'^\d+\.\d+[a-z]?\s', line):
            # 这是规则编号行，可能包含内容
            # 去掉编号部分
            line = re.sub(r'^\d+\.\d+[a-z]?\s*', '', line)

        # 判断是否是空行
        if not line:
            continue

        # 判断中英文
        has_cn = bool(re.search(r'[\u4e00-\u9fff]', line))
        has_en = bool(re.search(r'[A-Za-z]', line))

        if has_cn:
            content_cn.append(line)
            last_was_cn = True
        elif has_en:
            content_en.append(line)
            last_was_cn = False

    return {
        'rule_number': rule_number,
        'rule_title_cn': title_cn,
        'rule_title_en': title_en,
        'rule_content_cn': ' '.join(content_cn),
        'rule_content_en': ' '.join(content_en)
    }


def parse_rule_file(filepath):
    """解析规则文件"""
    rules = []

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 按 ### 分割章节
    sections = re.split(r'^### ', content, flags=re.MULTILINE)

    for section in sections:
        rule = parse_rule_section(section)
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
