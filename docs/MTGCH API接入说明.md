# MTGCH 汉化 API 接入说明

## 概述

已成功接入 MTGCH 中文万智牌API（https://mtgch.com），提供完整的卡牌查询、搜索和自动补全功能。

## API 文档

官方文档: https://mtgch.com/api/v1/docs

## 已实现的功能

### 1. 卡牌搜索 API

**端点**: `GET /api/mtgch/search`

**参数**:
- `q` (必填): 查询字符串
- `page` (可选): 页码，默认1
- `page_size` (可选): 每页数量，默认5，最大100
- `priority_chinese` (可选): 是否优先中文版本，默认true
- `order` (可选): 排序字段（如 name, -mv, rarity）
- `unique` (可选): 去重方式（scryfall_id, oracle_id, illustration_id）

**查询方式说明**:
- **中文牌查询**: 使用中文名搜索，如 `q=闪电风暴`，设置 `priority_chinese=true`
- **英文牌查询**: 使用英文名搜索，如 `q=Lightning Storm`，设置 `priority_chinese=false`

**示例**:

中文牌查询:
```
GET /api/mtgch/search?q=闪电风暴&page_size=3&priority_chinese=true
```

英文牌查询:
```
GET /api/mtgch/search?q=Lightning Storm&page_size=3&priority_chinese=false
```

### 2. 单张卡牌详情 API

**端点**: `GET /api/mtgch/card`

**参数**（二选一）:
- `id`: 卡牌UUID
- `set` + `number`: 系列代码 + 收集编号

**示例**:
```
GET /api/mtgch/card?id=uuid
GET /api/mtgch/card?set=MKM&number=2
```

### 3. 随机卡牌 API

**端点**: `GET /api/mtgch/random`

**参数**: 无

**示例**:
```
GET /api/mtgch/random
```

### 4. 自动补全 API

**端点**: `GET /api/mtgch/autocomplete`

**参数**:
- `q` (必填): 搜索关键词
- `size` (可选): 返回数量，默认10，最大50
- `is_for_deck` (可选): 是否用于卡组构建，默认false

**示例**:
```
GET /api/mtgch/autocomplete?q=闪电&size=5
```

## 微信集成

在微信中发送消息时，可以使用以下格式查询卡牌：

### 中文牌查询
- **卡牌查询**: `卡牌:闪电风暴`（中文名称）
- 优先返回中文版本的卡牌信息
- 适合查询已汉化的卡牌

### 英文牌查询
- **卡牌查询**: `卡牌:Lightning Storm`（英文名称）
- 返回英文版本的卡牌信息
- 适合查询未汉化或英文卡牌

### 其他查询方式
- **规则搜索**: 输入任意关键词或描述
- **关键词查询**: 输入单个关键词（如"飞行"、"警戒"）

## Python SDK 使用

### 基本用法

```python
from backend.services.mtgch_api import MTGCHAPIClient, format_card_info

# 创建客户端
client = MTGCHAPIClient()

# 查询中文牌
result = client.search_cards("闪电风暴", page_size=5, priority_chinese=True)
if "items" in result:
    for card in result["items"]:
        print(format_card_info(card))

# 查询英文牌
result = client.search_cards("Lightning Storm", page_size=5, priority_chinese=False)
if "items" in result:
    for card in result["items"]:
        print(format_card_info(card))

# 获取单张卡牌
card = client.get_card_by_id("uuid")
if card:
    print(format_card_info(card))

# 随机卡牌
card = client.get_random_card()

# 自动补全（中文）
result = client.autocomplete("闪电", size=10)

# 自动补全（英文）
result = client.autocomplete("Lightning", size=10)

# 获取系列列表
sets = client.get_sets()

# 获取某系列的卡牌
result = client.get_set_cards("MKM", page_size=20)

# 关闭客户端
client.close()
```

### 使用上下文管理器

```python
with MTGCHAPIClient() as client:
    result = client.search_cards("闪电风暴")
    # 自动关闭连接
```

### 格式化卡牌信息

```python
from backend.services.mtgch_api import format_card_info

card_info = {
    "name": "闪电风暴",
    "mana_cost": "{1}{R}{R}",
    "type_line": "Instant",
    "oracle_text": "Lightning Storm deals X damage..."
}

text = format_card_info(card_info)
print(text)
```

输出格式:
```
📛 名称: 闪电风暴
💎 法力费用: {1}{R}{R}
🏷️  类型: Instant
⭐ 稀有度: uncommon
📜 规则文本:
Lightning Storm deals X damage...
📚 系列编号: ? #89
```

## 可用的方法

### MTGCHAPIClient

| 方法 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| `search_cards()` | query, page, page_size, priority_chinese, order, unique | Dict | 搜索卡牌 |
| `get_card_by_id()` | card_id | Optional[Dict] | 通过UUID获取卡牌 |
| `get_card_by_set_and_number()` | set_code, collector_number | Optional[Dict] | 通过系列和编号获取卡牌 |
| `get_card_versions()` | card_id, limit | List[Dict] | 获取卡牌的所有版本 |
| `get_random_card()` | - | Optional[Dict] | 获取随机卡牌 |
| `get_adjacent_card()` | set_code, collector_number, direction | Optional[Dict] | 获取相邻卡牌 |
| `autocomplete()` | query, size, is_for_deck, page | Dict | 自动补全搜索 |
| `get_sets()` | - | List[Dict] | 获取所有系列 |
| `get_set_by_code()` | set_code | Optional[Dict] | 获取系列详情 |
| `get_set_cards()` | set_code, order, unique, priority_chinese, page, page_size | Dict | 获取系列卡牌 |

## 测试

运行测试脚本验证API接入:

```bash
python test_mtgch_api.py
```

## 注意事项

1. **请求超时**: 默认10秒，可在创建客户端时自定义
2. **错误处理**: 所有方法都包含异常处理，返回None或空列表表示失败
3. **分页**: 搜索和系列卡牌接口支持分页
4. **中文优先**: 默认优先返回中文版本的卡牌
5. **会话管理**: 建议使用上下文管理器自动关闭连接

## API 限制

- 搜索: 每页最多100张卡牌
- 自动补全: 最多50条建议
- 版本查询: 最多100个版本

## 错误码

API可能返回以下错误码：
- `400`: 请求参数错误
- `404`: 资源未找到
- `429`: 请求过于频繁
- `500`: 服务器内部错误

## 未来扩展

可以考虑添加的功能：
1. 卡牌收藏功能
2. 卡牌评分和评论
3. 卡组构建建议
4. 价格查询
5. 翻译API（需要认证）

## 相关文件

- `/backend/services/mtgch_api.py`: MTGCH API客户端实现
- `/functions/magic-rules-api/scf_index.py`: 云函数API端点
- `/test_mtgch_api.py`: 测试脚本
