#!/usr/bin/env python3
"""
将解析后的规则数据导入数据库
"""
import sys
sys.path.append('./backend')

from database import RuleDatabase
from services.rule_downloader import RuleDownloader

def main():
    """主函数"""
    print("=" * 60)
    print("📝 数据库导入工具")
    print("=" * 60)
    
    # 下载并解析规则
    print("\n📥 下载并解析规则...")
    downloader = RuleDownloader()
    result = downloader.download_rules(force=True)
    
    if not result["success"]:
        print(f"❌ 下载失败: {result.get('message')}")
        return
    
    parse_result = downloader.parse_rules()
    
    if not parse_result["success"]:
        print(f"❌ 解析失败: {parse_result.get('message')}")
        return
    
    print(f"✅ 解析成功!")
    print(f"   规则条目: {len(parse_result['rules'])}")
    print(f"   关键词异能: {len(parse_result['keyword_abilities'])}")
    print(f"   术语表: {len(parse_result['glossary'])}")
    
    # 导入数据库
    print(f"\n💾 开始导入数据库...")
    db = RuleDatabase()
    
    try:
        # 重建数据库（删除旧文件）
        import os
        if os.path.exists(db.db_path):
            os.remove(db.db_path)
            print("✅ 已清空旧数据库")
        
        # 重新初始化
        db._init_database()
        
        # 导入规则
        print(f"💾 导入规则...")
        for rule in parse_result['rules']:
            db.insert_rule(
                rule['rule_number'],
                rule.get('title', ''),
                rule['content'],
                rule.get('category')
            )
        print(f"✅ 导入规则: {len(parse_result['rules'])} 条")
        
        # 导入关键词
        print(f"💾 导入关键词...")
        for keyword in parse_result['keyword_abilities']:
            db.insert_keyword_ability(
                keyword['keyword_name'],
                keyword['description'],
                keyword['full_text'],
                keyword.get('examples')
            )
        print(f"✅ 导入关键词: {len(parse_result['keyword_abilities'])} 条")
        
        print(f"\n✅ 数据库导入完成!")
        
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
