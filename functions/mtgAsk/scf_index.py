#!/usr/bin/env python3
"""
CloudBase HTTP 云函数入口
需要监听 9000 端口处理 HTTP 请求
"""
import sys
import os
import hashlib
from urllib.parse import parse_qs
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

# 添加 vendor 依赖目录到 Python 路径
vendor_path = os.path.join(os.path.dirname(__file__), 'vendor')
if os.path.exists(vendor_path):
    sys.path.insert(0, vendor_path)

# 添加 backend 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# 数据库路径配置
def ensure_database():
    """确保数据库可用"""
    print(f"=== ensure_database called ===")
    print(f"__file__: {__file__}")
    
    # 尝试多个可能的路径
    possible_paths = [
        os.path.join(os.path.dirname(__file__), 'data', 'magic_rules.db'),
        os.path.join(os.path.dirname(__file__), 'backend', 'data', 'magic_rules.db'),
        os.path.join(os.path.dirname(__file__), '..', 'data', 'magic_rules.db'),
        '/tmp/magic_rules.db',
        os.path.join(os.getcwd(), 'data', 'magic_rules.db'),
        os.path.join(os.getcwd(), 'backend', 'data', 'magic_rules.db'),
    ]
    
    # 检查环境变量
    env_db_path = os.environ.get('DATABASE_PATH')
    if env_db_path:
        # 如果是相对路径，转换为绝对路径
        if not os.path.isabs(env_db_path):
            env_db_path = os.path.join(os.path.dirname(__file__), env_db_path)
        possible_paths.insert(0, env_db_path)
    
    print(f"Checking paths: {possible_paths}")
    
    for db_path in possible_paths:
        print(f"Checking: {db_path}")
        if os.path.exists(db_path):
            print(f"✓ Found database at: {db_path}")
            os.environ['DATABASE_PATH'] = db_path
            return db_path
    
    # 如果都没找到，抛出错误
    print(f"✗ Database not found. Checked paths: {possible_paths}")
    raise FileNotFoundError(f"Database not found. Checked: {possible_paths}")

# 尝试加载配置
try:
    from backend.config import Config
    WECHAT_TOKEN = Config.WECHAT_TOKEN
    print("✓ Loaded WECHAT_TOKEN from backend.config")
except Exception as e:
    print(f"✗ Config import error: {e}, using environment variable")
    WECHAT_TOKEN = os.environ.get('WECHAT_TOKEN', 'wx_mtg_rules_2024')

print(f"WECHAT_TOKEN: {WECHAT_TOKEN}")

class RequestHandler(BaseHTTPRequestHandler):
    """HTTP 请求处理器"""
    
    def log_message(self, format, *args):
        """覆盖默认的日志输出"""
        print(f"[{self.log_date_time_string()}] {format % args}")
    
    def do_GET(self):
        """处理 GET 请求"""
        print(f"=== GET Request ===")
        print(f"Path: {self.path}")
        
        # 检查是否有 x-original-uri header (CloudBase HTTP)
        original_uri = self.headers.get('x-original-uri') or self.headers.get('x-request-uri')
        if original_uri:
            print(f"Original URI from header: {original_uri}")
            # 优先使用原始路径
            self.path = original_uri
        
        try:
            # 解析路径和查询参数
            path = self.path
            query_params = {}
            
            if '?' in path:
                path, query_string = path.split('?', 1)
                query_params = parse_qs(query_string)
                query_params = {k: v[0] if len(v) == 1 else v for k, v in query_params.items()}
            
            print(f"Parsed path: {path}")
            print(f"Query params: {query_params}")
            print(f"Current directory: {os.getcwd()}")
            print(f"Script directory: {os.path.dirname(__file__)}")
            print(f"Files in script directory: {os.listdir(os.path.dirname(__file__))}")
            print(f"Files in data directory: {os.listdir(os.path.join(os.path.dirname(__file__), 'data')) if os.path.exists(os.path.join(os.path.dirname(__file__), 'data')) else 'N/A'}")
            
            # 规则搜索 API（支持 /api/search 和 /search）
            if path in ('/api/search', '/search'):
                # 规则搜索 API
                try:
                    from backend.database import RuleDatabase
                    from backend.services import RuleService

                    db = RuleDatabase()
                    rule_service = RuleService(db)
                    q = query_params.get('q', '')
                    results = rule_service.search_rules(q)

                    # 计算总结果数
                    total_count = (
                        len(results.get('rules', [])) +
                        len(results.get('keyword_abilities', [])) +
                        len(results.get('cards', [])) +
                        len(results.get('qa_templates', []))
                    )

                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    response = {'query': q, 'count': total_count, 'results': results}
                    self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                    return
                except FileNotFoundError as e:
                    import traceback
                    traceback.print_exc()
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    # 返回空结果而不是错误
                    response = {'query': q, 'count': 0, 'results': {'rules': [], 'keyword_abilities': [], 'cards': [], 'qa_templates': []}, 'error': 'Database not found'}
                    self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                    return
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    self.send_response(500)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    response = {'error': str(e), 'traceback': traceback.format_exc()}
                    self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                    return
            
            # 关键词查询 API（支持 /api/keyword 和 /keyword）
            elif path in ('/api/keyword', '/keyword'):
                # 关键词查询 API
                try:
                    from backend.database import RuleDatabase
                    from backend.services import RuleService

                    db = RuleDatabase()
                    rule_service = RuleService(db)
                    keyword = query_params.get('k', '')
                    result = rule_service.get_keyword_ability(keyword)

                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    response = {'keyword': keyword, 'result': result}
                    self.wfile.write(json.dumps(response, ensure_ascii=False, default=str).encode('utf-8'))
                    return
                except FileNotFoundError as e:
                    import traceback
                    traceback.print_exc()
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    response = {'keyword': keyword, 'result': None, 'error': 'Database not found'}
                    self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                    return
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    self.send_response(500)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    response = {'error': str(e)}
                    self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                    return

            # MTGCH 卡牌搜索 API（支持 /mtgch/search、/api/mtgch/search 和 /api/card）
            elif path in ('/mtgch/search', '/api/mtgch/search', '/card', '/api/card'):
                # MTGCH 卡牌搜索 API
                try:
                    from backend.services.mtgch_api import MTGCHAPIClient

                    q = query_params.get('q', '')
                    page = int(query_params.get('page', 1))
                    page_size = int(query_params.get('page_size', 5))
                    priority_chinese = query_params.get('priority_chinese', 'true').lower() == 'true'

                    if not q:
                        self.send_response(400)
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                        response = {'error': '缺少查询参数 q'}
                        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                        return

                    client = MTGCHAPIClient()
                    result = client.search_cards(q, page=page, page_size=page_size, priority_chinese=priority_chinese)
                    client.close()

                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))
                    return
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    self.send_response(500)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    response = {'error': str(e)}
                    self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                    return

            # MTGCH 单张卡牌详情 API（支持 /mtgch/card 和 /api/mtgch/card）
            elif path in ('/mtgch/card', '/api/mtgch/card'):
                # MTGCH 单张卡牌详情 API
                try:
                    from backend.services.mtgch_api import MTGCHAPIClient

                    # 支持两种方式：UUID 或 set+number
                    card_id = query_params.get('id')
                    set_code = query_params.get('set')
                    collector_number = query_params.get('number')

                    client = MTGCHAPIClient()

                    if card_id:
                        card = client.get_card_by_id(card_id)
                    elif set_code and collector_number:
                        card = client.get_card_by_set_and_number(set_code, collector_number)
                    else:
                        self.send_response(400)
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                        response = {'error': '需要提供 id 或 set+number 参数'}
                        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                        client.close()
                        return

                    client.close()

                    if card:
                        self.send_response(200)
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps(card, ensure_ascii=False).encode('utf-8'))
                    else:
                        self.send_response(404)
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                        response = {'error': '未找到卡牌'}
                        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                    return
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    self.send_response(500)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    response = {'error': str(e)}
                    self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                    return

            # MTGCH 随机卡牌 API（支持 /mtgch/random 和 /api/mtgch/random）
            elif path in ('/mtgch/random', '/api/mtgch/random'):
                # MTGCH 随机卡牌 API
                try:
                    from backend.services.mtgch_api import MTGCHAPIClient

                    client = MTGCHAPIClient()
                    card = client.get_random_card()
                    client.close()

                    if card:
                        self.send_response(200)
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps(card, ensure_ascii=False).encode('utf-8'))
                    else:
                        self.send_response(500)
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                        response = {'error': '获取随机卡牌失败'}
                        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                    return
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    self.send_response(500)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    response = {'error': str(e)}
                    self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                    return

            # MTGCH 自动补全 API（支持 /mtgch/autocomplete 和 /api/mtgch/autocomplete）
            elif path in ('/mtgch/autocomplete', '/api/mtgch/autocomplete'):
                # MTGCH 自动补全 API
                try:
                    from backend.services.mtgch_api import MTGCHAPIClient

                    q = query_params.get('q', '')
                    size = int(query_params.get('size', 10))
                    is_for_deck = query_params.get('is_for_deck', 'false').lower() == 'true'

                    if not q:
                        self.send_response(400)
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                        response = {'error': '缺少查询参数 q'}
                        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                        return

                    client = MTGCHAPIClient()
                    result = client.autocomplete(q, size=size, is_for_deck=is_for_deck)
                    client.close()

                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))
                    return
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    self.send_response(500)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    response = {'error': str(e)}
                    self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                    return
            
            # 检查是否有微信验证参数
            if 'echostr' in query_params or 'signature' in query_params:
                # 微信服务器验证
                signature = query_params.get('signature', '')
                timestamp = query_params.get('timestamp', '')
                nonce = query_params.get('nonce', '')
                echostr = query_params.get('echostr', '')
                
                print(f"WeChat verify: signature={signature}, timestamp={timestamp}, nonce={nonce}, echostr={echostr}")
                
                params = [WECHAT_TOKEN, timestamp, nonce]
                params.sort()
                params_str = "".join(params)
                sha1 = hashlib.sha1(params_str.encode("utf-8"))
                calculated_signature = sha1.hexdigest()
                
                print(f"Calculated signature: {calculated_signature}")
                print(f"Expected signature: {signature}")
                
                if calculated_signature == signature or signature == '':
                    print("✓ Signature verified")
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/plain')
                    self.end_headers()
                    self.wfile.write(echostr.encode('utf-8'))
                    return
                else:
                    print("✗ Signature verification failed")
                    self.send_response(403)
                    self.send_header('Content-Type', 'text/plain')
                    self.end_headers()
                    self.wfile.write('签名验证失败'.encode('utf-8'))
                    return

            # 根路径或其他路径
            print(f"⚠️ No matching route for path: {path}")
            print(f"⚠️ Checked paths: /, /wechat, /search, /api/search, /keyword, /api/keyword, /card, /api/card, /mtgch/search, /api/mtgch/search, /mtgch/card, /api/mtgch/card, /mtgch/random, /api/mtgch/random, /mtgch/autocomplete, /api/mtgch/autocomplete")
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = {
                'message': '万智牌规则问答服务运行中',
                'status': 'ok',
                'service': 'CloudBase HTTP Function',
                'path': path,
                'query_params': query_params
            }
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            return
        
        except Exception as e:
            import traceback
            error_msg = traceback.format_exc()
            print(f"Error: {error_msg}")
            
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = {'error': str(e)}
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
    
    def do_POST(self):
        """处理 POST 请求"""
        print(f"=== POST Request ===")
        print(f"Path: {self.path}")
        
        # 检查是否有 x-original-uri header (CloudBase HTTP)
        original_uri = self.headers.get('x-original-uri') or self.headers.get('x-request-uri')
        if original_uri:
            print(f"Original URI from header: {original_uri}")
            self.path = original_uri
        
        # 读取请求体
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        body_str = body.decode('utf-8', errors='ignore')
        print(f"Body: {body_str}")
        
        try:
            # 微信消息处理
            if '/wechat' in self.path:
                # 确保数据库可用
                ensure_database()
                
                # 解析 XML
                import xml.etree.ElementTree as ET
                root = ET.fromstring(body_str)
                
                msg_type = root.find('MsgType').text
                from_user = root.find('FromUserName').text
                to_user = root.find('ToUserName').text
                
                print(f"Message type: {msg_type}, From: {from_user}, To: {to_user}")
                
                if msg_type == 'event':
                    # 事件消息（菜单点击等）
                    event = root.find('Event').text
                    event_key = root.find('EventKey').text if root.find('EventKey') is not None else ''
                    
                    print(f"Event: {event}, EventKey: {event_key}")
                    
                    try:
                        from backend.database import RuleDatabase
                        from backend.services import RuleService
                        from backend.services.mtgch_api import MTGCHAPIClient, format_card_info

                        db = RuleDatabase()
                        rule_service = RuleService(db)
                        
                        # 处理菜单点击事件
                        if event == 'CLICK':
                            if event_key == 'keyword_search':
                                # 关键词查询说明
                                reply = """📖 关键词查询

发送关键词即可查询卡牌异能的规则解释。

例如发送以下关键词：
• 飞行 - 飞行异能的规则
• 警戒 - 警戒异能的规则  
• 死触 - 死触异能的规则
• 闪现 - 闪现异能的规则

💡 小贴士：直接发送关键词即可，无需其他格式。"""
                            
                            elif event_key == 'rule_search':
                                # 规则搜索说明
                                reply = """🔍 规则搜索

发送您想了解的游戏规则，即可搜索相关规则条目。

例如发送：
• 战斗 - 战斗阶段相关规则
• 施放 - 咒语施放规则
• 支付费用 - 如何支付费用

💡 小贴士：描述尽量简洁，关键词效果更好。"""
                            
                            elif event_key == 'card_search':
                                # 卡牌查询说明
                                reply = """🃏 卡牌查询

发送「卡牌:卡牌名称」即可查询卡牌信息。

例如：
• 卡牌:闪电击
• 卡牌:析米克生长师
• 卡牌:心神不安

💡 小贴士：卡牌名称要准确，尽量使用原版名称。"""
                            
                            elif event_key == 'feature_intro':
                                # 功能介绍
                                reply = """📱 万智牌规则问答服务

本服务提供以下功能：

🔍 规则搜索 - 输入规则关键词搜索相关规则
📖 关键词查询 - 查询卡牌异能的详细解释
🃏 卡牌查询 - 输入「卡牌:名称」查询卡牌信息

💡 发送任何规则相关问题即可自动搜索！"""
                            
                            elif event_key == 'about':
                                # 关于服务
                                reply = """ℹ️ 关于万智牌规则问答

基于 Magic: The Gathering 官方规则构建。

📊 数据包含：
• 完整游戏规则 (1133条)
• 关键词能力 (190+)
• 卡牌数据查询

🔧 技术支持：CloudBase 云函数

有问题请发送消息咨询！"""
                            
                            else:
                                reply = f"收到点击事件：{event_key}\n\n您可以：\n• 发送关键词查询（如：飞行）\n• 发送「卡牌:名称」查询卡牌\n• 直接发送规则问题搜索"
                        
                        else:
                            reply = "欢迎使用万智牌规则问答服务！点击下方菜单或直接发送关键词查询。"
                    
                    except Exception as e:
                        print(f"Event handle error: {e}")
                        import traceback
                        traceback.print_exc()
                        reply = f"处理事件时出现错误：{str(e)}"
                    
                    # 构建回复
                    reply_xml = f"""<xml>
<ToUserName><![CDATA[{from_user}]]></ToUserName>
<FromUserName><![CDATA[{to_user}]]></FromUserName>
<CreateTime>{int(__import__('time').time())}</CreateTime>
<MsgType><![CDATA[text]]></MsgType>
<Content><![CDATA[{reply}]]></Content>
</xml>"""
                    
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/xml')
                    self.end_headers()
                    self.wfile.write(reply_xml.encode('utf-8'))
                    return
                
                elif msg_type == 'text':
                    # 文本消息
                    content = root.find('Content').text
                    create_time = int(root.find('CreateTime').text)

                    print(f"User message: {content}")

                    # 处理查询
                    try:
                        from backend.database import RuleDatabase
                        from backend.services import RuleService
                        from backend.services.mtgch_api import MTGCHAPIClient, format_card_info

                        db = RuleDatabase()
                        rule_service = RuleService(db)

                        # 判断查询类型
                        if content.startswith('卡牌:'):
                            # 卡牌查询
                            card_name = content[3:].strip()
                            client = MTGCHAPIClient()
                            result = client.search_cards(card_name, page_size=1)
                            client.close()

                            if "items" in result and result["items"]:
                                card = result["items"][0]
                                reply = format_card_info(card)
                            else:
                                reply = f"未找到卡牌「{card_name}」，请检查卡牌名称。"
                        elif len(content) <= 10:
                            # 关键词查询
                            result = rule_service.get_keyword_ability(content)
                            if result:
                                reply = f"关键词【{content}】的解释：\n{result}"
                            else:
                                reply = f"未找到关键词【{content}】的规则解释。您可以尝试其他关键词，如：飞行、瞬息、警戒等。"
                        else:
                            # 规则搜索
                            results = rule_service.search_rules(content)
                            if results:
                                reply = f"找到 {len(results)} 条相关规则：\n\n" + "\n\n".join(results[:3])
                            else:
                                reply = f"未找到与「{content}」相关的规则。您可以尝试更简洁的搜索词，或使用「卡牌:名称」查询卡牌信息。"

                        print(f"Reply: {reply}")

                    except Exception as e:
                        print(f"Query error: {e}")
                        import traceback
                        traceback.print_exc()
                        reply = f"查询时出现错误：{str(e)}"
                    
                    # 构建回复
                    reply_xml = f"""<xml>
<ToUserName><![CDATA[{from_user}]]></ToUserName>
<FromUserName><![CDATA[{to_user}]]></FromUserName>
<CreateTime>{int(__import__('time').time())}</CreateTime>
<MsgType><![CDATA[text]]></MsgType>
<Content><![CDATA[{reply}]]></Content>
</xml>"""
                    
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/xml')
                    self.end_headers()
                    self.wfile.write(reply_xml.encode('utf-8'))
                    return
                
                else:
                    # 其他消息类型，返回 success
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/plain')
                    self.end_headers()
                    self.wfile.write('success'.encode('utf-8'))
                    return
            
            # 其他 POST 请求
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = {'message': 'POST received', 'path': self.path}
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            return
        
        except Exception as e:
            import traceback
            error_msg = traceback.format_exc()
            print(f"POST Error: {error_msg}")
            
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = {'error': str(e)}
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

def main():
    """启动 HTTP 服务器"""
    port = int(os.environ.get('SCF_PORT', 9000))
    print(f"Starting HTTP server on port {port}...")
    
    server = HTTPServer(('0.0.0.0', port), RequestHandler)
    print(f"Server is running on http://0.0.0.0:{port}")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.shutdown()


def main_handler(event, context):
    """
    CloudBase HTTP 函数入口
    处理 API Gateway 触发的事件
    """
    print(f"=== main_handler called ===")
    print(f"Event: {event}")
    print(f"Context: {context}")
    
    # 解析请求
    http_method = event.get('httpMethod', 'GET')
    path = event.get('path', '/')
    query_string = event.get('queryString', '')
    headers = event.get('headers', {})
    body = event.get('body', '')
    
    print(f"Method: {http_method}, Path: {path}, Query: {query_string}")
    
    # 创建模拟的请求处理器
    from io import BytesIO
    
    class MockHandler(RequestHandler):
        def __init__(self):
            self.headers = headers
            self.path = path + ('?' + query_string if query_string else '')
            self.command = http_method
            self.rfile = BytesIO(body.encode('utf-8') if body else b'')
            self.wfile = BytesIO()
            
        def send_response(self, code, message=None):
            self.response_code = code
            self.response_headers = []
            
        def send_header(self, keyword, value):
            self.response_headers.append((keyword, value))
            
        def end_headers(self):
            pass
            
        def log_message(self, format, *args):
            print(f"[LOG] {format % args}")
    
    handler = MockHandler()
    
    # 处理请求
    try:
        if http_method == 'GET':
            handler.do_GET()
        elif http_method == 'POST':
            handler.do_POST()
        else:
            return {
                'statusCode': 405,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Method not allowed'})
            }
        
        # 获取响应
        handler.wfile.seek(0)
        response_body = handler.wfile.read().decode('utf-8')
        
        return {
            'statusCode': getattr(handler, 'response_code', 200),
            'headers': dict(getattr(handler, 'response_headers', [('Content-Type', 'application/json')])),
            'body': response_body
        }
        
    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        print(f"Error in main_handler: {error_msg}")
        
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }


if __name__ == '__main__':
    main()
