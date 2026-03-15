#!/usr/bin/env python3
"""测试正确的CloudBase MTGCH API"""

import json
import urllib.request
import urllib.parse
import urllib.error
import ssl

def test_cloud_api():
    """测试云端API"""
    
    # 使用正确的访问URL
    base_url = "https://magic-rules-assistant-0a1904c329-1410769303.ap-shanghai.app.tcloudbase.com"
    
    tests = [
        {
            "name": "测试中文牌查询",
            "path": "/wechat/api/mtgch/search",
            "params": {"q": "闪电风暴", "page_size": 1, "priority_chinese": "true"}
        },
        {
            "name": "测试英文牌查询", 
            "path": "/wechat/api/mtgch/search",
            "params": {"q": "Lightning Storm", "page_size": 1, "priority_chinese": "false"}
        },
        {
            "name": "测试随机卡牌",
            "path": "/wechat/api/mtgch/random",
            "params": {}
        },
        {
            "name": "测试自动补全",
            "path": "/wechat/api/mtgch/autocomplete",
            "params": {"q": "闪电", "size": 5}
        },
        {
            "name": "测试根路径",
            "path": "/",
            "params": {}
        }
    ]
    
    print("=" * 70)
    print("CloudBase MTGCH API Test (Correct URL)")
    print("=" * 70)
    print(f"API: {base_url}\n")
    
    ssl_context = ssl._create_unverified_context()
    
    for i, test in enumerate(tests, 1):
        print(f"\n{'='*70}")
        print(f"Test {i}: {test['name']}")
        print(f"{'='*70}")
        print(f"Path: {test['path']}")
        print(f"Params: {test['params']}")
        print()

        try:
            url = f"{base_url}{test['path']}"
            if test['params']:
                query_string = urllib.parse.urlencode(test['params'])
                url += f"?{query_string}"

            print(f"URL: {url}")
            
            req = urllib.request.Request(url, method='GET')
            req.add_header('User-Agent', 'Mozilla/5.0')
            
            with urllib.request.urlopen(req, context=ssl_context, timeout=30) as response:
                response_text = response.read().decode('utf-8')
                
                print(f"Status: {response.status}")
                print(f"Content-Type: {response.headers.get('Content-Type', 'unknown')}")
                print(f"\nResponse:")

                try:
                    data = json.loads(response_text)
                    print(json.dumps(data, ensure_ascii=False, indent=2)[:1000] + "...")

                    # Check result
                    if "items" in data:
                        print(f"\nFound {len(data.get('items', []))} cards")
                        if data['items']:
                            card = data['items'][0]
                            print(f"  First card: {card.get('name', 'unknown')}")
                    elif "name" in data:
                        print(f"\nCard name: {data.get('name', 'unknown')}")
                    elif "message" in data:
                        print(f"\nMessage: {data['message']}")
                    elif "error" in data:
                        print(f"\nError: {data['error']}")
                        
                except json.JSONDecodeError:
                    print(response_text[:1000] + "...")
                
        except urllib.error.HTTPError as e:
            print(f"HTTP Error: {e.code} - {e.reason}")
            try:
                error_data = json.loads(e.read().decode('utf-8'))
                print(f"   Detail: {json.dumps(error_data, ensure_ascii=False, indent=2)}")
            except:
                pass
        except urllib.error.URLError as e:
            print(f"URL Error: {e.reason}")
        except Exception as e:
            print(f"Error: {str(e)}")
            import traceback
            traceback.print_exc()

    print(f"\n{'='*70}")
    print("Test Complete")
    print("=" * 70)

if __name__ == "__main__":
    test_cloud_api()
