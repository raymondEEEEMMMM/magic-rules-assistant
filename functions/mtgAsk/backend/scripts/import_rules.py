#!/usr/bin/env python3
"""
导入规则数据到 rules_v2 表
解析中文规则文件 1.md~9.md，提取规则编号、标题和内容

支持从 Cloud Storage 下载:
- 存储路径: mtgAsk/rules/markdown/1.md ~ 9.md
"""
import re
import os
import sys
import json
import requests
from typing import List, Dict, Optional, Tuple

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pymysql


# Cloud Storage 配置
STORAGE_BASE_URL = "https://6d61-magic-rules-assistant-0a1904c329-1410769303.tcb.qcloud.la"
STORAGE_RULES_PATH = "mtgAsk/rules/markdown"

# 规则文件列表 (1-9章)
RULE_FILES = [f"{i}.md" for i in range(1, 10)]


def backup_rules_table():
    """备份当前 rules_v2 表数据到 rules_backup 表"""
    import time
    conn = get_mysql_connection()
    try:
        with conn.cursor() as cursor:
            # 创建备份表（如果不存在）并复制数据
            # 使用时间戳作为备份标识
            backup_table = f"rules_backup_{int(time.time())}"

            # 先删除旧备份表（保留最近3个）
            try:
                cursor.execute("""
                    SELECT table_name FROM information_schema.tables
                    WHERE table_schema = DATABASE() AND table_name LIKE 'rules_backup_%'
                    ORDER BY table_name DESC
                """)
                all_rows = cursor.fetchall()
                # 尝试使用字典访问或索引访问
                if all_rows:
                    try:
                        old_backups = [row['table_name'] for row in all_rows]
                    except (KeyError, TypeError):
                        old_backups = [row[0] for row in all_rows]
                else:
                    old_backups = []
                if len(old_backups) >= 3:
                    for old_table in old_backups[2:]:
                        cursor.execute(f"DROP TABLE IF EXISTS {old_table}")
            except Exception as e:
                print(f"  清理旧备份表失败（跳过）: {e}")

            # 创建备份表并复制数据
            try:
                cursor.execute(f"CREATE TABLE {backup_table} LIKE rules_v2")
                cursor.execute(f"INSERT INTO {backup_table} SELECT * FROM rules_v2")
                conn.commit()

                # 统计备份数量
                cursor.execute(f"SELECT COUNT(*) FROM {backup_table}")
                result = cursor.fetchone()
                count = result[0] if isinstance(result, tuple) else result.get('COUNT(*)', 0)
                print(f"✓ 备份成功: {backup_table} ({count} 条规则)")
                return backup_table, count
            except Exception as e:
                print(f"  备份失败（继续导入）: {e}")
                return None, 0
    finally:
        conn.close()


def download_from_storage(filename: str, timeout: int = 60) -> Tuple[Optional[str], Optional[str]]:
    """
    从 Cloud Storage 下载文件

    Returns:
        (content, error_message)
    """
    url = f"{STORAGE_BASE_URL}/{STORAGE_RULES_PATH}/{filename}"
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            # 显式指定 UTF-8 编码，避免 requests 自动检测错误
            response.encoding = 'utf-8'
            return response.text, None
        else:
            return None, f"HTTP {response.status_code}"
    except requests.exceptions.Timeout:
        return None, "Timeout"
    except requests.exceptions.RequestException as e:
        return None, str(e)


def download_all_rule_files() -> Tuple[List[Dict], List[str]]:
    """
    下载所有规则文件，确保完整性

    Returns:
        (file_contents, errors)
        file_contents = [{"filename": "1.md", "content": "...", "size": 123}, ...]
    """
    file_contents = []
    errors = []

    print("=" * 50)
    print("从 Cloud Storage 下载规则文件")
    print(f"路径: {STORAGE_BASE_URL}/{STORAGE_RULES_PATH}/")
    print("=" * 50)

    for filename in RULE_FILES:
        print(f"下载: {filename}...", end=" ", flush=True)
        content, error = download_from_storage(filename)

        if error:
            print(f"失败 ({error})")
            errors.append(f"{filename}: {error}")
        else:
            size = len(content)
            # 简单验证：内容不应太小 (每个文件至少 10KB)
            if size < 10000:
                print(f"警告 (内容过小: {size} 字节)")
                errors.append(f"{filename}: 内容过小 ({size} 字节)")
            else:
                print(f"成功 ({size} 字节)")
                file_contents.append({
                    "filename": filename,
                    "content": content,
                    "size": size
                })

    print()
    print(f"下载完成: {len(file_contents)}/{len(RULE_FILES)} 个文件")

    if errors:
        print("\n下载问题:")
        for err in errors:
            print(f"  - {err}")

    return file_contents, errors


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
        cursorclass=pymysql.cursors.DictCursor,
        use_unicode=True
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

    规则文件格式:
    - ## <span id='cr100'>100.</span> 章节标题 (章节头，不是规则)
    - <b id='cr100-1'>100.1.</b> 内容 (规则)
    - <b id='cr100-1a'>100.1a</b> 子规则

    关键词异能格式 (702.x):
    - ## <span id='cr702-9'>702.9. 飞行 Flying</span> (这是主规则!)
    - <b id='cr702-9a'>702.9a</b> 子规则
    """
    rules = []

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 按 ## 分割章节
    sections = re.split(r'^## ', content, flags=re.MULTILINE)

    for section in sections:
        if not section.strip():
            continue

        # 分割所有块
        rule_blocks = re.split(r'(?=<(?:span|b) id=[\'"]?cr)', section)

        i = 0
        while i < len(rule_blocks):
            block = rule_blocks[i]

            # 检查是否是 span 块
            # id格式可能是 cr702-9 (hyphen) 或 cr100 (no hyphen)
            # 需要将 cr702-9 转换为 702.9
            span_match = re.match(r'\s*<span id=[\'"]?cr([\d]+(?:-[\d]+)?)', block)

            if span_match:
                span_num = span_match.group(1).replace('-', '.')
                # span_num like "702.9" or "100"
                # 如果是完整的规则号（如 702.9），合并后续的子规则块
                # 如果只是章节号（如 702），则合并后续规则
                merged = block
                j = i + 1

                while j < len(rule_blocks):
                    next_block = rule_blocks[j]
                    # 检查下一个块的规则号
                    next_match = re.match(r'\s*<b id=[\'"]?cr([\d]+(?:-[\d]+)?[a-z]?)', next_block)
                    if not next_match:
                        next_match = re.match(r'\s*<span id=[\'"]?cr([\d]+(?:-[\d]+)?)', next_block)

                    if next_match:
                        next_num = next_match.group(1).replace('-', '.')
                        # 检查是否是 <span> 块（新的规则/章节开始），如果是则停止合并
                        is_next_span = next_block.strip().startswith('<span')
                        if is_next_span:
                            # 遇到新的 span 块，停止合并
                            break
                        # 只有 <b> 块才能合并
                        # 检查编号是否匹配（用于决定是否继续合并）
                        # 702.9 后面跟 702.9a, 702.9b -> 合并
                        # 702 后面跟 702.1a 等 -> 合并
                        if next_num.startswith(span_num) and (len(next_num) == len(span_num) or next_num[len(span_num)] in 'abcdefghijklmnopqrstuvwxyz'):
                            merged += '\n' + next_block
                            j += 1
                        else:
                            break
                    else:
                        break

                merged_blocks = [merged]
                # 解析合并后的块
                rule = parse_rule_section(merged_blocks[0])
                if rule:
                    rules.append(rule)
                i = j
            else:
                # 非 span 块（纯 b 块），直接解析
                if block.strip():
                    rule = parse_rule_section(block)
                    if rule:
                        rules.append(rule)
                i += 1

    return rules


def parse_rule_content(content: str) -> List[Dict]:
    """
    解析规则内容字符串

    直接解析传入的 markdown 内容字符串，返回规则列表
    """
    rules = []

    # 按 ## 分割章节
    sections = re.split(r'^## ', content, flags=re.MULTILINE)

    for section in sections:
        if not section.strip():
            continue

        # 分割所有块
        rule_blocks = re.split(r'(?=<(?:span|b) id=[\'"]?cr)', section)

        i = 0
        while i < len(rule_blocks):
            block = rule_blocks[i]

            # 检查是否是 span 块
            span_match = re.match(r'\s*<span id=[\'"]?cr([\d]+(?:-[\d]+)?)', block)

            if span_match:
                span_num = span_match.group(1).replace('-', '.')
                merged = block
                j = i + 1

                while j < len(rule_blocks):
                    next_block = rule_blocks[j]
                    next_match = re.match(r'\s*<b id=[\'"]?cr([\d]+(?:-[\d]+)?[a-z]?)', next_block)
                    if not next_match:
                        next_match = re.match(r'\s*<span id=[\'"]?cr([\d]+(?:-[\d]+)?)', next_block)

                    if next_match:
                        next_num = next_match.group(1).replace('-', '.')
                        is_next_span = next_block.strip().startswith('<span')
                        if is_next_span:
                            break
                        if next_num.startswith(span_num) and (len(next_num) == len(span_num) or next_num[len(span_num)] in 'abcdefghijklmnopqrstuvwxyz'):
                            merged += '\n' + next_block
                            j += 1
                        else:
                            break
                    else:
                        break

                merged_blocks = [merged]
                rule = parse_rule_section(merged_blocks[0])
                if rule:
                    rules.append(rule)
                i = j
            else:
                if block.strip():
                    rule = parse_rule_section(block)
                    if rule:
                        rules.append(rule)
                i += 1

    return rules


def parse_rule_file(filepath: str) -> List[Dict]:
    """解析本地规则文件（兼容旧接口）"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    return parse_rule_content(content)


def import_rules_from_storage() -> Dict:
    """
    从 Cloud Storage 下载规则文件并导入数据库

    Returns:
        导入结果字典
    """
    result = {
        "success": False,
        "downloaded_files": 0,
        "parsed_rules": 0,
        "inserted": 0,
        "errors": []
    }

    # 1. 备份现有数据
    print("步骤 1: 备份现有数据...")
    try:
        backup_table, backup_count = backup_rules_table()
        result["backup_table"] = backup_table
        result["backup_count"] = backup_count
    except Exception as e:
        result["errors"].append(f"备份失败: {str(e)}")
        return result

    # 2. 下载文件
    print("\n步骤 2: 下载规则文件...")
    file_contents = []
    download_errors = []

    for filename in RULE_FILES:
        print(f"下载: {filename}...", end=" ", flush=True)
        content, error = download_from_storage(filename)
        if error:
            print(f"失败 ({error})")
            download_errors.append(f"{filename}: {error}")
        else:
            size = len(content)
            if size < 10000:  # 每个文件至少 10KB
                print(f"警告 (内容过小: {size} 字节)")
                download_errors.append(f"{filename}: 内容过小 ({size} 字节)")
            else:
                print(f"成功 ({size} 字节)")
                file_contents.append({"filename": filename, "content": content})

    result["downloaded_files"] = len(file_contents)
    if download_errors:
        result["errors"].extend(download_errors)

    if len(file_contents) < len(RULE_FILES):
        result["errors"].append(f"下载不完整: {len(file_contents)}/{len(RULE_FILES)}")
        return result

    # 3. 解析规则
    print("\n步骤 3: 解析规则...")
    all_rules = []
    for fc in file_contents:
        rules = parse_rule_content(fc["content"])
        print(f"  {fc['filename']}: {len(rules)} 条规则")
        all_rules.extend(rules)

    result["parsed_rules"] = len(all_rules)

    # 4. 导入数据库
    print("\n步骤 4: 导入数据库...")
    conn = get_mysql_connection()
    try:
        with conn.cursor() as cursor:
            # 清空现有规则
            cursor.execute("DELETE FROM rules_v2")

            # 批量插入
            inserted = 0
            for rule in all_rules:
                try:
                    cursor.execute("""
                        INSERT INTO rules_v2
                        (rule_number, rule_title_cn, rule_title_en, rule_content_cn, rule_content_en)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (
                        rule['rule_number'],
                        rule['rule_title_cn'],
                        rule['rule_title_en'],
                        rule['rule_content_cn'],
                        rule['rule_content_en']
                    ))
                    inserted += 1
                except Exception as e:
                    pass  # 忽略重复键等错误

            conn.commit()
            result["inserted"] = inserted
            result["success"] = True
            print(f"✓ 成功导入 {inserted} 条规则")
    finally:
        conn.close()

    return result


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
