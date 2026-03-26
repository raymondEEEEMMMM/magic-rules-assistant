# 云端 API 部署完整指南

本文档详细记录了 Magic Rules Assistant 在 CloudBase 上的完整部署过程，包括遇到的问题和解决方案。

## 目录

1. [项目概述](#项目概述)
2. [部署前准备](#部署前准备)
3. [CloudBase 环境配置](#cloudbase-环境配置)
4. [云函数部署](#云函数部署)
5. [问题诊断与解决](#问题诊断与解决)
6. [数据库方案选择](#数据库方案选择)
7. [最终实现方案](#最终实现方案)
8. [验证与测试](#验证与测试)
9. [维护指南](#维护指南)

---

## 项目概述

### 项目结构

```
cbworkplace/
├── backend/              # 后端服务
│   ├── api.py           # API 入口
│   ├── config.py        # 配置管理
│   ├── database.py      # 数据库操作
│   └── services/        # 业务服务
├── functions/           # 云函数代码
│   └── magic-rules-api/
│       ├── scf_index.py # 云函数入口
│       ├── backend/     # 后端代码副本
│       └── requirements.txt
├── data/               # 本地数据
│   └── magic_rules.db  # SQLite 数据库
└── tests/              # 测试脚本
    └── quick_test.py   # 快速测试
```

### API 端点列表

| 端点 | 方法 | 功能 | 数据库依赖 |
|-----|------|------|-----------|
| `/api/search` | GET | 规则搜索 | SQLite |
| `/api/keyword` | GET | 关键词查询 | SQLite |
| `/api/card` | GET | 卡牌查询 | SQLite |
| `/api/mtgch/search` | GET | MTGCH 卡牌搜索 | HTTP API |
| `/api/mtgch/card` | GET | MTGCH 卡牌详情 | HTTP API |
| `/api/mtgch/random` | GET | MTGCH 随机卡牌 | HTTP API |
| `/api/mtgch/autocomplete` | GET | MTGCH 自动补全 | HTTP API |

---

## 部署前准备

### 1. 安装 CloudBase CLI

```bash
# 全局安装
npm install -g @cloudbase/cli

# 验证安装
tcb --version
```

### 2. 登录 CloudBase

```bash
# 扫码登录
tcb login

# 验证登录状态
tcb env list
```

### 3. 初始化项目配置

```bash
# 在项目根目录执行
tcb init

# 选择配置项：
# - 环境: magic-rules-assistant-0a1904c329
# - 服务: magic-rules-api
# - 框架: None (自定义)
```

生成的配置文件 `cloudbaserc.json`:

```json
{
  "envId": "magic-rules-assistant-0a1904c329",
  "$schema": "https://framework-1258016615.tcloudbaseapp.com/schema/latest.json",
  "version": "2.0",
  "framework": {
    "name": "magic-rules",
    "plugins": {}
  }
}
```

---

## CloudBase 环境配置

### 1. 创建环境（如未存在）

```bash
# 通过控制台创建或使用 CLI
tcb env create magic-rules-assistant
```

### 2. 配置环境变量

在 CloudBase 控制台设置以下环境变量：

| 变量名 | 值 | 说明 |
|-------|---|------|
| `WECHAT_TOKEN` | `wx_mtg_rules_2024` | 微信验证令牌 |
| `ENVIRONMENT` | `production` | 运行环境 |

### 3. 启用云存储 ~~（已废弃）~~

> ⚠️ **已废弃**: 云存储方案不再用于数据库。请跳过此步骤。

```bash
# 旧版命令（请勿使用）
# tcb storage init
# tcb storage upload data/magic_rules.db
```

---

## 云函数部署

### 1. 准备函数代码

```bash
# 创建函数目录结构
mkdir -p functions/magic-rules-api/backend

# 复制后端代码
cp -r backend/* functions/magic-rules-api/backend/
cp backend/config.py functions/magic-rules-api/backend/
cp backend/api.py functions/magic-rules-api/backend/
cp backend/database.py functions/magic-rules-api/backend/
cp -r backend/services functions/magic-rules-api/backend/
```

### 2. 编写 requirements.txt

```txt
# CloudBase HTTP Cloud Function Dependencies
# Python 3.10 runtime

# HTTP 请求库
requests==2.31.0
urllib3==2.0.7

# 配置管理
python-dotenv==1.0.0
```

### 3. 编写云函数入口 (scf_index.py)

核心实现：

```python
#!/usr/bin/env python3
"""
CloudBase HTTP 云函数入口
需要监听 9000 端口处理 HTTP 请求
"""
import sys
import os
from urllib.parse import parse_qs
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

# 添加 backend 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# 从云存储下载数据库文件到本地 /tmp 目录
def download_database():
    """从云存储下载数据库文件"""
    import urllib.request
    
    # 云存储下载链接（需定期更新签名）
    CLOUD_STORAGE_URL = "https://6d61-magic-rules-assistant-0a1904c329-1410769303.tcb.qcloud.la/magic_rules.db?..."
    local_path = "/tmp/magic_rules.db"
    
    # 检查本地缓存
    if os.path.exists(local_path):
        print(f"✓ Using cached database: {local_path}")
        return local_path
    
    try:
        print(f"Downloading database from cloud storage...")
        urllib.request.urlretrieve(CLOUD_STORAGE_URL, local_path)
        print(f"✓ Database downloaded: {local_path}")
        return local_path
    except Exception as e:
        print(f"✗ Failed to download database: {e}")
        raise

def ensure_database():
    """确保数据库已下载（在 API 请求前调用）"""
    db_path = "/tmp/magic_rules.db"
    if not os.path.exists(db_path):
        download_database()
    elif not os.environ.get('DATABASE_PATH'):
        os.environ['DATABASE_PATH'] = db_path
    return db_path

# 配置加载
try:
    from backend.config import Config
    WECHAT_TOKEN = Config.WECHAT_TOKEN
    print("✓ Loaded WECHAT_TOKEN from backend.config")
except Exception as e:
    print(f"✗ Config import error: {e}, using environment variable")
    WECHAT_TOKEN = os.environ.get('WECHAT_TOKEN', 'wx_mtg_rules_2024')

# HTTP 请求处理器
class RequestHandler(BaseHTTPRequestHandler):
    """HTTP 请求处理器"""
    
    def log_message(self, format, *args):
        """覆盖默认的日志输出"""
        print(f"[{self.log_date_time_string()}] {format % args}")
    
    def do_GET(self):
        """处理 GET 请求"""
        # 解析请求路径和参数
        path = self.path.split('?')[0]
        query_params = parse_qs(self.path.split('?')[1] if '?' in self.path else '')
        
        print(f"Full path: {self.path}")
        print(f"Parsed path: {path}")
        print(f"Query params: {query_params}")
        
        # 关键词查询 API（支持 /api/keyword 和 /keyword）
        if path in ('/api/keyword', '/keyword'):
            ensure_database()  # 确保数据库已下载
            try:
                from backend.database import RuleDatabase
                from backend.services import RuleService
                
                keyword = query_params.get('k', [''])[0]
                
                db = RuleDatabase()
                service = RuleService(db)
                result = service.get_keyword_details(keyword)
                
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
        
        # 其他 API 端点...
        
        # 默认响应
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        response = {'message': 'Magic Rules API', 'endpoints': [...]}
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

def main():
    """启动 HTTP 服务器"""
    print("Starting HTTP server on port 9000...")
    server = HTTPServer(('0.0.0.0', 9000), RequestHandler)
    print(f"Server is running on http://0.0.0.0:9000")
    server.serve_forever()

if __name__ == '__main__':
    main()
```

### 4. 部署云函数

```bash
# 方式 1: 使用 CloudBase CLI
tcb functions deploy magic-rules-api

# 方式 2: 使用 MCP 工具（推荐）
# 在 AI 助手中调用 CloudBase MCP 工具
```

### 5. 配置 HTTP 访问

```bash
# 创建 HTTP 访问路径
tcb gateway:api create \
  --name magic-rules-api \
  --path /api \
  --type HTTP \
  --serviceName magic-rules-api \
  --functionName magic-rules-api
```

或使用 MCP 工具：

```python
mcp_call_tool(
    serverName="CloudBase MCP",
    toolName="createFunctionHTTPAccess",
    arguments='{"name": "magic-rules-api", "path": "/api", "type": "HTTP"}'
)
```

---

## 问题诊断与解决

### 问题 1: HTTP 400 Bad Request

**症状**: 
```
curl: (52) Empty reply from server
```

**原因**: HTTP 访问路径未配置，只有 `/wechat` 路径可访问

**解决方案**:
- 创建 `/api` 路径的 HTTP 访问配置
- 确保函数类型为 HTTP 类型

### 问题 2: 路径不匹配

**症状**: 
```
请求: /api/keyword
实际接收: /keyword
函数期望: /api/keyword
结果: 不匹配
```

**原因**: CloudBase 自动去掉 `/api` 前缀

**解决方案**:
```python
# 同时支持两种路径格式
if path in ('/api/keyword', '/keyword'):
    # 处理逻辑
```

### 问题 3: 缺少依赖包

**症状**:
```python
No module named 'dotenv'
```

**原因**: `backend/config.py` 导入 `dotenv`，但 `requirements.txt` 中缺失

**解决方案**:
```txt
# 在 requirements.txt 中添加
python-dotenv==1.0.0
```

### 问题 4: 数据库文件无法访问

**症状**:
```python
unable to open database file
```

**原因**: 
1. 数据库文件未打包到云函数
2. 云函数无状态，本地文件无法持久化

**解决方案对比**:

| 方案 | 优点 | 缺点 | 推荐度 |
|-----|------|------|--------|
| ~~方案1: 云存储+运行时下载~~ | ~~避免脚本过大~~ | ~~首次请求延迟~~ | ~~❌ 已废弃~~ |
| ~~方案2: 内嵌初始化代码~~ | ~~无外部依赖~~ | ~~脚本过大~~ | ~~❌ 已废弃~~ |
| **方案3: CloudBase MySQL** | 正式生产方案 | 迁移成本高 | ⭐⭐⭐⭐⭐ |

---

## 数据库方案选择

> ⚠️ **历史说明**: 以下文档描述了旧版 SQLite + 云存储方案，该方案已被废弃。
> 当前生产环境使用 **CloudBase MySQL** 作为数据库。

### 方案对比分析

#### ~~方案1: 云存储 + 运行时下载~~ ❌ 已废弃

> 请勿使用此方案

**实现方式**:
```python
def download_database():
    CLOUD_STORAGE_URL = "https://6d61-magic-rules-assistant-0a1904c329-1410769303.tcb.qcloud.la/magic_rules.db?..."
    local_path = "/tmp/magic_rules.db"
    urllib.request.urlretrieve(CLOUD_STORAGE_URL, local_path)
```

**弃用原因**:
- AI Agent 方案不再使用云存储读取
- 知识库通过 SSH/rsync 直接同步到 OpenCLAW Gateway

#### ~~方案2: 内嵌初始化代码~~ ❌ 已废弃

**实现方式**:
```python
# 将 SQL 导出为 Python 字符串
INIT_SQL = """
CREATE TABLE IF NOT EXISTS rules (...)
INSERT INTO rules VALUES (...);
-- 200MB 的 SQL 语句
"""

def init_database():
    conn = sqlite3.connect('/tmp/magic_rules.db')
    conn.executescript(INIT_SQL)
```

**优点**:
- 无外部依赖
- 首次请求更快（只需写入，无需下载）

**缺点**:
- 代码文件过大（200MB+）
- 部署时间极长
- 不便于维护

#### 方案3: CloudBase MySQL

**实现方式**:
```python
# 迁移到 CloudBase 关系型数据库
DATABASE_URL = f"mysql://user:pass@{MYSQL_HOST}/magic_rules"
```

**优点**:
- 正式的生产环境方案
- 性能最佳
- 支持高并发

**缺点**:
- 需要数据迁移
- 有额外成本
- 配置复杂

---

## 最终实现方案

> ⚠️ **当前架构**: 本文档描述的云存储方案已废弃。当前使用以下架构：

### 当前架构设计

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  微信小程序     │────▶│  CloudBase      │────▶│   MySQL         │
│  / 其他客户端   │     │  云函数         │     │   数据库         │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                                 │
                                 ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │  OpenCLAW       │────▶│  知识库         │
                        │  Gateway        │     │  (SSH 同步)     │
                        └─────────────────┘     └─────────────────┘
```

### 关键配置

| 配置项 | 值 |
|--------|-----|
| 数据库类型 | CloudBase MySQL |
| AI 裁判 | OpenCLAW Gateway |
| 知识库同步 | SSH/rsync 到 OpenCLAW 服务器 |

---

## ❌ 废弃：旧版云存储方案

> 以下内容为历史文档，仅供参考。请勿使用。

### 架构设计（旧版）

```
客户端请求
    ↓
CloudBase API 网关
    ↓
云函数 (magic-rules-api)
    ├─ 首次请求: 下载数据库到 /tmp
    ├─ 后续请求: 使用缓存数据库
    └─ 处理业务逻辑
    ↓
返回响应
```

### 关键代码实现（旧版）

#### 1. 数据库下载函数（旧版）

```python
def download_database():
    """从云存储下载数据库文件"""
    import urllib.request

    # 云存储下载链接（1小时有效，需定期更新）
    CLOUD_STORAGE_URL = "https://6d61-magic-rules-assistant-0a1904c329-1410769303.tcb.qcloud.la/magic_rules.db?sign=..."
    local_path = "/tmp/magic_rules.db"

    # 检查本地缓存
    if os.path.exists(local_path):
        print(f"✓ Using cached database: {local_path}")
        return local_path

    try:
        print(f"Downloading database from cloud storage...")
        urllib.request.urlretrieve(CLOUD_STORAGE_URL, local_path)
        print(f"✓ Database downloaded: {local_path}")
        return local_path
    except Exception as e:
        print(f"✗ Failed to download database: {e}")
        raise
```

#### 2. 数据库确保函数

```python
def ensure_database():
    """确保数据库已下载（在 API 请求前调用）"""
    db_path = "/tmp/magic_rules.db"
    if not os.path.exists(db_path):
        download_database()
    elif not os.environ.get('DATABASE_PATH'):
        os.environ['DATABASE_PATH'] = db_path
    return db_path
```

#### 3. API 路由配置

```python
# 关键词查询 API
if path in ('/api/keyword', '/keyword'):
    ensure_database()  # 确保数据库已下载
    try:
        from backend.database import RuleDatabase
        from backend.services import RuleService
        
        keyword = query_params.get('k', [''])[0]
        
        db = RuleDatabase()
        service = RuleService(db)
        result = service.get_keyword_details(keyword)
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))
        return
    except Exception as e:
        # 错误处理
        ...
```

### 部署流程

```bash
# 1. 上传数据库到云存储
tcb storage upload data/magic_rules.db

# 2. 更新云函数代码（包含下载逻辑）
tcb functions deploy magic-rules-api

# 3. 配置 HTTP 访问
tcb gateway:api create --name magic-rules-api --path /api --type HTTP

# 4. 测试 API
curl "https://magic-rules-assistant-0a1904c329-1410769303.ap-shanghai.app.tcloudbase.com/api/keyword?k=飞行"
```

---

## 验证与测试

### 快速测试脚本

创建 `tests/quick_test.py`:

```python
#!/usr/bin/env python3
import requests
import json

BASE_URL = "https://magic-rules-assistant-0a1904c329-1410769303.ap-shanghai.app.tcloudbase.com"

def test_api():
    """测试关键 API 端点"""
    
    # 测试 1: 关键词查询
    print("Testing /api/keyword...")
    response = requests.get(f"{BASE_URL}/api/keyword", params={'k': '飞行'})
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    
    # 测试 2: 规则搜索
    print("\nTesting /api/search...")
    response = requests.get(f"{BASE_URL}/api/search", params={'q': '践踏'})
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")

if __name__ == '__main__':
    test_api()
```

### 测试步骤

```bash
# 1. 运行快速测试
python3 tests/quick_test.py

# 2. 查看函数日志
tcb functions:logs magic-rules-api

# 3. 验证响应格式
curl -s "https://magic-rules-assistant-0a1904c329-1410769303.ap-shanghai.app.tcloudbase.com/api/keyword?k=飞行" | python3 -m json.tool
```

### 预期结果

```json
{
  "keyword": "飞行",
  "rules": [
    {
      "rule_text": "702.15. 飞行是一种与某些生物相关的关键词能力...",
      "rule_type": "核心规则"
    }
  ],
  "related_cards": [
    "飞翔瓦斯特卡"
  ]
}
```

---

## 维护指南

### 日常维护

#### 1. 更新数据库

> ⚠️ **已废弃**: 当前使用 MySQL 数据库，无需手动上传。

```bash
# 旧版命令（请勿使用）
# python3 update_rules.py
# tcb storage upload data/magic_rules.db
```

**当前方式**: MySQL 数据库由 CloudBase 自动管理，无需手动更新。
如需更新规则数据，请联系管理员。
```

#### 2. 更新云函数代码

```bash
# 修改代码后重新部署
tcb functions deploy magic-rules-api

# 查看部署状态
tcb functions:detail magic-rules-api
```

#### 3. 监控和日志

```bash
# 查看实时日志
tcb functions:logs magic-rules-api --tail

# 查看特定时间段的日志
tcb functions:logs magic-rules-api --start "2026-03-13 00:00:00" --end "2026-03-13 23:59:59"
```

### 性能优化

#### ~~1. 缓存策略~~ ❌ 已废弃

> 当前使用 MySQL，无需此缓存策略。

- ~~利用 `/tmp` 目录的持久性~~
- ~~同一实例的多次请求共享数据库缓存~~
- ~~冷启动时才需要下载~~

#### 2. 并发控制

```python
# 在函数配置中设置
最大并发数: 10  # 避免过多并发导致重复下载
```

#### 3. 超时设置

```python
# 在函数配置中设置
超时时间: 60秒  # 足够完成数据库下载
```

### 故障排除

#### ~~问题: 数据库下载失败~~ ❌ 已废弃

> 使用 MySQL 后不再有此问题

**症状**:
```
✗ Failed to download database: ...
unable to open database file
```

**排查步骤**:
1. ~~检查云存储链接是否过期~~
2. ~~验证网络连接~~
3. ~~查看函数日志中的详细错误~~
4. ~~检查 `/tmp` 目录权限~~

#### 问题: 依赖包未安装

**症状**:
```
No module named 'xxx'
```

**排查步骤**:
1. 检查 `requirements.txt` 是否完整
2. 确认函数已重新部署
3. 查看函数初始化日志

#### 问题: API 响应慢

**症状**: 首次请求返回时间 > 10秒

**原因**: 冷启动 + 数据库下载

**优化**:
- 预热函数（定时触发）
- 考虑迁移到 MySQL
- 使用函数预热机制

---

## 附录

### A. CloudBase 常用命令

```bash
# 环境管理
tcb env list              # 列出所有环境
tcb env info              # 查看当前环境信息

# 函数管理
tcb functions list        # 列出所有函数
tcb functions:deploy      # 部署函数
tcb functions:detail      # 查看函数详情
tcb functions:logs        # 查看函数日志

# 网关管理
tcb gateway:api list      # 列出所有 API
tcb gateway:api create    # 创建 API
tcb gateway:api delete    # 删除 API

# 存储管理
tcb storage init          # 初始化云存储
tcb storage upload       # 上传文件
tcb storage download     # 下载文件
```

### B. MCP 工具调用示例

```python
# 获取函数列表
mcp_call_tool(
    serverName="CloudBase MCP",
    toolName="getFunctionList",
    arguments='{"action": "list"}'
)

# 部署函数代码
mcp_call_tool(
    serverName="CloudBase MCP",
    toolName="updateFunctionCode",
    arguments='{"name": "magic-rules-api", "functionRootPath": "/path/to/functions"}'
)

# 创建 HTTP 访问
mcp_call_tool(
    serverName="CloudBase MCP",
    toolName="createFunctionHTTPAccess",
    arguments='{"name": "magic-rules-api", "path": "/api", "type": "HTTP"}'
)

# 上传文件到云存储
mcp_call_tool(
    serverName="CloudBase MCP",
    toolName="manageStorage",
    arguments='{"action": "upload", "localPath": "/path/to/file", "cloudPath": "file.db"}'
)

# 查询函数日志
mcp_call_tool(
    serverName="CloudBase MCP",
    toolName="getFunctionLogs",
    arguments='{"name": "magic-rules-api", "limit": 10}'
)

# 获取日志详情
mcp_call_tool(
    serverName="CloudBase MCP",
    toolName="getFunctionLogDetail",
    arguments='{"requestId": "xxx-xxx-xxx"}'
)
```

### C. 环境变量配置

| 变量名 | 值 | 说明 |
|-------|---|------|
| `WECHAT_TOKEN` | `wx_mtg_rules_2024` | 微信验证令牌 |
| `ENVIRONMENT` | `production` | 运行环境 |
| `DATABASE_PATH` | `/tmp/magic_rules.db` | 数据库路径（运行时设置） |

### D. 相关文档

- [CloudBase 官方文档](https://docs.cloudbase.net/)
- [云函数开发指南](https://docs.cloudbase.net/cloud-function/intro.html)
- [API 网关配置](https://docs.cloudbase.net/api-gateway/intro.html)
- [云存储使用指南](https://docs.cloudbase.net/storage/intro.html)

---

## 更新日志

| 日期 | 版本 | 更新内容 |
|-----|------|---------|
| 2026-03-13 | v1.0 | 初始版本，完成基础部署 |
| 2026-03-13 | v1.1 | 修复路径不匹配问题 |
| 2026-03-13 | v1.2 | 添加缺失依赖包 |
| ~~2026-03-13~~ | ~~v1.3~~ | ~~实现云存储数据库方案~~ ❌ 已废弃 |
| ~~2026-03-13~~ | ~~v1.4~~ | ~~优化数据库下载逻辑~~ ❌ 已废弃 |

---

## 联系方式

如有问题或建议，请联系项目维护者或提交 Issue。
