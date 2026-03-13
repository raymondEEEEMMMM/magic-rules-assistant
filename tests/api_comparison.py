#!/usr/bin/env python3
"""
对比本地和云端 API 返回值
"""
import sys
sys.path.insert(0, 'backend')

import json
import requests
from database import RuleDatabase
from services import RuleService

# CloudBase 访问地址
BASE_URL = "https://magic-rules-assistant-0a1904c329-1410769303.ap-shanghai.app.tcloudbase.com"

def get_local_result(keyword):
    """获取本地 API 结果"""
    db = RuleDatabase()
    rule_service = RuleService(db)
    result = rule_service.get_keyword_ability(keyword)
    return {
        "keyword": keyword,
        "result": result
    }

def get_cloud_result(keyword):
    """获取云端 API 结果"""
    url = f"{BASE_URL}/api/keyword?k={keyword}"
    try:
        response = requests.get(url, timeout=10)
        return {
            "status_code": response.status_code,
            "text": response.text,
            "json": response.json() if response.headers.get('content-type', '').startswith('application/json') else None
        }
    except Exception as e:
        return {
            "error": str(e)
        }

def compare_results(keyword):
    """对比本地和云端结果"""
    print(f"{'='*80}")
    print(f"对比测试: /api/keyword?k={keyword}")
    print(f"{'='*80}\n")

    # 本地结果
    print("【本地结果】")
    print("-"*80)
    local_result = get_local_result(keyword)
    print(json.dumps(local_result, indent=2, ensure_ascii=False, default=str))

    # 云端结果
    print("\n【云端结果】")
    print("-"*80)
    cloud_result = get_cloud_result(keyword)
    if "error" in cloud_result:
        print(f"错误: {cloud_result['error']}")
    else:
        print(f"状态码: {cloud_result['status_code']}")
        print(f"响应文本: {cloud_result['text']}")
        if cloud_result['json']:
            print(f"\nJSON 内容:")
            print(json.dumps(cloud_result['json'], indent=2, ensure_ascii=False))

    # 对比分析
    print("\n【对比分析】")
    print("-"*80)

    if "error" in cloud_result:
        print("❌ 云端请求失败，无法对比")
        return

    if cloud_result['status_code'] != 200:
        print(f"❌ 云端返回状态码: {cloud_result['status_code']}，预期 200")
        print(f"   可能原因:")
        print(f"   1. 路径配置问题")
        print(f"   2. 函数代码未正确部署")
        print(f"   3. HTTP 访问配置错误")
        return

    if not cloud_result['json']:
        print("❌ 云端返回的不是 JSON 格式")
        return

    # 对比关键字段
    cloud_json = cloud_result['json']
    print(f"云端返回字段: {cloud_json.keys()}")

    if 'result' in cloud_json:
        cloud_result_data = cloud_json['result']
        if isinstance(cloud_result_data, dict):
            print(f"\n云端 result 字段内容: {cloud_result_data.keys()}")

            # 对比具体字段
            print("\n字段对比:")
            for key in local_result['result'].keys():
                local_value = local_result['result'][key]
                cloud_value = cloud_result_data.get(key)

                if local_value == cloud_value:
                    print(f"  ✅ {key}: 一致")
                else:
                    print(f"  ❌ {key}: 不一致")
                    print(f"     本地: {local_value}")
                    print(f"     云端: {cloud_value}")
        else:
            print(f"❌ 云端 result 不是字典类型: {type(cloud_result_data)}")
    else:
        print("❌ 云端返回中没有 'result' 字段")
        print(f"   实际字段: {cloud_json.keys()}")

    print("\n【总结】")
    print("-"*80)

if __name__ == "__main__":
    keywords = ["飞行", "践踏", "先攻"]

    for keyword in keywords:
        compare_results(keyword)
        print()
