# mtgAsk 测试文档

## 1. 测试策略

### 1.1 测试分层

| 测试层级 | 位置 | 说明 | 运行方式 |
|---------|------|------|---------|
| 单元测试 | `tests/unit/` | 使用 mock 模拟外部依赖，无需网络 | `pytest tests/unit/ -v` |
| 集成测试 | `tests/integration/` | 需要数据库环境，默认跳过 | `pytest tests/integration/ -v -m integration` |
| 云函数测试 | `tests/cloud/` | 需要外部网络，默认跳过 | `pytest tests/cloud/ -v -m cloud` |

### 1.2 测试依赖

```bash
pip install pytest pytest-asyncio
```

### 1.3 pytest 标记

| 标记 | 说明 |
|-----|------|
| `@pytest.mark.integration` | 集成测试，需要数据库环境 |
| `@pytest.mark.cloud` | 云函数测试，需要网络连接 |
| `@pytest.mark.skip` | 跳过测试 |

---

## 2. 单元测试

### 2.1 测试文件清单

| 文件 | 测试内容 | 测试数 |
|-----|---------|--------|
| `test_mtgch_api.py` | MTGCH API 客户端功能 | 27 |
| `test_openclaw_client.py` | OpenCLAW SSH 客户端 | 28 |
| `test_agent_pool_manager.py` | Agent 池管理器 | 23 |
| `test_ai_judge_daily_limit.py` | AI 裁判每日限制 | - |
| `test_deck_parser.py` | 套牌 URL 解析 | - |
| `test_routes.py` | FastAPI 路由 | 24（待修复） |

### 2.2 MTGCH API 测试

**文件：** `tests/unit/test_mtgch_api.py`

```python
# 测试用例示例
def test_search_cards_success(mock_session):
    """测试搜索卡牌成功"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"items": [...]}
    mock_session.get.return_value = mock_response
    
    client = MTGCHAPIClient()
    result = client.search_cards("闪电风暴")
    
    assert "items" in result
    assert len(result["items"]) > 0

@pytest.mark.parametrize("rarity,expected", [
    ("C", "普通"),
    ("U", "非普通"),
    ("R", "稀有"),
    ("M", "秘稀"),
])
def test_format_card_info_rarity_mapping(self, rarity, expected):
    """测试稀有度映射"""
    ...
```

**运行：**
```bash
pytest tests/unit/test_mtgch_api.py -v
```

### 2.3 OpenCLAW 客户端测试

**文件：** `tests/unit/test_openclaw_client.py`

```python
# 测试用例示例
def test_execute_command_success(mock_ssh_client):
    """测试命令执行成功"""
    mock_stdout = Mock()
    mock_stdout.read.return_value = '{"success": true}'
    mock_stderr = Mock()
    mock_stderr.read.return_value = ''
    mock_ssh_client.exec_command.return_value = (None, mock_stdout, mock_stderr)
    
    client = OpenCLAWClient()
    result = client.execute_command("openclaw --version")
    
    assert result["success"] == True
```

### 2.4 Agent 池管理器测试

**文件：** `tests/unit/test_agent_pool_manager.py`

```python
# 测试用例示例
def test_get_or_create_agent_new_user(mock_db):
    """测试为新用户创建 Agent"""
    mock_db.get_agent_by_openid.return_value = None
    mock_db.create_agent.return_value = True
    
    manager = AgentPoolManager()
    agent_name = manager.get_or_create_agent("new_user_openid")
    
    assert agent_name.startswith("user_")
    mock_db.create_agent.assert_called_once()
```

---

## 3. 集成测试

### 3.1 测试文件

| 文件 | 测试内容 |
|-----|---------|
| `test_first_stage.py` | 第一阶段功能测试 |
| `test_card_service.py` | 卡牌服务测试 |
| `test_rule_downloader.py` | 规则下载测试 |
| `test_ai_judge_service.py` | AI 裁判服务测试 |

### 3.2 运行方式

```bash
# 需要先配置数据库环境变量
export MYSQL_HOST=sh-cynosdbmysql-grp-5ydpqjru.sql.tencentcdb.com
export MYSQL_PORT=27987
export MYSQL_USER=mtingask
export MYSQL_PASSWORD=your_password
export MYSQL_DATABASE=magic-rules-assistant-0a1904c329

# 运行集成测试
pytest tests/integration/ -v -m integration
```

### 3.3 本地开发数据库

本地开发可使用 SQLite 或外部 MySQL（配置在 `.env.local`）：

```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r functions/mtgAsk/requirements.txt
```

---

## 4. API 测试

### 4.1 本地服务测试

**启动本地服务：**
```bash
python functions/mtgAsk/backend/main.py
# 或
bash deployment/scripts/start.sh
```

**测试端点：**
```bash
# 服务状态
curl http://localhost:8000/

# 规则搜索
curl 'http://localhost:8000/api/search?q=飞行'

# 关键词异能
curl 'http://localhost:8000/api/keyword?k=践踏'

# 卡牌搜索
curl 'http://localhost:8000/api/card?n=黑莲花'

# AI 裁判
curl -X POST http://localhost:8000/api/ai-judge/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "闪电击伤害", "openid": "test_user"}'
```

### 4.2 云函数测试脚本

**文件：** `test_cloud_api.sh`

```bash
#!/bin/bash
# CloudBase 云函数 API 测试

# 服务状态
tcb fn invoke mtgAsk --params '{"httpMethod":"GET","path":"/","queryString":""}'

# 卡牌搜索
tcb fn invoke mtgAsk --params '{"httpMethod":"GET","path":"/api/mtgch/search","queryString":"q=闪电风暴"}'
```

---

## 5. 测试最佳实践

### 5.1 测试原则

1. **独立性**：每个测试独立运行，不依赖其他测试
2. **可重复性**：单元测试使用 mock，不依赖外部服务
3. **明确性**：测试名称清晰描述测试内容
4. **快速性**：单元测试应快速执行

### 5.2 Mock 使用示例

```python
from unittest.mock import Mock, patch, MagicMock

def test_with_mock():
    """使用 Mock 模拟外部依赖"""
    with patch('requests.Session') as mock_session_class:
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": []}
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        client = MTGCHAPIClient()
        result = client.search_cards("test")
        
        assert "items" in result
```

### 5.3 参数化测试

```python
import pytest

@pytest.mark.parametrize("input,expected", [
    ("飞行", True),
    ("Flying", False),
    ("", False),
])
def test_keyword_detection(input, expected):
    """测试关键词检测"""
    is_chinese = bool(re.search(r'[一-鿿]', input))
    assert bool(is_chinese) == expected
```

---

## 6. 测试覆盖

### 6.1 当前测试状态

| 文件 | 状态 | 通过数 |
|-----|------|--------|
| `test_mtgch_api.py` | 通过 | 27 |
| `test_openclaw_client.py` | 通过 | 28 |
| `test_agent_pool_manager.py` | 通过 | 23 |
| `test_routes.py` | 待修复 | - |

**总测试数**：78 个通过

### 6.2 待修复问题

**test_routes.py：** starlette 0.27.0 与 httpx 0.28.1 不兼容

**解决方案：**
```bash
# 方案1：降级 starlette
pip install starlette==0.27.0

# 方案2：升级 httpx
pip install httpx>=0.28.1
```

---

## 7. 测试工具

### 7.1 路径调试

**文件：** `tests/utils/test_path_debug.py`

用于调试模块导入路径问题。

```python
import sys
import os

def test_path_debug():
    """调试路径问题"""
    print("Python path:")
    for p in sys.path:
        print(f"  {p}")
    
    # 检查 vendor 目录
    vendor_path = "functions/mtgAsk/vendor"
    print(f"\nVendor exists: {os.path.exists(vendor_path)}")
```

### 7.2 Cloud 函数测试

**文件：** `tests/cloud/test_cloud_mtgch_correct.py`

通过 CloudBase MCP 工具调用云函数进行测试。

```python
# 使用 MCP 工具调用
mcp__cloudbase__manageFunctions({
  action: "invokeFunction",
  functionName: "mtgAsk",
  params: {
    httpMethod: "GET",
    path: "/api/mtgch/search",
    queryString: "q=闪电风暴"
  }
})
```

---

## 8. 持续集成

### 8.1 本地预提交检查

```bash
# 运行所有单元测试
pytest tests/unit/ -v

# 运行特定测试
pytest tests/unit/test_mtgch_api.py tests/unit/test_openclaw_client.py -v
```

### 8.2 测试覆盖报告

```bash
# 生成覆盖率报告
pip install pytest-cov
pytest tests/unit/ --cov=functions/mtgAsk/backend --cov-report=html
```

---

*文档版本: 1.0*
*最后更新: 2026-05-27*