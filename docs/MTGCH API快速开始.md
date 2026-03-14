# MTGCH API 快速开始指南

## 1分钟快速上手

### 1. 直接使用HTTP API

```bash
# 查询中文牌
curl "https://your-function-url/api/mtgch/search?q=闪电风暴&page_size=3&priority_chinese=true"

# 查询英文牌
curl "https://your-function-url/api/mtgch/search?q=Lightning Storm&page_size=3&priority_chinese=false"

# 获取随机卡牌
curl "https://your-function-url/api/mtgch/random"

# 中文自动补全
curl "https://your-function-url/api/mtgch/autocomplete?q=闪电&size=5"

# 英文自动补全
curl "https://your-function-url/api/mtgch/autocomplete?q=Lightning&size=5"
```

### 2. 在代码中使用

```python
from backend.services.mtgch_api import MTGCHAPIClient

# 创建客户端
client = MTGCHAPIClient()

# 查询中文牌
result = client.search_cards("闪电风暴", page_size=5, priority_chinese=True)
for card in result.get("items", []):
    print(card["name"])

# 查询英文牌
result = client.search_cards("Lightning Storm", page_size=5, priority_chinese=False)
for card in result.get("items", []):
    print(card["name"])

# 获取随机卡牌
card = client.get_random_card()
print(card["name"])

# 自动补全
result = client.autocomplete("闪电", size=10)

client.close()
```

### 3. 微信机器人使用

直接在微信公众号中发送：

**中文牌查询**:
- 查询中文牌：`卡牌:闪电风暴`（返回中文版）
- 查询中文牌：`卡牌:黑莲花`（返回中文版）

**英文牌查询**:
- 查询英文牌：`卡牌:Lightning Storm`（返回英文版）
- 查询英文牌：`卡牌:Black Lotus`（返回英文版）

**其他查询**:
- 搜索规则：`飞行生物`
- 关键词查询：`瞬息`

## 主要功能

### 🔍 查询中文牌
- 使用中文名搜索
- 优先返回中文版本
- 支持分页
- 适合查询已汉化卡牌

### 🔍 查询英文牌
- 使用英文名搜索
- 返回英文版本
- 支持分页
- 适合查询未汉化或英文卡牌

### 🎲 随机卡牌
- 随机获取一张卡牌
- 适合每日推荐

### 💡 自动补全
- 快速输入建议
- 支持卡组构建模式

## API端点总览

| 端点 | 功能 | 参数 | 说明 |
|------|------|------|------|
| `/api/mtgch/search` | 搜索卡牌 | q, page, page_size, priority_chinese | 设置priority_chinese控制语言 |
| `/api/mtgch/card` | 单张卡牌 | id 或 set+number | 根据ID查询，不区分语言 |
| `/api/mtgch/random` | 随机卡牌 | - | 随机返回中英文卡牌 |
| `/api/mtgch/autocomplete` | 自动补全 | q, size, is_for_deck | 根据搜索词自动补全 |

## 示例响应

### 搜索响应
```json
{
  "items": [
    {
      "name": "Lightning Storm",
      "name_en": "Lightning Storm",
      "mana_cost": "{1}{R}{R}",
      "type_line": "Instant",
      "oracle_text": "Lightning Storm deals X damage...",
      "set_code": "USG",
      "collector_number": "89"
    }
  ],
  "total": 1,
  "page": 1
}
```

## 常见问题

### Q: 如何查询中文牌？
A: 使用中文名搜索，并设置 `priority_chinese=true`
```bash
GET /api/mtgch/search?q=闪电风暴&priority_chinese=true
```

### Q: 如何查询英文牌？
A: 使用英文名搜索，并设置 `priority_chinese=false`
```bash
GET /api/mtgch/search?q=Lightning Storm&priority_chinese=false
```

### Q: 如何限制搜索结果？
A: 使用 `page_size` 参数，最大100

### Q: 支持哪些查询语法？
A: 支持简单的关键词搜索，也支持结构化查询如 `t:creature c:red`

### Q: API有调用限制吗？
A: 请参考MTGCH官方文档，建议合理控制请求频率

### Q: 微信中如何区分中文牌和英文牌查询？
A: 直接使用卡牌名称即可，系统会根据语言自动识别：
- 中文牌：`卡牌:闪电风暴` → 返回中文版
- 英文牌：`卡牌:Lightning Storm` → 返回英文版

## 更多信息

- 完整文档: `/docs/MTGCH API接入说明.md`
- 官方文档: https://mtgch.com/api/v1/docs
- 测试脚本: `python test_mtgch_api.py`
