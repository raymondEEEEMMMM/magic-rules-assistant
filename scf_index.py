import json
import sys
import os
import hashlib
from urllib.parse import parse_qs

# 添加 backend 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def main_handler(event, context):
    """
    云函数入口
    """
    print(f"Event: {json.dumps(event, ensure_ascii=False)}")
    
    try:
        # 获取请求信息
        path = event.get('path', '/')
        method = event.get('httpMethod', 'GET')
        headers = event.get('headers', {})
        query_params = event.get('queryString', {})
        
        # 解析查询参数
        if isinstance(query_params, str):
            query_params = parse_qs(query_params)
            query_params = {k: v[0] if len(v) == 1 else v for k, v in query_params.items()}
        
        # 导入配置
        from backend.config import Config
        
        # 路由处理
        if method == 'GET' and path == '/':
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'message': '万智牌规则问答服务运行中', 'status': 'ok'}, ensure_ascii=False)
            }
        
        elif method == 'GET' and path == '/wechat':
            # 微信服务器验证
            signature = query_params.get('signature', '')
            timestamp = query_params.get('timestamp', '')
            nonce = query_params.get('nonce', '')
            echostr = query_params.get('echostr', '')
            
            params = [Config.WECHAT_TOKEN, timestamp, nonce]
            params.sort()
            params_str = "".join(params)
            sha1 = hashlib.sha1(params_str.encode("utf-8"))
            
            if sha1.hexdigest() == signature:
                return {
                    'statusCode': 200,
                    'headers': {'Content-Type': 'text/plain'},
                    'body': echostr
                }
            else:
                return {
                    'statusCode': 403,
                    'headers': {'Content-Type': 'text/plain'},
                    'body': '签名验证失败'
                }
        
        elif method == 'GET' and path == '/api/search':
            from backend.database import RuleDatabase
            from backend.services import RuleService
            
            db = RuleDatabase()
            rule_service = RuleService(db)
            q = query_params.get('q', '')
            results = rule_service.search_rules(q)
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'query': q, 'results': results}, ensure_ascii=False)
            }
        
        elif method == 'GET' and path == '/api/keyword':
            from backend.database import RuleDatabase
            from backend.services import RuleService
            
            db = RuleDatabase()
            rule_service = RuleService(db)
            keyword = query_params.get('k', '')
            result = rule_service.get_keyword_ability(keyword)
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'keyword': keyword, 'result': result}, ensure_ascii=False, default=str)
            }
        
        elif method == 'GET' and path == '/api/card':
            from backend.database import RuleDatabase
            from backend.services import RuleService

            db = RuleDatabase()
            rule_service = RuleService(db)
            card_name = query_params.get('n', '')
            result = rule_service.get_card_rule(card_name)

            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'card_name': card_name, 'result': result}, ensure_ascii=False, default=str)
            }

        elif method == 'GET' and path == '/api/mtgch/search':
            # MTGCH 卡牌搜索 API
            try:
                from backend.services.mtgch_api import MTGCHAPIClient

                q = query_params.get('q', '')
                page = int(query_params.get('page', 1))
                page_size = int(query_params.get('page_size', 5))
                priority_chinese = query_params.get('priority_chinese', 'true').lower() == 'true'

                if not q:
                    return {
                        'statusCode': 400,
                        'headers': {'Content-Type': 'application/json'},
                        'body': json.dumps({'error': '缺少查询参数 q'}, ensure_ascii=False)
                    }

                client = MTGCHAPIClient()
                result = client.search_cards(q, page=page, page_size=page_size, priority_chinese=priority_chinese)
                client.close()

                return {
                    'statusCode': 200,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps(result, ensure_ascii=False)
                }
            except Exception as e:
                import traceback
                traceback.print_exc()
                return {
                    'statusCode': 500,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'error': str(e)}, ensure_ascii=False)
                }

        elif method == 'GET' and path == '/api/mtgch/card':
            # MTGCH 单张卡牌详情 API
            try:
                from backend.services.mtgch_api import MTGCHAPIClient

                card_id = query_params.get('id')
                set_code = query_params.get('set')
                collector_number = query_params.get('number')

                client = MTGCHAPIClient()

                if card_id:
                    card = client.get_card_by_id(card_id)
                elif set_code and collector_number:
                    card = client.get_card_by_set_and_number(set_code, collector_number)
                else:
                    client.close()
                    return {
                        'statusCode': 400,
                        'headers': {'Content-Type': 'application/json'},
                        'body': json.dumps({'error': '需要提供 id 或 set+number 参数'}, ensure_ascii=False)
                    }

                client.close()

                if card:
                    return {
                        'statusCode': 200,
                        'headers': {'Content-Type': 'application/json'},
                        'body': json.dumps(card, ensure_ascii=False)
                    }
                else:
                    return {
                        'statusCode': 404,
                        'headers': {'Content-Type': 'application/json'},
                        'body': json.dumps({'error': '未找到卡牌'}, ensure_ascii=False)
                    }
            except Exception as e:
                import traceback
                traceback.print_exc()
                return {
                    'statusCode': 500,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'error': str(e)}, ensure_ascii=False)
                }

        elif method == 'GET' and path == '/api/mtgch/random':
            # MTGCH 随机卡牌 API
            try:
                from backend.services.mtgch_api import MTGCHAPIClient

                client = MTGCHAPIClient()
                card = client.get_random_card()
                client.close()

                if card:
                    return {
                        'statusCode': 200,
                        'headers': {'Content-Type': 'application/json'},
                        'body': json.dumps(card, ensure_ascii=False)
                    }
                else:
                    return {
                        'statusCode': 500,
                        'headers': {'Content-Type': 'application/json'},
                        'body': json.dumps({'error': '获取随机卡牌失败'}, ensure_ascii=False)
                    }
            except Exception as e:
                import traceback
                traceback.print_exc()
                return {
                    'statusCode': 500,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'error': str(e)}, ensure_ascii=False)
                }

        elif method == 'GET' and path == '/api/mtgch/autocomplete':
            # MTGCH 自动补全 API
            try:
                from backend.services.mtgch_api import MTGCHAPIClient

                q = query_params.get('q', '')
                size = int(query_params.get('size', 10))
                is_for_deck = query_params.get('is_for_deck', 'false').lower() == 'true'

                if not q:
                    return {
                        'statusCode': 400,
                        'headers': {'Content-Type': 'application/json'},
                        'body': json.dumps({'error': '缺少查询参数 q'}, ensure_ascii=False)
                    }

                client = MTGCHAPIClient()
                result = client.autocomplete(q, size=size, is_for_deck=is_for_deck)
                client.close()

                return {
                    'statusCode': 200,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps(result, ensure_ascii=False)
                }
            except Exception as e:
                import traceback
                traceback.print_exc()
                return {
                    'statusCode': 500,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'error': str(e)}, ensure_ascii=False)
                }

        else:
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Not found'}, ensure_ascii=False)
            }
    
    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        print(f"Error: {error_msg}")
        
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)}, ensure_ascii=False)
        }
