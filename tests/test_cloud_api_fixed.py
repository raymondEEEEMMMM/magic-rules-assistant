#!/usr/bin/env python3
"""
测试修复后的云端 API
"""
import requests
import json
import time

# CloudBase 访问地址
BASE_URL = "https://magic-rules-assistant-0a1904c329-1410769303.ap-shanghai.app.tcloudbase.com"

def test_api(name, path, params=None):
    """测试 API 端点"""
    print(f"\n{'='*80}")
    print(f"测试: {name}")
    print(f"{'='*80}")
    
    url = f"{BASE_URL}{path}"
    try:
        response = requests.get(url, params=params, timeout=10)
        
        print(f"URL: {url}")
        if params:
            print(f"参数: {params}")
        
        print(f"状态码: {response.status_code}")
        
        try:
            data = response.json()
            print(f"响应内容:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # 判断是否成功
            if 'keyword' in data and 'result' in data:
                print(f"✅ 成功: 返回了关键词数据")
                return True
            elif 'query' in data and 'results' in data:
                print(f"✅ 成功: 返回了搜索结果")
                return True
            elif 'error' in data:
                print(f"❌ 失败: {data['error']}")
                return False
            else:
                print(f"⚠️ 未知响应格式")
                return False
        except json.JSONDecodeError:
            print(f"响应不是 JSON 格式: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

def main():
    print("万智牌规则问答 API - 云端测试")
    print("="*80)
    
    results = []
    
    # 测试 1: 关键词查询
    results.append(test_api(
        "关键词查询 (/api/keyword)",
        "/api/keyword",
        {"k": "飞行"}
    ))
    
    time.sleep(1)
    
    # 测试 2: 规则搜索
    results.append(test_api(
        "规则搜索 (/api/search)",
        "/api/search",
        {"q": "践踏"}
    ))
    
    time.sleep(1)
    
    # 测试 3: 卡牌查询
    results.append(test_api(
        "卡牌查询 (/api/card)",
        "/api/card",
        {"n": "黑莲花"}
    ))
    
    time.sleep(1)
    
    # 测试 4: MTGCH 卡牌搜索（测试依赖）
    results.append(test_api(
        "MTGCH 卡牌搜索 (/api/mtgch/search)",
        "/api/mtgch/search",
        {"q": "闪电风暴"}
    ))
    
    time.sleep(1)
    
    # 测试 5: MTGCH 随机卡牌
    results.append(test_api(
        "MTGCH 随机卡牌 (/api/mtgch/random)",
        "/api/mtgch/random"
    ))
    
    # 总结
    print(f"\n{'='*80}")
    print(f"测试总结")
    print(f"{'='*80}")
    
    total = len(results)
    success = sum(results)
    failed = total - success
    
    print(f"总计: {total} 个测试")
    print(f"成功: {success} 个")
    print(f"失败: {failed} 个")
    print(f"成功率: {success/total*100:.1f}%")
    
    if failed > 0:
        print(f"\n失败的测试:")
        print("-"*80)
        test_names = [
            "关键词查询",
            "规则搜索",
            "卡牌查询",
            "MTGCH 卡牌搜索",
            "MTGCH 随机卡牌"
        ]
        for i, result in enumerate(results):
            if not result:
                print(f"  ❌ {test_names[i]}")

if __name__ == "__main__":
    main()
