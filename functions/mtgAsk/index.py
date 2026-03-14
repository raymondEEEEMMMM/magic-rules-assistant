#!/usr/bin/env python3
"""
CloudBase HTTP 函数入口 - 简化版
"""
import json
import os
import sys

# 添加 backend 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def main_handler(event, context):
    """
    CloudBase HTTP 函数入口
    """
    print(f"Event: {json.dumps(event)}")
    
    # 获取请求信息
    http_method = event.get('httpMethod', 'GET')
    path = event.get('path', '/')
    query_string = event.get('queryString', '')
    headers = event.get('headers', {})
    body = event.get('body', '')
    
    print(f"Method: {http_method}, Path: {path}, Query: {query_string}")
    
    try:
        # 解析查询参数
        query_params = {}
        if query_string:
            from urllib.parse import parse_qs
            parsed = parse_qs(query_string)
            query_params = {k: v[0] if len(v) == 1 else v for k, v in parsed.items()}
        
        # 路由处理
        if path == '/' or path == '':
            # 服务状态
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'message': '万智牌规则问答服务运行中',
                    'status': 'ok',
                    'service': 'CloudBase HTTP Function',
                    'path': path
                }, ensure_ascii=False)
            }
        
        elif path in ('/api/search', '/search'):
            # 规则搜索
            from backend.database import RuleDatabase
            from backend.services import RuleService
            
            db = RuleDatabase()
            rule_service = RuleService(db)
            q = query_params.get('q', '')
            results = rule_service.search_rules(q)
            
            total_count = (
                len(results.get('rules', [])) +
                len(results.get('keyword_abilities', [])) +
                len(results.get('cards', []))
            )
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'query': q,
                    'count': total_count,
                    'results': results
                }, ensure_ascii=False)
            }
        
        elif path in ('/api/keyword', '/keyword'):
            # 关键词查询
            from backend.database import RuleDatabase
            from backend.services import RuleService
            
            db = RuleDatabase()
            rule_service = RuleService(db)
            keyword = query_params.get('k', '')
            result = rule_service.get_keyword_ability(keyword)
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'keyword': keyword,
                    'result': result
                }, ensure_ascii=False, default=str)
            }
        
        elif path in ('/api/card', '/card', '/mtgch/search', '/api/mtgch/search'):
            # 卡牌搜索
            from backend.services.mtgch_api import MTGCHAPIClient
            
            q = query_params.get('q', '')
            page = int(query_params.get('page', 1))
            page_size = int(query_params.get('page_size', 5))
            
            if not q:
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'error': '缺少查询参数 q'})
                }
            
            client = MTGCHAPIClient()
            result = client.search_cards(q, page=page, page_size=page_size)
            client.close()
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps(result, ensure_ascii=False)
            }
        
        elif path in ('/api/mtgch/card', '/mtgch/card'):
            # 单张卡牌详情
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
                    'body': json.dumps({'error': '需要提供 id 或 set+number 参数'})
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
                    'body': json.dumps({'error': '未找到卡牌'})
                }
        
        elif path in ('/api/mtgch/random', '/mtgch/random'):
            # 随机卡牌
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
                    'body': json.dumps({'error': '获取随机卡牌失败'})
                }
        
        elif path in ('/api/mtgch/autocomplete', '/mtgch/autocomplete'):
            # 自动补全
            from backend.services.mtgch_api import MTGCHAPIClient
            
            q = query_params.get('q', '')
            size = int(query_params.get('size', 10))
            
            if not q:
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'error': '缺少查询参数 q'})
                }
            
            client = MTGCHAPIClient()
            result = client.autocomplete(q, size=size)
            client.close()
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps(result, ensure_ascii=False)
            }
        
        else:
            # 未知路径
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'error': 'Not Found',
                    'path': path,
                    'available_paths': [
                        '/',
                        '/api/search',
                        '/api/keyword',
                        '/api/card',
                        '/api/mtgch/card',
                        '/api/mtgch/random',
                        '/api/mtgch/autocomplete'
                    ]
                })
            }
    
    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        print(f"Error: {error_msg}")
        
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }
