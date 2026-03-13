#!/usr/bin/env python3
"""测试云端的MTGCH API - 使用微信路径"""

import json
import urllib.request
import urllib.parse
import urllib.error

def test_cloud_api():
    """测试云端API"""
    
    # 使用微信路径访问
    base_url = "https://magic-rules-assistant-0a1904c329.ap-shanghai.tcloudbaseapp.com/wechat"
    
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
        }
    ]
    
    print("=" * 70)
    print("🧪 CloudBase MTGCH API 测试 (微信路径)")
    print("=" * 70)
    print(f"📍 API地址: {base_url}\n")
    
    import ssl
    ssl_context = ssl._create_unverified_context()
    
    for i, test in enumerate(tests, 1):
        print(f"\n{'='*70}")
        print(f"📋 测试 {i}: {test['name']}")
        print(f"{'='*70}")
        print(f"🔗 路径: {test['path']}")
        print(f"📝 参数: {test['params']}")
        print()
        
        try:
            url = f"{base_url}{test['path']}"
            if test['params']:
                query_string = urllib.parse.urlencode(test['params'])
                url += f"?{query_string}"
            
            print(f"🌐 请求URL: {url}")
            
            req = urllib.request.Request(url, method='GET')
            req.add_header('User-Agent', 'Mozilla/5.0')
            
            with urllib.request.urlopen(req, context=ssl_context, timeout=30) as response:
                response_text = response.read().decode('utf-8')
                
                print(f"✓ 状态码: {response.status}")
                print(f"✓ 响应类型: {response.headers.get('Content-Type', 'unknown')}")
                print(f"\n📦 响应数据:")
                
                try:
                    data = json.loads(response_text)
                    print(json.dumps(data, ensure_ascii=False, indent=2)[:800] + "...")
                    
                    # 检查是否成功
                    if "items" in data:
                        print(f"\n✓ 找到 {len(data.get('items', []))} 张卡牌")
                        if data['items']:
                            card = data['items'][0]
                            print(f"  第一张卡牌: {card.get('name', '未知')}")
                    elif "name" in data:
                        print(f"\n✓ 卡牌名称: {data.get('name', '未知')}")
                    elif "error" in data:
                        print(f"\n✗ 错误: {data['error']}")
                        
                except json.JSONDecodeError:
                    print(response_text[:800] + "...")
                
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

if __name__ == "__main__":
    test_cloud_api()
