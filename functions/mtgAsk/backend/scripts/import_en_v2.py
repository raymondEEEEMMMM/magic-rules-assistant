#!/usr/bin/env python3
"""
导入英文关键词数据到 keyword_abilities_v2 表 - 改进版
"""
import re
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pymysql

def get_mysql_connection():
    """获取MySQL连接"""
    # 本地调试配置
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

def parse_english_glossary_v2(filepath):
    """解析英文 glossary 文件 - 改进版"""
    keywords_map = {}  # key: 中文名 -> 英文数据
    en_keywords_map = {}  # key: 英文名 -> 英文数据

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 分割每个词汇条目
    sections = content.split('----')

    for section in sections:
        section = section.strip()
        if not section:
            continue

        # 匹配格式: ### <span id='Keyword'>Keyword</span> / <span id='中文'>中文</span>
        title_match = re.search(r"###.*?<span id='([^']+)'>([^<]+)</span>.*?<span id='([^']+)'>([^<]+)</span>", section)
        if not title_match:
            continue

        keyword_en = title_match.group(2).strip()
        keyword_cn = title_match.group(4).strip()

        # 提取描述 - 英文描述在中文描述之后，用 "   " 分隔
        lines = section.split('\n')
        description_en = ''
        description_cn = ''

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line.startswith('#') or line.startswith('----'):
                continue

            # 分割英文和中文部分
            parts = re.split(r'\s{2,}', line)
            for part in parts:
                part = part.strip()
                if not part:
                    continue

                # 如果包含中文，就是中文描述
                if re.search(r'[\u4e00-\u9fff]', part):
                    if description_cn:
                        description_cn += ' '
                    description_cn += part
                elif part.startswith('See rule'):
                    # 规则引用
                    pass
                else:
                    if description_en:
                        description_en += ' '
                    description_en += part

        # 提取规则引用
        rule_ref_en = ''
        rule_ref_cn = ''

        # 英文规则引用 - See rule 702.9
        en_rule_match = re.search(r'See rule (\d+(?:\.\d+)?)', section, re.IGNORECASE)
        if en_rule_match:
            rule_ref_en = f"Rule {en_rule_match.group(1)}"

        # 中文规则引用 - 参见规则702.9
        cn_rule_match = re.search(r'参见规则(\d+(?:\.\d+)?)', section)
        if cn_rule_match:
            rule_ref_cn = f"规则{cn_rule_match.group(1)}"

        data = {
            'keyword_en': keyword_en,
            'keyword_cn': keyword_cn,
            'description_en': description_en.strip(),
            'description_cn': description_cn.strip(),
            'rule_ref_en': rule_ref_en,
            'rule_ref_cn': rule_ref_cn
        }

        keywords_map[keyword_cn] = data
        en_keywords_map[keyword_en] = data

    return keywords_map, en_keywords_map

def main():
    # 解析英文 glossary
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    filepath = os.path.join(base_dir, 'data/knowledge/markdown/glossary.md')
    print(f"解析英文 glossary: {filepath}")
    cn_map, en_map = parse_english_glossary_v2(filepath)
    print(f"解析到 {len(cn_map)} 个中文关键词, {len(en_map)} 个英文关键词")

    # 连接数据库
    conn = get_mysql_connection()

    try:
        with conn.cursor() as cursor:
            # 获取所有现有记录
            cursor.execute("SELECT id, keyword_cn, keyword_en, description_en FROM keyword_abilities_v2")
            existing_records = cursor.fetchall()

            update_count = 0

            for record in existing_records:
                cn = record['keyword_cn']
                current_en = record['keyword_en']
                current_desc_en = record['description_en']

                # 优先通过中文名匹配
                matched_data = None
                if cn and cn in cn_map:
                    matched_data = cn_map[cn]
                elif current_en and current_en in en_map:
                    matched_data = en_map[current_en]

                if matched_data:
                    # 强制更新英文数据
                    cursor.execute("""
                        UPDATE keyword_abilities_v2
                        SET keyword_en = %s,
                            description_en = %s,
                            rule_ref_en = %s
                        WHERE id = %s
                    """, (
                        matched_data['keyword_en'],
                        matched_data['description_en'],
                        matched_data['rule_ref_en'],
                        record['id']
                    ))
                    update_count += 1
                    print(f"更新 [{cn}] -> [{matched_data['keyword_en']}]")

            conn.commit()
            print(f"\n共更新 {update_count} 条记录")

    finally:
        conn.close()

if __name__ == '__main__':
    main()
