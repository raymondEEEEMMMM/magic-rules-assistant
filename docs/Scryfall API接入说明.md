# Scryfall API 接入说明

## 概述

Scryfall API（https://api.scryfall.com）是一个完整的万智牌数据 API，提供卡牌搜索、图片、裁定等信息。目前项目中已集成用于：
1. 系列卡牌查询（获取卡图）
2. 卡牌官方裁定查询

## API 文档

官方文档: https://scryfall.com/docs/api

## 已实现的功能

### 1. 系列卡牌查询 API

**端点**: `GET /api/scryfall/set/{set_code}/cards/`

**参数**:
- `page` (可选): 页码，默认1

**说明**:
- 调用 Scryfall `/cards/search?q=set:{set_code}` 获取系列卡牌
- Scryfall 支持分页，每页返回 175 张卡
- 后端会自动循环获取所有页面

**示例**:
```
GET /api/scryfall/set/mkm/cards/
GET /api/scryfall/set/sld/cards/
```

### 2. 卡牌裁定查询

**前端直接调用**（小程序中）:
```javascript
// miniprogram/utils/api.js
api.getCardRulings(cardId) {
  return new Promise((resolve, reject) => {
    wx.request({
      url: `https://api.scryfall.com/cards/${cardId}/rulings`,
      success: res => {
        const rulings = res.data?.data || []
        resolve(rulings)
      },
      fail: () => resolve([])
    })
  })
}
```

## Secret Lair 查询

### Secret Lair 基本信息

| 属性 | 值 |
|------|-----|
| Set Code | `sld` |
| Set Name | `Secret Lair Drop` |
| Set Type | `box` |
| 卡牌总数 | ~1600 张 |
| 发布日期 | 2019-12-02 起 |

### 查询 Secret Lair 卡牌

```bash
curl "https://api.scryfall.com/cards/search?q=set:sld&page=1"
```

返回字段：
- `id`: 卡牌 UUID
- `name`: 卡牌名称
- `released_at`: 发布日期
- `image_uris`: 图片 URL（small, normal, large, png, art_crop, border_crop）
- `colors`: 颜色数组
- `cmc`: 转换费用
- `type_line`: 类型行
- `rarity`: 稀有度（common, uncommon, rare, mythic）
- `mana_cost`: 法力费用
- `oracle_text`: 规则文本
- `promo_types`: 促销类型数组

### Secret Lair 数据特点

1. **无 collector_number**: Secret Lair 卡牌没有传统的收集编号
2. **同一卡牌多发布时间**: 同一张卡可能在不同 Drop 中发布
3. **图片 URL 有效期**: Scryfall 图片 URL 包含版本参数 `?1706389555`，建议定期刷新

## Python SDK 使用

### 基本用法

```python
from backend.services.mtgch_api import MTGCHAPIClient

# 创建客户端
client = MTGCHAPIClient()

# 查询系列卡牌（通过 Scryfall）
result = client.search_cards_by_set("sld", page=1)

# 获取所有 Secret Lair 卡牌
all_cards = []
page = 1
while True:
    result = client.search_cards_by_set("sld", page=page)
    cards = result.get('data', [])
    all_cards.extend(cards)
    if not result.get('has_more'):
        break
    page += 1

print(f"Total Secret Lair cards: {len(all_cards)}")

client.close()
```

## Mana Symbol 查询

Scryfall 提供官方法力符号图片：

### 查询所有法力符号

```bash
curl "https://api.scryfall.com/symbology"
```

返回结构：
```json
{
  "object": "list",
  "data": [
    {
      "symbol": "{W}",
      "svg_uri": "https://svgs.scryfall.io/card-symbols/W.svg",
      "mana_cost": "W",
      "cmc": 1.0,
      "colors": ["W"],
      "type": "modal_dfc",
      "hyphenated": "W"
    },
    ...
  ]
}
```

### 常用法力符号 URL

| 符号 | URL |
|------|-----|
| W | `https://svgs.scryfall.io/card-symbols/W.svg` |
| U | `https://svgs.scryfall.io/card-symbols/U.svg` |
| B | `https://svgs.scryfall.io/card-symbols/B.svg` |
| R | `https://svgs.scryfall.io/card-symbols/R.svg` |
| G | `https://svgs.scryfall.io/card-symbols/G.svg` |
| 0 | `https://svgs.scryfall.io/card-symbols/0.svg` |
| 1-20 | `https://svgs.scryfall.io/card-symbols/{N}.svg` |
| X | `https://svgs.scryfall.io/card-symbols/X.svg` |
| PHYREXIAN | `https://svgs.scryfall.io/card-symbols/P.svg` |

### 前端使用示例

```javascript
// 将法力费用转换为图片数组
getManaSymbols(manaCost) {
  if (!manaCost) return []
  const symbols = manaCost.match(/\{([^}]+)\}/g) || []
  return symbols.map(s => {
    const symbol = s.replace(/[{}]/g, '')
    return {
      url: `https://svgs.scryfall.io/card-symbols/${symbol}.svg`,
      key: symbol
    }
  })
}
```

## 常用 Scryfall API Endpoints

### 卡牌相关

| Endpoint | 说明 |
|----------|------|
| `/cards/search?q=set:{code}` | 搜索某系列的卡牌 |
| `/cards/{id}` | 获取单张卡牌详情 |
| `/cards/{id}/rulings` | 获取卡牌官方裁定 |
| `/cards/{id}/images` | 获取卡牌多张图片 |

### 系列相关

| Endpoint | 说明 |
|----------|------|
| `/sets` | 获取所有系列列表 |
| `/sets/{code}` | 获取某系列详情 |
| `/sets/search?q={query}` | 搜索系列 |

### 其他

| Endpoint | 说明 |
|----------|------|
| `/symbology` | 获取所有法力符号 |
| `/catalog/card-names` | 获取所有卡牌名称 |
| `/catalog/word-bank` | 获取常用词库 |

## API 限制

- **速率限制**: 每秒最多 10 次请求
- **分页**: 默认每页 175 条数据
- **无需认证**: Scryfall API 是公开的

## 返回字段说明

### 卡牌对象 (Card Object)

```json
{
  "id": "bd6e71a1-713e-4eca-bd65-9f0638c16794",
  "name": "Absolving Lammasu",
  "lang": "en",
  "released_at": "2024-02-02",
  "uri": "https://api.scryfall.com/cards/bd6e71a1-713e-4eca-bd65-9f0638c16794",
  "image_uris": {
    "small": "https://cards.scryfall.io/small/front/...",
    "normal": "https://cards.scryfall.io/normal/front/...",
    "large": "https://cards.scryfall.io/large/front/...",
    "png": "https://cards.scryfall.io/png/front/...",
    "art_crop": "https://cards.scryfall.io/art_crop/front/...",
    "border_crop": "https://cards.scryfall.io/border_crop/front/..."
  },
  "mana_cost": "{3}{W}",
  "cmc": 4.0,
  "colors": ["W"],
  "type_line": "Creature — Lammasu",
  "oracle_text": "Flying\nLifelink",
  "power": "3",
  "toughness": "3",
  "rarity": "uncommon",
  "set": "mkm",
  "set_name": "Murders at Karlov Manor",
  "collector_number": "2",
  "artist": "Johnidon"
}
```

### 系列对象 (Set Object)

```json
{
  "id": "7ead17a9-05c5-42a4-89c2-2359b3c3a8f6",
  "name": "Murders at Karlov Manor",
  "code": "mkm",
  "set_type": "expansion",
  "released_at": "2024-02-02",
  "card_count": 291,
  "icon_svg_uri": "https://svgs.scryfall.io/sets/mkm.svg"
}
```

## 相关文件

- `/functions/mtgAsk/backend/services/mtgch_api.py` - 包含 `search_cards_by_set()` 方法
- `/functions/mtgAsk/index.py` - 包含 `/api/scryfall/set/{code}/cards/` 路由
- `/miniprogram/utils/api.js` - 包含 `getCardRulings()` 方法

## 注意事项

1. **图片 URL 有效期**: Scryfall 图片 URL 包含缓存刷新参数，建议在展示时处理图片加载失败的情况
2. **速率限制**: 避免短时间内大量请求
3. **分页处理**: 部分接口需要循环请求才能获取全部数据
4. **Secret Lair 特殊性**: Secret Lair 卡牌使用 `set:sld`，但每张卡有自己的发布日期
