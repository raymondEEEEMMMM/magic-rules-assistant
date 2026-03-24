#!/usr/bin/env python3
"""
导入英文关键词数据到 keyword_abilities_v2 表
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

def parse_english_glossary(filepath):
    """解析英文 glossary 文件"""
    keywords = {}

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

        # 提取描述 - 英文描述在中文描述之前
        lines = section.split('\n')
        descriptions_en = []
        descriptions_cn = []

        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue

            # 跳过标题行和分隔符
            if line.startswith('#') or line.startswith('----'):
                continue

            # 描述行包含两个句子，用 "   " 分隔
            # 格式: 英文描述。   中文描述。

            # 检测是否包含中文
            has_cn = bool(re.search(r'[\u4e00-\u9fff]', line))

            if has_cn:
                # 分割英文和中文
                parts = re.split(r'\s{2,}', line)
                for part in parts:
                    part = part.strip()
                    if not part:
                        continue
                    if re.search(r'[\u4e00-\u9fff]', part):
                        descriptions_cn.append(part)
                    else:
                        descriptions_en.append(part)
            else:
                # 纯英文行
                if line and not line.startswith('See rule'):
                    descriptions_en.append(line)

        # 清理描述
        description_en = ' '.join(descriptions_en).strip()
        description_cn = ' '.join(descriptions_cn).strip()

        # 提取规则引用 - 查找 "See rule X" 或 "参见规则X"
        rule_ref_en = ''
        rule_ref_cn = ''

        # 英文规则引用
        en_rule_match = re.search(r'See rule\[?(\d+(?:\.\d+)?)\]?', section)
        if en_rule_match:
            rule_ref_en = f"Rule {en_rule_match.group(1)}"

        # 中文规则引用
        cn_rule_match = re.search(r'参见规则\[?(\d+(?:\.\d+)?)\]?', section)
        if cn_rule_match:
            rule_ref_cn = f"规则{cn_rule_match.group(1)}"

        keywords[keyword_en] = {
            'keyword_en': keyword_en,
            'keyword_cn': keyword_cn,
            'description_en': description_en,
            'description_cn': description_cn,
            'rule_ref_en': rule_ref_en,
            'rule_ref_cn': rule_ref_cn
        }

    return keywords

def main():
    # 解析英文 glossary
    filepath = '../data/knowledge/markdown/glossary.md'
    print(f"解析英文 glossary: {filepath}")
    en_keywords = parse_english_glossary(filepath)
    print(f"解析到 {len(en_keywords)} 个英文关键词")

    # 连接数据库
    conn = get_mysql_connection()

    try:
        with conn.cursor() as cursor:
            # 获取所有现有记录
            cursor.execute("SELECT id, keyword_cn, keyword_en FROM keyword_abilities_v2")
            existing_records = cursor.fetchall()

            update_count = 0

            for record in existing_records:
                cn = record['keyword_cn']
                en = record['keyword_en']

                # 尝试通过中文名查找对应的英文数据
                matched_en = None
                for key_en, data in en_keywords.items():
                    if data['keyword_cn'] == cn:
                        matched_en = data
                        break

                if not matched_en:
                    # 尝试通过已有的英文名查找
                    if en in en_keywords:
                        matched_en = en_keywords[en]

                if matched_en:
                    # 更新英文数据（如果还没有英文数据）
                    if not en or not record['keyword_en']:
                        cursor.execute("""
                            UPDATE keyword_abilities_v2
                            SET keyword_en = %s,
                                description_en = %s,
                                rule_ref_en = %s
                            WHERE id = %s
                        """, (
                            matched_en['keyword_en'],
                            matched_en['description_en'],
                            matched_en['rule_ref_en'],
                            record['id']
                        ))
                        update_count += 1
                        print(f"更新: {cn} -> {matched_en['keyword_en']}")

            conn.commit()
            print(f"共更新 {update_count} 条记录")

    finally:
        conn.close()

if __name__ == '__main__':
    main()
