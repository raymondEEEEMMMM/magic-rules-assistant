#!/usr/bin/env python3
"""测试云端的MTGCH API"""

import json
import urllib.request
import urllib.parse
import urllib.error

def test_cloud_api():
    """测试云端API"""
    
    # API基础URL（需要根据实际情况修改）
    # 方式1：直接访问云函数
    base_url = "https://magic-rules-assistant-0a1904c329.service.tcloudbaseapp.com/magic-rules-api"
    
    # 方式2：通过微信入口访问
    # base_url = "https://magic-rules-assistant-0a1904c329.ap-shanghai.tcloudbaseapp.com/wechat"
    
    tests = [
        {
            "name": "测试中文牌查询",
            "path": "/api/mtgch/search",
            "params": {"q": "闪电风暴", "page_size": 1, "priority_chinese": "true"}
        },
        {
            "name": "测试英文牌查询",
            "path": "/api/mtgch/search",
            "params": {"q": "Lightning Storm", "page_size": 1, "priority_chinese": "false"}
        },
        {
            "name": "测试随机卡牌",
            "path": "/api/mtgch/random",
            "params": {}
        },
        {
            "name": "测试自动补全",
            "path": "/api/mtgch/autocomplete",
            "params": {"q": "闪电", "size": 5}
        }
    ]
    
    print("=" * 70)
    print("🧪 CloudBase MTGCH API 测试")
    print("=" * 70)
    print(f"📍 API地址: {base_url}\n")
    
    for i, test in enumerate(tests, 1):
        print(f"\n{'='*70}")
        print(f"📋 测试 {i}: {test['name']}")
        print(f"{'='*70}")
        print(f"🔗 路径: {test['path']}")
        print(f"📝 参数: {test['params']}")
        print()
        
        try:
            # 构建URL
            url = f"{base_url}{test['path']}"
            if test['params']:
                query_string = urllib.parse.urlencode(test['params'])
                url += f"?{query_string}"
            
            print(f"🌐 请求URL: {url}")
            
            # 发送请求
            req = urllib.request.Request(url, method='GET')
            req.add_header('User-Agent', 'Mozilla/5.0')
            
            with urllib.request.urlopen(req, timeout=30) as response:
                response_text = response.read().decode('utf-8')
                
                # 尝试解析JSON
                try:
                    data = json.loads(response_text)
                    print(f"✓ 状态码: {response.status}")
                    print(f"✓ 响应类型: {response.headers.get('Content-Type', 'unknown')}")
                    print(f"\n📦 响应数据:")
                    print(json.dumps(data, ensure_ascii=False, indent=2)[:500] + "...")
                except json.JSONDecodeError:
                    print(f"✓ 状态码: {response.status}")
                    print(f"✓ 响应类型: {response.headers.get('Content-Type', 'unknown')}")
                    print(f"\n📦 响应数据 (非JSON):")
                    print(response_text[:500] + "...")
                
        except urllib.error.HTTPError as e:
            print(f"✗ HTTP错误: {e.code} - {e.reason}")
            try:
                error_data = json.loads(e.read().decode('utf-8'))
                print(f"   错误详情: {json.dumps(error_data, ensure_ascii=False, indent=2)}")
            except:
                pass
        except urllib.error.URLError as e:
            print(f"✗ URL错误: {e.reason}")
        except Exception as e:
            print(f"✗ 错误: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*70}")
    print("✅ 测试完成")
    print("=" * 70)
    
    print("\n💡 提示:")
    print("1. 如果访问失败，请检查:")
    print("   - 云函数是否正确部署")
    print("   - HTTP访问是否已启用")
    print("   - 域名配置是否正确")
    print("\n2. 替代的API访问方式:")
    print("   - 通过CloudBase Web控制台获取正确的访问URL")
    print("   - 配置自定义域名")
    print("   - 使用API网关")

if __name__ == "__main__":
    test_cloud_api()
