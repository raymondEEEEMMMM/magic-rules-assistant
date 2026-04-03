# 测试目录

本目录包含万智牌规则问答公众号项目的所有测试用例。

## 目录结构

```
tests/
├── README.md                    # 本文件
├── unit/                        # 单元测试
│   └── test_mtgch_api.py       # MTGCH API 单元测试（使用 pytest + mock）
├── integration/                 # 集成测试
│   ├── test_first_stage.py      # 第一阶段功能测试
│   ├── test_card_service.py     # 卡牌服务测试
│   └── test_rule_downloader.py  # 规则下载测试
├── cloud/                       # 云函数测试
│   ├── test_cloud_mtgch.py      # CloudBase 云函数测试（v1）
│   ├── test_cloud_mtgch_correct.py  # CloudBase 云函数测试（修正版）
│   └── test_cloud_mtgch_v2.py   # CloudBase 云函数测试（v2）
└── utils/                       # 测试工具
    └── test_path_debug.py       # 路径调试测试
```

## 快速开始

### 安装测试依赖

```bash
pip install pytest pytest-asyncio
```

### 运行测试

```bash
# 进入项目根目录
cd /Users/lianghaoming/cbworkplace

# 激活虚拟环境
source venv/bin/activate

# 运行所有测试
pytest tests/ -v

# 运行单元测试（推荐）
pytest tests/unit/ -v

# 运行特定测试文件
pytest tests/unit/test_mtgch_api.py -v
```

## 测试分类

### 1. 单元测试 (tests/unit/)

使用 **pytest** 框架，通过 **mock** 模拟网络请求，无需外部依赖。

| 文件 | 测试内容 |
|------|----------|
| `test_mtgch_api.py` | MTGCH API 客户端功能测试（27 个测试） |
| `test_openclaw_client.py` | OpenCLAW SSH 客户端测试（28 个测试） |
| `test_agent_pool_manager.py` | Agent 池管理器测试（23 个测试） |
| `test_routes.py` | FastAPI 路由测试（24 个测试）⚠️ 需要修复 starlette/httpx 兼容性 |

**运行方式**:
```bash
pytest tests/unit/ -v
```

### 2. 集成测试 (tests/integration/)

需要数据库环境，默认跳过。

| 文件 | 测试内容 |
|------|----------|
| `test_first_stage.py` | 第一阶段功能测试 |
| `test_card_service.py` | 卡牌服务测试 |
| `test_rule_downloader.py` | 规则下载测试 |

**运行方式**:
```bash
# 运行集成测试（需要数据库环境）
pytest tests/integration/ -v -m integration
```

### 3. 云函数测试 (tests/cloud/)

需要外部网络连接，默认跳过。

| 文件 | 版本 | 说明 |
|------|------|------|
| `test_cloud_mtgch.py` | v1 | 初版云函数测试 |
| `test_cloud_mtgch_correct.py` | 修正版 | 修正版测试 |
| `test_cloud_mtgch_v2.py` | v2 | 微信路径测试 |

**运行方式**:
```bash
# 运行云函数测试（需要网络）
pytest tests/cloud/ -v -m cloud
```

### 4. 工具测试 (tests/utils/)

| 文件 | 说明 |
|------|------|
| `test_path_debug.py` | 路径调试测试 |

## pytest 标记

项目使用以下 pytest 标记：

| 标记 | 说明 |
|------|------|
| `@pytest.mark.integration` | 集成测试，需要数据库环境 |
| `@pytest.mark.cloud` | 云函数测试，需要网络连接 |
| `@pytest.mark.api` | API 测试，需要外部服务 |
| `@pytest.mark.skip` | 跳过测试 |

## 测试示例

### 单元测试示例

```python
import pytest
from unittest.mock import Mock, patch

def test_search_cards_success(self, mock_session):
    """测试搜索卡牌成功"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"items": [...]}
    mock_session.get.return_value = mock_response

    client = MTGCHAPIClient()
    result = client.search_cards("闪电风暴")

    assert "items" in result
    assert len(result["items"]) > 0
```

### 参数化测试

```python
@pytest.mark.parametrize("rarity,expected", [
    ("C", "普通"),
    ("U", "非普通"),
    ("R", "稀有"),
    ("M", "秘稀"),
])
def test_format_card_info_rarity_mapping(self, rarity, expected):
    """测试稀有度映射"""
    card = {"name": "Test", "rarity": rarity}
    result = format_card_info(card)
    assert expected in result
```

## 测试最佳实践

1. **独立性**: 每个测试应该独立运行，不依赖其他测试
2. **可重复性**: 单元测试使用 mock，不依赖外部服务
3. **明确性**: 测试名称应该清晰描述测试内容
4. **快速性**: 单元测试应该快速执行

## 当前测试状态

| 文件 | 状态 | 说明 |
|------|------|------|
| `test_mtgch_api.py` | ✅ 通过 | 27 个测试全部通过 |
| `test_openclaw_client.py` | ✅ 通过 | 28 个测试全部通过 |
| `test_agent_pool_manager.py` | ✅ 通过 | 23 个测试全部通过 |
| `test_routes.py` | ⚠️ 阻塞 | starlette 0.27.0 与 httpx 0.28.1 不兼容，需要环境修复 |

**总测试数**: 78 个通过，24 个待修复

## 相关文档

- [项目 README](../README.md)
- [MTGCH API 文档](../docs/MTGCH%20API快速开始.md)
- [CloudBase 部署指南](../docs/CloudBase部署指南.md)

---

**最后更新**: 2026-03-16
**测试框架**: pytest
