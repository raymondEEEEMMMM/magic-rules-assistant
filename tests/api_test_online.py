#!/usr/bin/env python3
"""
测试 CloudBase 外网业务 API
"""
import requests
import json

# CloudBase 访问地址
BASE_URL = "https://magic-rules-assistant-0a1904c329-1410769303.ap-shanghai.app.tcloudbase.com"

def test_endpoint(name, url, description=""):
    """测试单个端点"""
    try:
        print(f"\n{'='*60}")
        print(f"测试: {name}")
        print(f"URL: {url}")
        if description:
            print(f"说明: {description}")
        print(f"{'='*60}")
        
        response = requests.get(url, timeout=10)
        
        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        print(f"响应内容:")
        print(response.text)
        
        try:
            json_data = response.json()
            print(f"\nJSON 格式:")
            print(json.dumps(json_data, indent=2, ensure_ascii=False))
        except:
            pass
        
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def main():
    print("开始测试 CloudBase 外网业务 API")
    print(f"Base URL: {BASE_URL}")
    
    results = []
    
    # 测试结果存储
    test_cases = [
        ("根路径", f"{BASE_URL}/", "服务状态"),
        ("微信验证路径", f"{BASE_URL}/wechat", "微信服务器验证"),
        ("规则搜索", f"{BASE_URL}/api/search?q=飞行", "搜索规则"),
        ("关键词查询", f"{BASE_URL}/api/keyword?k=飞行", "查询关键词异能"),
        ("卡牌查询", f"{BASE_URL}/api/card?n=黑莲花", "查询卡牌规则"),
        ("MTGCH 卡牌搜索", f"{BASE_URL}/api/mtgch/search?q=闪电风暴", "MTGCH 卡牌搜索"),
        ("MTGCH 随机卡牌", f"{BASE_URL}/api/mtgch/random", "MTGCH 随机卡牌"),
        ("MTGCH 自动补全", f"{BASE_URL}/api/mtgch/autocomplete?q=闪电", "MTGCH 自动补全"),
    ]
    
    success_count = 0
    fail_count = 0
    
    for name, url, description in test_cases:
        if test_endpoint(name, url, description):
            success_count += 1
            print("✅ 测试通过")
        else:
            fail_count += 1
            print("❌ 测试失败")
        results.append((name, "✅" if success_count - len(results) == 0 else "❌"))
    
    # 测试总结
    print(f"\n{'='*60}")
    print("测试总结")
    print(f"{'='*60}")
    print(f"总计: {len(test_cases)} 个测试")
    print(f"成功: {success_count} 个")
    print(f"失败: {fail_count} 个")
    
    print("\n详细结果:")
    for name, status in results:
        print(f"{status} {name}")

if __name__ == "__main__":
    main()
