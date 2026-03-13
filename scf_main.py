import sys
import os

# 添加 backend 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.main import app
from cloudbase import cloudbase_handler

# CloudBase 云函数入口
@cloudbase_handler
def main(event, context):
    """
    CloudBase 云函数入口
    event: 触发事件
    context: 运行上下文
    """
    # 处理 HTTP 请求
    if 'httpMethod' in event:
        from fastapi.requests import Request
        from fastapi.responses import JSONResponse, PlainTextResponse

        # 创建模拟的 Request 对象
        scope = {
            'type': 'http',
            'method': event['httpMethod'],
            'headers': event.get('headers', {}),
            'path': event.get('path', '/'),
            'query_string': event.get('queryString', ''),
            'server': ('localhost', 80),
        }

        # 解析查询参数
        query_params = {}
        if 'queryString' in event:
            from urllib.parse import parse_qs
            query_params = parse_qs(event['queryString'])
            # 转换为单值
            query_params = {k: v[0] if len(v) == 1 else v for k, v in query_params.items()}

        # 处理不同的路由
        path = event.get('path', '/')
        method = event['httpMethod']

        try:
            if method == 'GET' and path == '/':
                return {
                    'statusCode': 200,
                    'headers': {'Content-Type': 'application/json'},
                    'body': '{"message": "万智牌规则问答服务运行中", "status": "ok"}'
                }
            elif method == 'GET' and path == '/wechat':
                # 微信服务器验证
                signature = query_params.get('signature', '')
                timestamp = query_params.get('timestamp', '')
                nonce = query_params.get('nonce', '')
                echostr = query_params.get('echostr', '')

                import hashlib
                from backend.config import Config

                params = [Config.WECHAT_TOKEN, timestamp, nonce]
                params.sort()
                params_str = "".join(params)
                sha1 = hashlib.sha1()
                sha1.update(params_str.encode("utf-8"))

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
                from backend.config import Config

                db = RuleDatabase()
                rule_service = RuleService(db)
                q = query_params.get('q', '')
                results = rule_service.search_rules(q)

                return {
                    'statusCode': 200,
                    'headers': {'Content-Type': 'application/json'},
                    'body': '{"query": "' + q + '", "results": ' + str(results).replace("'", '"') + '}'
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
                    'body': '{"keyword": "' + keyword + '", "result": ' + str(result) + '}'
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
                    'body': '{"card_name": "' + card_name + '", "result": ' + str(result) + '}'
                }

            else:
                return {
                    'statusCode': 404,
                    'headers': {'Content-Type': 'application/json'},
                    'body': '{"error": "Not found"}'
                }

        except Exception as e:
            import traceback
            error_msg = traceback.format_exc()
            print(f"Error: {error_msg}")

            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json'},
                'body': '{"error": "' + str(e) + '"}'
            }

    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': '{"message": "CloudBase Function is running"}'
    }

# 兼容旧版本 CloudBase
def handler(event, context):
    return main(event, context)
