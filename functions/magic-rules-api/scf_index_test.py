#!/usr/bin/env python3
"""
简化测试版本 - 不依赖数据库
"""
import sys
import os
from urllib.parse import parse_qs
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """处理 GET 请求"""
        path = self.path
        query_params = {}
        
        if '?' in path:
            path, query_string = path.split('?', 1)
            query_params = parse_qs(query_string)
            query_params = {k: v[0] if len(v) == 1 else v for k, v in query_params.items()}
        
        # 规则搜索 API
        if path in ('/api/search', '/search'):
            q = query_params.get('q', '')
            response = {'query': q, 'count': 1, 'results': {'rules': [], 'keyword_abilities': [], 'cards': [], 'qa_templates': []}}
            self._send_json(200, response)
            return
        
        # 关键词查询 API
        elif path in ('/api/keyword', '/keyword'):
            keyword = query_params.get('k', '')
            response = {'keyword': keyword, 'result': None}
            self._send_json(200, response)
            return
        
        # 其他路径
        self._send_json(200, {'message': '测试服务运行中', 'path': path, 'query_params': query_params})
    
    def _send_json(self, status_code, data):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

def main():
    port = int(os.environ.get('SCF_PORT', 9000))
    print(f"Starting test server on port {port}...")
    server = HTTPServer(('0.0.0.0', port), RequestHandler)
    server.serve_forever()

if __name__ == '__main__':
    main()
