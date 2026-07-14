#!/usr/bin/env python3
"""
CloudBase HTTP 函数入口 - 简化版
"""
import json
import os
import re
import sys

# 添加 vendor 依赖和 backend 目录到路径
vendor_path = os.path.join(os.path.dirname(__file__), 'vendor')
sys.path.insert(0, vendor_path)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))


def _get_card_image_url(card):
    """
    获取卡牌图片 URL，支持双面牌（transform cards）
    双面牌的图片在 card_faces[0].image_uris 中
    """
    # 优先使用顶层的 image_uris（普通单面牌）
    image_uris = card.get('image_uris')
    if image_uris:
        return image_uris.get('border_crop') or image_uris.get('normal') or ''

    # 双面牌（transform）：图片在 card_faces[0].image_uris 中
    card_faces = card.get('card_faces', [])
    if card_faces and len(card_faces) > 0:
        face_uris = card_faces[0].get('image_uris')
        if face_uris:
            return face_uris.get('border_crop') or face_uris.get('normal') or ''

    return ''


def main(event, context):
    """
    CloudBase HTTP 函数入口
    """
    print(f"Event: {json.dumps(event)}")

    # 检查是否为定时触发器
    trigger_name = event.get('TriggerName', '')
    trigger_type = event.get('Type', '')
    if trigger_type == 'Timer' and trigger_name == 'session-cleanup-timer':
        print(f"=== 定时任务触发: {trigger_name} ===")
        from backend.services.agent_pool_manager import AgentPoolManager
        manager = AgentPoolManager()

        # 1. 先清理所有过期会话
        session_result = manager.cleanup_all_sessions()
        print(f"=== 会话清理结果: {session_result} ===")

        # 2. 再销毁空闲超时的 agents
        idle_cleaned = manager.cleanup_idle_agents()
        print(f"=== 空闲 Agent 清理数量: {idle_cleaned} ===")

        # 获取池状态
        stats = manager.get_pool_stats()
        print(f"=== Agent 池状态: {stats} ===")

        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': True,
                'triggered_by': trigger_name,
                'session_result': session_result,
                'idle_agents_cleaned': idle_cleaned,
                'pool_stats': stats
            }, ensure_ascii=False)
        }

    # 获取请求信息
    http_method = event.get('httpMethod', 'GET')
    path = event.get('path', '/')
    query_string = event.get('queryString', '')
    headers = event.get('headers', {})
    body = event.get('body', '')

    print(f"Method: {http_method}, Path: {path}, Query: {query_string}")
    
    try:
        # 检查是否有 action 参数（来自 wx.cloud.callFunction）
        action = event.get('action', '')
        if action == 'getOpenid':
            # Event 函数通过 wx.cloud.callFunction 调用时，openid 在 wxContext 中
            wx_context = event.get('wxContext', {})
            openid = wx_context.get('OPENID') or wx_context.get('openid') or event.get('openid') or headers.get('x-wx-openid', None)
            # 打印完整 event 和 context 用于调试
            print(f"CODEBUDDY_DEBUG getOpenid: openid={openid}, wxContext={wx_context}")
            print(f"CODEBUDDY_DEBUG event keys={list(event.keys())}, context keys={list(context.keys()) if context else 'None'}")
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'openid': openid})
            }

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

        elif path in ('/api/rule', '/rule'):
            # 规则详情查询
            from backend.database import RuleDatabase

            rule_number = query_params.get('n', '')
            if not rule_number:
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'error': '缺少规则编号参数 n'})
                }

            db = RuleDatabase()
            result = db.get_rule_by_number(rule_number)

            if result:
                return {
                    'statusCode': 200,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'result': result}, ensure_ascii=False, default=str)
                }
            else:
                return {
                    'statusCode': 404,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'error': '未找到规则'})
                }

        elif path in ('/api/card', '/card', '/mtgch/search', '/api/mtgch/search'):
            # 卡牌搜索 - 按发行日期排序，原版优先
            from backend.services.mtgch_api import MTGCHAPIClient

            q = query_params.get('q', '')
            page = int(query_params.get('page', 1))
            page_size = int(query_params.get('page_size', 5))
            order = query_params.get('order', 'released_at')  # 默认按发行日期排序，原版优先

            if not q:
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'error': '缺少查询参数 q'})
                }

            client = MTGCHAPIClient()
            result = client.search_cards(q, page=page, page_size=page_size, order=order)
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

        elif path in ('/api/mtgch/sets', '/wechat/api/mtgch/sets'):
            # 获取系列列表
            from backend.services.mtgch_api import MTGCHAPIClient

            client = MTGCHAPIClient()
            result = client.get_sets()
            client.close()

            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps(result, ensure_ascii=False)
            }

        elif re.match(r'^/api/mtgch/set/([^/]+)/cards/?$', path):
            # 获取特定系列的卡牌
            match = re.match(r'^/api/mtgch/set/([^/]+)/cards/?$', path)
            set_code = match.group(1)
            page = int(query_params.get('page', 1))
            page_size = int(query_params.get('page_size', 20))

            from backend.services.mtgch_api import MTGCHAPIClient
            client = MTGCHAPIClient()
            result = client.get_set_cards(set_code, page=page, page_size=page_size)
            client.close()

            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps(result, ensure_ascii=False)
            }

        elif re.match(r'^/api/scryfall/set/([^/]+)/cards/?$', path):
            # 通过Scryfall API获取系列卡牌（包含图片）
            match = re.match(r'^/api/scryfall/set/([^/]+)/cards/?$', path)
            set_code = match.group(1).lower()  # Scryfall set code is lowercase

            from backend.services.mtgch_api import MTGCHAPIClient
            client = MTGCHAPIClient()

            # 获取所有页面的卡牌
            all_cards = []
            page = 1
            while True:
                result = client.search_cards_by_set(set_code, page=page)
                cards = result.get('data', [])
                all_cards.extend(cards)
                if not result.get('has_more'):
                    break
                page += 1
                if page > 10:  # 最多10页，防止无限循环
                    break
            client.close()

            # 转换格式以适配前端
            transformed = {
                'items': [{
                    'id': card['id'],
                    'display_name': card['name'],
                    'image_url': _get_card_image_url(card),
                    'collector_number': card.get('collector_number', ''),
                    'colors': card.get('colors', []),  # 颜色
                    'cmc': card.get('cmc', 0),  # 转换费用
                    'type_line': card.get('type_line', ''),  # 类别
                    'rarity': card.get('rarity', ''),  # 稀有度
                    'mana_cost': card.get('mana_cost', ''),  # 法力费用
                } for card in all_cards],
                'total': len(all_cards)
            }

            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps(transformed, ensure_ascii=False)
            }

        elif path == '/api/secret-lair/cards':
            # 获取 Secret Lair 卡牌（按发布日期分组）
            import requests
            from datetime import datetime

            # 支持 months 参数，默认12个月
            months_count = int(query_params.get('months', 12))

            # 生成需要查询的月份列表（过去months_count个月，包含当月）
            def get_past_months(start, months_count):
                """获取从start往前推months_count个月份列表"""
                months = []
                current = start
                for _ in range(months_count):
                    months.append(current.strftime('%Y-%m'))
                    # 上个月
                    if current.month == 1:
                        current = current.replace(year=current.year - 1, month=12)
                    else:
                        current = current.replace(month=current.month - 1)
                return months

            today = datetime.today()
            months = get_past_months(today, months_count)

            all_cards = []

            # 按月查询（Scryfall 支持 date:YYYY-MM 前缀匹配）
            # 带重试的请求函数
            def fetch_with_retry(url, max_retries=3):
                for attempt in range(max_retries):
                    try:
                        resp = requests.get(url, timeout=30)
                        return resp.json()
                    except requests.exceptions.RequestException as e:
                        if attempt == max_retries - 1:
                            raise
                        import time
                        time.sleep(1)  # 重试前等待1秒

            for month in months:
                query = f"set:sld+date:{month}"
                page = 1
                while True:
                    # 直接调用 Scryfall API
                    url = f"https://api.scryfall.com/cards/search?q={query}&page={page}"
                    result = fetch_with_retry(url)
                    cards = result.get('data', [])
                    all_cards.extend(cards)
                    if not result.get('has_more'):
                        break
                    page += 1
                    if page > 5:  # 防止异常数据导致过多请求
                        break

            # 按年月分组
            groups = {}
            for card in all_cards:
                released = card.get('released_at', '')
                if released:
                    year_month = released[:7]  # YYYY-MM
                    if year_month not in groups:
                        groups[year_month] = []
                    groups[year_month].append({
                        'id': card['id'],
                        'name': card['name'],
                        'image_url': _get_card_image_url(card),
                        'released_at': released,
                        'type_line': card.get('type_line', ''),
                        'collector_number': card.get('collector_number', ''),
                    })

            # 按日期降序排列
            sorted_groups = sorted(groups.items(), key=lambda x: x[0], reverse=True)

            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'total': len(all_cards),
                    'groups': [{'date': k, 'cards': v} for k, v in sorted_groups]
                }, ensure_ascii=False)
            }

        elif path == '/api/secret-lair/search':
            # 搜索 Secret Lair 卡牌（按 SLD 编码搜索）
            import requests
            from datetime import datetime

            code = query_params.get('code', '').strip()
            if not code:
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'error': '缺少 code 参数'})
                }

            # 使用 Scryfall 的 cn: 查询（collector_number）
            query = f"set:sld+cn:{code}"
            url = f"https://api.scryfall.com/cards/search?q={query}"
            try:
                resp = requests.get(url, timeout=30)
                result = resp.json()
            except requests.exceptions.RequestException:
                return {
                    'statusCode': 200,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'found': False, 'code': code, 'error': '请求超时'})
                }

            cards = result.get('data', [])
            if not cards:
                return {
                    'statusCode': 200,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({
                        'found': False,
                        'code': code,
                        'card': None
                    }, ensure_ascii=False)
                }

            card = cards[0]
            released_at = card.get('released_at', '')
            year_month = released_at[:7] if released_at else ''

            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'found': True,
                    'code': code,
                    'card': {
                        'id': card['id'],
                        'name': card['name'],
                        'image_url': _get_card_image_url(card),
                        'released_at': released_at,
                        'year_month': year_month,
                        'type_line': card.get('type_line', ''),
                        'collector_number': card.get('collector_number', ''),
                    }
                }, ensure_ascii=False)
            }

        elif path == '/api/ai-judge/init' and http_method == 'POST':
            # 预热 AI Agent
            from backend.services.ai_judge_service import ai_judge_service

            try:
                body_data = json.loads(body) if body else {}
            except json.JSONDecodeError:
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'success': False, 'error': 'Invalid JSON body'})
                }

            openid = body_data.get('openid', None)

            if not openid:
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'success': False, 'error': 'openid is required'})
                }

            result = ai_judge_service.init_agent(openid=openid)
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps(result, ensure_ascii=False)
            }

        elif path == '/api/ai-judge/chat' and http_method == 'POST':
            # AI 裁判对话
            from backend.services.ai_judge_service import ai_judge_service

            try:
                body_data = json.loads(body) if body else {}
            except json.JSONDecodeError:
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'error': 'Invalid JSON body'})
                }

            message = body_data.get('message', '')
            session_id = body_data.get('session_id', 'default')
            clear_history = body_data.get('clear_history', False)
            short_mode = body_data.get('short_mode', False)
            openid = body_data.get('openid', None)

            if not message:
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'success': False, 'reply': '消息不能为空'})
                }

            # 如果请求清除历史
            if clear_history:
                ai_judge_service.clear_session(session_id)

            result = ai_judge_service.chat(message, session_id, short_mode=short_mode, openid=openid)
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps(result, ensure_ascii=False)
            }

        elif path == '/api/ai-judge/clear' and http_method == 'POST':
            # 清除 AI 裁判会话
            from backend.services.ai_judge_service import ai_judge_service

            try:
                body_data = json.loads(body) if body else {}
            except json.JSONDecodeError:
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'error': 'Invalid JSON body'})
                }

            session_id = body_data.get('session_id', 'default')
            openid = body_data.get('openid', None)

            # 如果有 openid，获取对应的 agent_name
            agent_name = None
            if openid:
                try:
                    from backend.services.agent_pool_manager import AgentPoolManager
                    manager = AgentPoolManager()
                    agent_info = manager.db.get_agent_by_openid(openid)
                    if agent_info:
                        agent_name = agent_info['agent_name']
                except Exception as e:
                    print(f"获取 agent_name 失败: {e}")

            ai_judge_service.clear_session(session_id, agent_name=agent_name)
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'success': True, 'message': '会话已清除'})
            }

        elif path == '/api/admin/cleanup-sessions' and http_method == 'POST':
            # 清理所有 OpenCLAW 过期会话
            from backend.services.agent_pool_manager import AgentPoolManager

            manager = AgentPoolManager()
            result = manager.cleanup_all_sessions()
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps(result, ensure_ascii=False)
            }

        elif path == '/api/admin/agent-pool/stats' and http_method == 'POST':
            # 获取 Agent 池统计信息
            from backend.services.agent_pool_manager import AgentPoolManager

            manager = AgentPoolManager()
            stats = manager.get_pool_stats()
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'success': True, 'stats': stats}, ensure_ascii=False)
            }

        elif path == '/api/admin/import-rules' and http_method == 'POST':
            # 从 Cloud Storage 导入规则到数据库
            import sys
            import os
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
            from backend.scripts.import_rules import import_rules_from_storage

            result = import_rules_from_storage()
            return {
                'statusCode': 200 if result.get('success') else 500,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps(result, ensure_ascii=False)
            }

        elif path == '/api/deck/cmc' and http_method == 'POST':
            # 计算套牌 AVG CMC
            # wx.cloud.callFunction 的 data 在 event 顶层，invokeFunction 测试在 event.body
            cards = event.get('cards', [])
            if not cards:
                try:
                    cards = json.loads(body).get('cards', []) if body else []
                except (json.JSONDecodeError, TypeError):
                    cards = []
            if not cards:
                return {'statusCode': 200, 'headers': {'Content-Type': 'application/json'}, 'body': json.dumps({'avgCMC': '0.00', 'cmcMap': {}})}

            import httpx
            cmc_map = {}

            async def fetch_batch(names):
                results = {}
                chunk_size = 75
                for i in range(0, len(names), chunk_size):
                    chunk = names[i:i + chunk_size]
                    identifiers = [{'name': n} for n in chunk]
                    try:
                        async with httpx.AsyncClient(timeout=30.0) as client:
                            resp = await client.post(
                                'https://api.scryfall.com/cards/collection',
                                json={'identifiers': identifiers}
                            )
                            data = resp.json()
                            if data.get('data'):
                                for card in data['data']:
                                    key = card.get('name', '').lower()
                                    type_line = card.get('type_line', '') or ''
                                    is_land = 'Land' in type_line
                                    results[key] = {'cmc': card.get('cmc') or 0, 'is_land': is_land}
                    except Exception as e:
                        print(f'Scryfall batch query failed: {e}')
                return results

            import asyncio
            names = [c['name'] for c in cards]
            cmc_map = asyncio.run(fetch_batch(names))

            total_cmc = 0.0
            total_count = 0
            for card in cards:
                info = cmc_map.get(card['name'].lower(), {'cmc': 0, 'is_land': False})
                mv = info['cmc']
                is_land = info['is_land']
                if is_land:
                    continue  # 去除地牌
                total_cmc += mv * card['count']
                total_count += card['count']

            avg_cmc = f'{total_cmc / total_count:.2f}' if total_count > 0 else '0.00'
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'avgCMC': avg_cmc, 'cmcMap': cmc_map})
            }

        elif path == '/api/deck/parse-url':
            # 从 URL 解析套牌 (MTGGoldfish / Moxfield)
            import html as html_module
            import requests
            from urllib.parse import unquote

            query_string = event.get('queryString', '') or ''
            print(f"DEBUG parse-url query_string={query_string}")
            url = None
            if query_string:
                # 直接从 query_string 提取 url= 后面的内容
                if 'url=' in query_string:
                    url = query_string.split('url=', 1)[1]
                    url = unquote(url.split('&')[0]) if '&' in url else unquote(url)
            print(f"DEBUG parse-url extracted url={url}")

            if not url:
                return {'statusCode': 200, 'headers': {'Content-Type': 'application/json'}, 'body': json.dumps({'success': False, 'error': '缺少 URL 参数'})}

            # 去掉 URL 中的锚点 (#paper 等)
            url = url.split('#')[0]

            # 验证 URL 域名，防止 SSRF 攻击
            from urllib.parse import urlparse
            parsed = urlparse(url)
            allowed_hosts = ['www.mtggoldfish.com', 'mtggoldfish.com']
            if parsed.netloc.lower() not in allowed_hosts:
                return {'statusCode': 200, 'headers': {'Content-Type': 'application/json'}, 'body': json.dumps({'success': False, 'error': '不支持该 URL 类型'})}

            try:
                if parsed.netloc.lower() in allowed_hosts:
                    # MTGGoldfish 解析
                    resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36', 'Accept': 'text/html'}, timeout=30)
                    resp.raise_for_status()
                    html_content = resp.text

                    # 提取 deck_input[deck]
                    deck_input_match = re.search(r'name="deck_input\[deck\]"[^>]*value="([^"]+)"', html_content)
                    if not deck_input_match:
                        return {'statusCode': 200, 'headers': {'Content-Type': 'application/json'}, 'body': json.dumps({'success': False, 'error': '未能解析到套牌数据'})}

                    deck_text = html_module.unescape(deck_input_match.group(1))

                    cards = []
                    seen = {}
                    current_section = "main"
                    for line in deck_text.split('\n'):
                        line = line.strip()
                        if not line:
                            continue
                        if line == '--':
                            current_section = "sideboard"
                            continue
                        if current_section == "sideboard":
                            continue
                        match = re.match(r'^(\d+)[xX]?\s+(.+)$', line)
                        if match:
                            qty = int(match.group(1))
                            card_name = match.group(2).strip()
                            if card_name and qty > 0:
                                key = card_name.lower()
                                if key not in seen:
                                    seen[key] = True
                                    cards.append({'name': card_name, 'count': qty})

                    # 提取名称
                    name_match = re.search(r'<h1[^>]*class="deck-view-title"[^>]*>([^<]+)', html_content)
                    name = name_match.group(1).strip() if name_match else ''

                    if not cards:
                        return {'statusCode': 200, 'headers': {'Content-Type': 'application/json'}, 'body': json.dumps({'success': False, 'error': '未能解析到套牌列表'})}

                    return {'statusCode': 200, 'headers': {'Content-Type': 'application/json'}, 'body': json.dumps({'success': True, 'name': name, 'cards': cards})}

                elif 'moxfield' in url.lower():
                    # Moxfield 解析
                    resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36', 'Accept': 'text/html'}, timeout=30)
                    resp.raise_for_status()
                    html_content = resp.text

                    # 提取标题
                    name_match = re.search(r'<h2[^>]*class="deck-view-info-name"[^>]*>([^<]+)', html_content)
                    name = name_match.group(1).strip() if name_match else 'Moxfield Deck'

                    # 提取卡牌
                    cards = []
                    seen = {}
                    card_matches = re.findall(r'card-view-quantity">(\d+)</span>.*?card-view-name">([^<]+)', html_content, re.DOTALL)
                    for qty, card_name in card_matches:
                        card_name = card_name.strip()
                        if card_name:
                            key = card_name.lower()
                            if key not in seen:
                                seen[key] = True
                                cards.append({'name': card_name, 'count': int(qty)})

                    if not cards:
                        return {'statusCode': 200, 'headers': {'Content-Type': 'application/json'}, 'body': json.dumps({'success': False, 'error': '未能解析到套牌列表'})}

                    return {'statusCode': 200, 'headers': {'Content-Type': 'application/json'}, 'body': json.dumps({'success': True, 'name': name, 'cards': cards})}

                else:
                    return {'statusCode': 200, 'headers': {'Content-Type': 'application/json'}, 'body': json.dumps({'success': False, 'error': '暂不支持该 URL 类型'})}

            except Exception as e:
                return {'statusCode': 200, 'headers': {'Content-Type': 'application/json'}, 'body': json.dumps({'success': False, 'error': f'解析失败: {str(e)}'})}

        elif path == '/api/feedback' and http_method == 'POST':
            # 提交反馈
            from backend.database import RuleDatabase

            try:
                body_data = json.loads(body) if body else {}
            except json.JSONDecodeError:
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'success': False, 'message': 'Invalid JSON body'})
                }

            content = body_data.get('content', '')
            contact = body_data.get('contact', None)
            feedback_type = body_data.get('type', 'suggestion')
            openid = body_data.get('openid', None) or headers.get('x-wx-openid', None)

            if not openid:
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'success': False, 'message': '请先登录后再提交反馈'})
                }

            if not content:
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'success': False, 'message': '反馈内容不能为空'})
                }

            db = RuleDatabase()
            success = db.submit_feedback(openid, content, contact, feedback_type)

            if success:
                return {
                    'statusCode': 200,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'success': True, 'message': '反馈已提交'})
                }
            else:
                return {
                    'statusCode': 500,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'success': False, 'message': '反馈提交失败'})
                }

        elif path == '/api/test-ssh' and http_method == 'POST':
            # 测试 SSH 连接
            import paramiko
            import tempfile
            import os

            try:
                key_content = os.getenv('OPENCLAW_SSH_KEY_CONTENT', '')
                ssh_host = os.getenv('OPENCLAW_HOST', '')
                if not key_content or not ssh_host:
                    return {
                        'statusCode': 500,
                        'headers': {'Content-Type': 'application/json'},
                        'body': json.dumps({'error': 'SSH host or key not configured'})
                    }

                # 创建 SSH 客户端
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

                # 写入临时密钥文件
                fd, key_path = tempfile.mkstemp(suffix='_ssh_key')
                os.write(fd, key_content.encode('utf-8'))
                os.close(fd)
                os.chmod(key_path, 0o600)

                # 连接
                print('Connecting to SSH...')
                client.connect(ssh_host, port=22, username='openclaw', key_filename=key_path, timeout=10)
                print('SSH connected')

                # 执行简单命令
                print('Executing echo test...')
                stdin, stdout, stderr = client.exec_command('echo "hello from SSH"', timeout=10)
                output = stdout.read().decode()
                error = stderr.read().decode()
                print(f'Echo output: {output}')

                # 测试 openclaw 命令
                print('Testing openclaw --version...')
                stdin2, stdout2, stderr2 = client.exec_command('openclaw --version', timeout=10)
                output2 = stdout2.read().decode()
                error2 = stderr2.read().decode()
                print(f'OpenCLAW version output: {output2}')

                # 清理
                os.unlink(key_path)
                client.close()

                return {
                    'statusCode': 200,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({
                        'success': True,
                        'echo_output': output.strip(),
                        'openclaw_version': output2.strip()
                    })
                }
            except Exception as e:
                import traceback
                return {
                    'statusCode': 500,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'error': str(e), 'trace': traceback.format_exc()})
                }

        elif path == '/api/ai-judge/history' and http_method == 'POST':
            # 获取 AI 裁判会话历史
            try:
                body_data = json.loads(body) if body else {}
            except json.JSONDecodeError:
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'success': False, 'error': {'code': 'INVALID_JSON', 'message': 'Invalid JSON body'}})
                }

            openid = body_data.get('openid')
            session_id = body_data.get('session_id')
            limit = int(body_data.get('limit', 10))
            offset = int(body_data.get('offset', 0))

            if not openid:
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'success': False, 'error': {'code': 'MISSING_OPENID', 'message': 'openid 参数必填'}})
                }

            try:
                from backend.services.agent_pool_manager import AgentPoolManager
                from backend.services.openclaw_client import OpenCLAWClient

                # 获取用户的 agent 名称
                agent_manager = AgentPoolManager()
                agent_info = agent_manager.db.get_agent_by_openid(openid)

                if not agent_info:
                    return {
                        'statusCode': 404,
                        'headers': {'Content-Type': 'application/json'},
                        'body': json.dumps({'success': False, 'error': {'code': 'AGENT_NOT_FOUND', 'message': '未找到该用户的会话记录'}})
                    }

                agent_name = agent_info['agent_name']

            except Exception as e:
                return {
                    'statusCode': 500,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'success': False, 'error': {'code': 'DB_ERROR', 'message': str(e)}})
                }

            try:
                client = OpenCLAWClient()

                if session_id:
                    # 返回指定会话的消息
                    messages = client.get_session_messages(agent_name, session_id, limit=limit)

                    # 统计
                    user_count = sum(1 for m in messages if m.get('role') == 'user')
                    assistant_count = sum(1 for m in messages if m.get('role') == 'assistant')

                    return {
                        'statusCode': 200,
                        'headers': {'Content-Type': 'application/json'},
                        'body': json.dumps({
                            'success': True,
                            'data': {
                                'sessionId': session_id,
                                'messages': messages,
                                'summary': {
                                    'totalMessages': len(messages),
                                    'userMessages': user_count,
                                    'assistantMessages': assistant_count
                                }
                            }
                        }, ensure_ascii=False)
                    }
                else:
                    # 返回会话列表
                    result = client.get_sessions(agent_name, limit=limit, offset=offset)
                    return {
                        'statusCode': 200,
                        'headers': {'Content-Type': 'application/json'},
                        'body': json.dumps({
                            'success': True,
                            'data': result
                        }, ensure_ascii=False)
                    }

            except Exception as e:
                return {
                    'statusCode': 500,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'success': False, 'error': {'code': 'SSH_ERROR', 'message': str(e)}})
                }

        elif path == '/api/deck/list' and http_method == 'GET':
            # 获取套牌列表
            openid = query_params.get('openid') or headers.get('x-wx-openid', None)
            if not openid:
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'success': False, 'error': '缺少 openid 参数'})
                }

            from backend.database import RuleDatabase
            db = RuleDatabase()
            db.ensure_decks_table()
            decks = db.get_decks_by_openid(openid)

            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'success': True, 'decks': decks}, ensure_ascii=False, default=str)
            }

        elif path == '/api/deck/add' and http_method == 'POST':
            # 添加套牌
            try:
                body_data = json.loads(body) if body else {}
            except json.JSONDecodeError:
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'success': False, 'error': 'Invalid JSON body'})
                }

            openid = body_data.get('openid') or headers.get('x-wx-openid', None)
            if not openid:
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'success': False, 'error': '缺少 openid 参数'})
                }

            name = body_data.get('name', '')
            format = body_data.get('format', '其他')
            commander = body_data.get('commander', '')
            cards = body_data.get('cards', [])
            total_cards = body_data.get('total_cards', 0)
            avg_cmc = body_data.get('avg_cmc', '0.00')

            if not name:
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'success': False, 'error': '套牌名称不能为空'})
                }

            from backend.database import RuleDatabase
            db = RuleDatabase()
            db.ensure_decks_table()
            deck_id = db.add_deck(openid, name, format, commander, cards, total_cards, avg_cmc)

            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'success': True, 'deck_id': deck_id}, ensure_ascii=False)
            }

        elif re.match(r'^/api/deck/([^/]+)$', path) and http_method == 'DELETE':
            # 删除套牌
            match = re.match(r'^/api/deck/([^/]+)$', path)
            deck_id = match.group(1)

            openid = query_params.get('openid') or headers.get('x-wx-openid', None)
            if not openid:
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'success': False, 'error': '缺少 openid 参数'})
                }

            from backend.database import RuleDatabase
            db = RuleDatabase()
            success = db.delete_deck(deck_id, openid)

            if success:
                return {
                    'statusCode': 200,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'success': True}, ensure_ascii=False)
                }
            else:
                return {
                    'statusCode': 404,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'success': False, 'error': '套牌不存在或无权删除'})
                }

        elif re.match(r'^/api/deck/([^/]+)$', path) and http_method == 'PUT':
            # 更新套牌
            match = re.match(r'^/api/deck/([^/]+)$', path)
            deck_id = match.group(1)

            try:
                body_data = json.loads(body) if body else {}
            except json.JSONDecodeError:
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'success': False, 'error': 'Invalid JSON body'})
                }

            openid = body_data.get('openid') or headers.get('x-wx-openid', None)
            if not openid:
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'success': False, 'error': '缺少 openid 参数'})
                }

            name = body_data.get('name')
            format = body_data.get('format')
            commander = body_data.get('commander')
            cards = body_data.get('cards')
            total_cards = body_data.get('total_cards')
            avg_cmc = body_data.get('avg_cmc')

            from backend.database import RuleDatabase
            db = RuleDatabase()
            success = db.update_deck(deck_id, openid, name, format, commander, cards, total_cards, avg_cmc)

            if success:
                return {
                    'statusCode': 200,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'success': True}, ensure_ascii=False)
                }
            else:
                return {
                    'statusCode': 404,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'success': False, 'error': '套牌不存在或无权更新'})
                }

        elif path == '/api/token/list':
            # Token 列表
            tokens = [
                {"name": "珍宝", "enName": "Treasure", "color": "C", "icon": "💎", "colorName": "无色", "power": 0, "toughness": 0},
                {"name": "复制品", "enName": "Copy", "color": "C", "icon": "🔄", "colorName": "任意", "type": "copy", "power": 0, "toughness": 0},
                {"name": "士兵", "enName": "Soldier", "color": "W", "icon": "⚔️", "colorName": "白", "power": 1, "toughness": 1},
                {"name": "天使", "enName": "Angel", "color": "W", "icon": "👼", "colorName": "白", "power": 3, "toughness": 3, "abilities": "飞行"},
                {"name": "精灵", "enName": "Elf", "color": "W", "icon": "🧝", "colorName": "白", "power": 1, "toughness": 1},
                {"name": "野狼", "enName": "Wolf", "color": "W", "icon": "🐺", "colorName": "白", "power": 2, "toughness": 2},
                {"name": "猫", "enName": "Cat", "color": "W", "icon": "🐱", "colorName": "白", "power": 2, "toughness": 2},
                {"name": "鸟", "enName": "Bird", "color": "U", "icon": "🐦", "colorName": "蓝", "power": 1, "toughness": 1, "abilities": "飞行"},
                {"name": "海洋幻惑", "enName": "Kraken", "color": "U", "icon": "🦑", "colorName": "蓝", "power": 0, "toughness": 0},
                {"name": "元素", "enName": "Elemental", "color": "U", "icon": "🌊", "colorName": "蓝", "power": 0, "toughness": 0},
                {"name": "虚影", "enName": "Illusion", "color": "U", "icon": "👤", "colorName": "蓝", "power": 1, "toughness": 1, "abilities": "飞行"},
                {"name": "灵俑", "enName": "Zombie", "color": "B", "icon": "💀", "colorName": "黑", "power": 2, "toughness": 2},
                {"name": "吸血鬼", "enName": "Vampire", "color": "B", "icon": "🧛", "colorName": "黑", "power": 1, "toughness": 1},
                {"name": "蝙蝠", "enName": "Bat", "color": "B", "icon": "🦇", "colorName": "黑", "power": 1, "toughness": 1, "abilities": "飞行"},
                {"name": "恶魔", "enName": "Demon", "color": "B", "icon": "😈", "colorName": "黑", "power": 5, "toughness": 5, "abilities": "飞行"},
                {"name": "妖精", "enName": "Fae", "color": "B", "icon": "🧚", "colorName": "黑", "power": 0, "toughness": 1},
                {"name": "龙", "enName": "Dragon", "color": "R", "icon": "🐉", "colorName": "红", "power": 2, "toughness": 2, "abilities": "飞行"},
                {"name": "鬼怪", "enName": "Goblin", "color": "R", "icon": "👺", "colorName": "红", "power": 1, "toughness": 1},
                {"name": "元素", "enName": "Elemental", "color": "R", "icon": "🔥", "colorName": "红", "power": 1, "toughness": 1},
                {"name": "龙兽", "enName": "Drake", "color": "R", "icon": "🦅", "colorName": "红", "power": 2, "toughness": 2, "abilities": "飞行"},
                {"name": "战士", "enName": "Warrior", "color": "R", "icon": "⚔️", "colorName": "红", "power": 1, "toughness": 1},
                {"name": "妖精", "enName": "Elf", "color": "G", "icon": "🧝", "colorName": "绿", "power": 1, "toughness": 1},
                {"name": "狼", "enName": "Wolf", "color": "G", "icon": "🐺", "colorName": "绿", "power": 2, "toughness": 2},
                {"name": "巨魔", "enName": "Troll", "color": "G", "icon": "🧌", "colorName": "绿", "power": 3, "toughness": 3},
                {"name": "蜈蚣", "enName": "Squirrel", "color": "G", "icon": "🐿", "colorName": "绿", "power": 1, "toughness": 1},
                {"name": "猫", "enName": "Cat", "color": "G", "icon": "🐱", "colorName": "绿", "power": 2, "toughness": 1},
                {"name": "变形兽", "enName": "Shapeshifter", "color": "C", "icon": "👹", "colorName": "无色", "power": 3, "toughness": 3},
                {"name": "组构体", "enName": "Construct", "color": "C", "icon": "🤖", "colorName": "无色", "power": 4, "toughness": 4},
                {"name": "皮托斯", "enName": "Myr", "color": "C", "icon": "🗿", "colorName": "无色", "power": 0, "toughness": 0},
                {"name": "Marit Lage", "enName": "Marit Lage", "color": "B", "icon": "🌊", "colorName": "黑", "power": 20, "toughness": 20, "abilities": "飞行，不灭"},
            ]
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'tokens': tokens}, ensure_ascii=False)
            }

        elif path == '/api/promos' and http_method == 'GET':
            # Promo 卡查询
            import requests
            from datetime import datetime

            # 获取方式中英文映射表
            acquisition_method_map = {
                'promopack': '补充包促销',
                'stamped': '印戳卡',
                'storechampionship': '店冠军赛',
                'standardshowdown': '标准对决',
                'wizardsplaynetwork': 'WPN促销',
                'bundle': '捆绑包促销',
                'mediainsert': '杂志附赠卡',
                'poster': '海报促销',
                'universesbeyond': '宇宙系列',
                'sourcematerial': '素材卡',
                'ffvii': '最终幻想VII',
            }

            # 支持 year 参数筛选，默认当前年份
            year = query_params.get('year', datetime.today().strftime('%Y'))

            all_cards = []
            seen = {}  # 用于去重 (name + set)

            def fetch_with_retry(url, max_retries=3):
                for attempt in range(max_retries):
                    try:
                        resp = requests.get(url, timeout=30, headers={
                            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                            'Accept': 'application/json'
                        })
                        return resp.json()
                    except requests.exceptions.RequestException as e:
                        if attempt == max_retries - 1:
                            raise
                        import time
                        time.sleep(1)

            # 查询 promo 卡 (排除 MTGO)
            page = 1
            while True:
                query = f'is:promo year:{year}'
                url = f"https://api.scryfall.com/cards/search?q={query}&page={page}"
                result = fetch_with_retry(url)
                cards = result.get('data', [])
                for card in cards:
                    # 排除 Magic Online Promos
                    if card.get('digital', False):
                        continue
                    # 排除重复卡 (按 name + set_code 去重，保留第一个)
                    key = (card.get('name', '').lower(), card.get('set', '').lower())
                    if key in seen:
                        continue
                    seen[key] = True

                    # 获取主要获取方式
                    promo_types = card.get('promo_types', [])
                    acquisition = promo_types[0] if promo_types else ''
                    acquisition_cn = acquisition_method_map.get(acquisition, acquisition)

                    all_cards.append({
                        'name': card.get('name', ''),
                        'set_name': card.get('set_name', ''),
                        'set_code': card.get('set', ''),
                        'released_at': card.get('released_at', ''),
                        'image_url': card.get('image_uris', {}).get('border_crop', '') or card.get('image_uris', {}).get('normal', ''),
                        'type_line': card.get('type_line', ''),
                        'colors': card.get('colors', []),
                        'rarity': card.get('rarity', ''),
                        'acquisition_method': acquisition,
                        'acquisition_method_cn': acquisition_cn,
                        'security_stamp': card.get('security_stamp', ''),
                    })

                if not result.get('has_more'):
                    break
                page += 1
                if page > 10:  # 防止过多请求
                    break

            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': True,
                    'total': len(all_cards),
                    'cards': all_cards
                }, ensure_ascii=False)
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
                        '/api/rule',
                        '/api/card',
                        '/api/mtgch/card',
                        '/api/mtgch/random',
                        '/api/mtgch/autocomplete',
                        '/api/ai-judge/chat',
                        '/api/ai-judge/clear',
                        '/api/ai-judge/history',
                        '/api/admin/cleanup-sessions',
                        '/api/admin/agent-pool/stats',
                        '/api/admin/import-rules',
                        '/api/feedback',
                        '/api/promos',
                        '/api/token/list'
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
