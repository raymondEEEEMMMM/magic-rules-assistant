# mtgAsk - API 文档

> 为小程序开发者提供的完整 API 接口文档

## 基础信息

- **API 基础地址**: `https://magic-rules-assistant-0a1904c329-1410769303.ap-shanghai.app.tcloudbase.com/`
- **请求方式**: `GET` / `POST`
- **响应格式**: `JSON`
- **字符编码**: `UTF-8`

## ⚠️ 数据限制说明

> **重要**: 后端当前**只支持英文规则查询**，**支持中文卡牌查询**（通过 MTGCH API）。

| 功能 | 当前支持语言 | 说明 |
|------|-------------|------|
| 关键词查询 | 英文 | 如 `Flying`, `Trample` |
| 规则搜索 | 英文 | 规则数据库为英文 |
| 卡牌搜索 | 中文/英文 | 通过 MTGCH API |

## API 端点列表

| 端点 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 服务状态 |
| `/wechat/api/search` | GET | 规则搜索（仅英文） |
| `/wechat/api/keyword` | GET | 关键词查询（仅英文） |
| `/wechat/api/mtgch/search` | GET | MTGCH 卡牌搜索（支持中文） |
| `/wechat/api/mtgch/card` | GET | MTGCH 单张卡牌详情 |
| `/wechat/api/mtgch/autocomplete` | GET | MTGCH 自动补全 |

---

## 1. 服务状态

### 接口
```
GET /
```

### 请求示例
```javascript
wx.request({
  url: 'https://magic-rules-assistant-0a1904c329-1410769303.ap-shanghai.app.tcloudbase.com/',
  method: 'GET'
})
```

### 响应示例
```json
{
  "message": "mtgAsk 服务运行中",
  "status": "ok",
  "service": "CloudBase HTTP Function",
  "path": "/",
  "query_params": {}
}
```

---

## 2. 规则搜索

### 接口
```
GET /wechat/api/search?q={keyword}
```

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| q | string | 是 | 搜索关键词 |

### 请求示例
```javascript
wx.request({
  url: 'https://magic-rules-assistant-0a1904c329-1410769303.ap-shanghai.app.tcloudbase.com/wechat/api/search',
  data: {
    q: 'combat'
  },
  method: 'GET',
  success(res) {
    console.log(res.data)
  }
})
```

### 响应示例
```json
{
  "query": "combat",
  "count": 3,
  "results": {
    "query": "combat",
    "rules": [
      {
        "rule_number": "506.",
        "rule_title": "",
        "rule_content": "Combat Phase",
        "category": null
      },
      {
        "rule_number": "507.",
        "rule_title": "",
        "rule_content": "Beginning of Combat Step",
        "category": null
      },
      {
        "rule_number": "510.",
        "rule_title": "",
        "rule_content": "Combat Damage Step",
        "category": null
      }
    ],
    "keyword_abilities": [],
    "cards": [],
    "qa_templates": []
  }
}
```

### 小程序使用示例
```javascript
// 搜索规则
function searchRules(keyword) {
  wx.showLoading({ title: '搜索中...' })
  
  wx.request({
    url: 'https://magic-rules-assistant-0a1904c329-1410769303.ap-shanghai.app.tcloudbase.com/wechat/api/search',
    data: { q: keyword },
    method: 'GET',
    success(res) {
      wx.hideLoading()
      const { results } = res.data
      const rules = results.rules || []
      
      if (rules.length > 0) {
        console.log('找到规则:', rules)
        // 显示结果
      } else {
        wx.showToast({ title: '未找到相关规则', icon: 'none' })
      }
    },
    fail(err) {
      wx.hideLoading()
      wx.showToast({ title: '请求失败', icon: 'none' })
    }
  })
}

// 使用
searchRules('combat')
```

---

## 3. 关键词查询

### 接口
```
GET /wechat/api/keyword?k={keyword}
```

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| k | string | 是 | 关键词名称（如 Flying, Reach, Deathtouch） |

### 请求示例
```javascript
wx.request({
  url: 'https://magic-rules-assistant-0a1904c329-1410769303.ap-shanghai.app.tcloudbase.com/wechat/api/keyword',
  data: {
    k: 'Flying'
  },
  method: 'GET',
  success(res) {
    console.log(res.data)
  }
})
```

### 响应示例
```json
{
  "keyword": "Flying",
  "result": {
    "keyword_name": "Flying",
    "description": "702.",
    "full_text": "702.9a Flying is an evasion ability."
  }
}
```

### 小程序使用示例
```javascript
// 查询关键词
function getKeyword(keyword) {
  wx.showLoading({ title: '查询中...' })
  
  wx.request({
    url: 'https://magic-rules-assistant-0a1904c329-1410769303.ap-shanghai.app.tcloudbase.com/wechat/api/keyword',
    data: { k: keyword },
    method: 'GET',
    success(res) {
      wx.hideLoading()
      const { result } = res.data
      
      if (result) {
        console.log('关键词详情:', result)
        // 显示结果
        wx.showModal({
          title: result.keyword_name,
          content: result.full_text
        })
      } else {
        wx.showToast({ title: '未找到该关键词', icon: 'none' })
      }
    },
    fail(err) {
      wx.hideLoading()
      wx.showToast({ title: '请求失败', icon: 'none' })
    }
  })
}

// 使用
getKeyword('Flying')
```

### 常见关键词列表
- **飞行类**: Flying, Reach
- **战斗类**: First Strike, Double Strike, Trample, Menace, Deathtouch
- **防御类**: Defender, Indestructible, Ward
- **进攻类**: Haste, Vigilance, Rush
- **操控类**: Tap, Untap, Flash
- **其他**: Hexproof, Shroud, Protection, Evoke

---

## 4. MTGCH 卡牌搜索

### 接口
```
GET /wechat/api/mtgch/search?q={card_name}&page={page}&page_size={page_size}
```

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| q | string | 是 | 卡牌名称 |
| page | number | 否 | 页码（默认 1） |
| page_size | number | 否 | 每页数量（默认 5） |

### 请求示例
```javascript
wx.request({
  url: 'https://magic-rules-assistant-0a1904c329-1410769303.ap-shanghai.app.tcloudbase.com/wechat/api/mtgch/search',
  data: {
    q: 'Lightning Bolt',
    page: 1,
    page_size: 5
  },
  method: 'GET',
  success(res) {
    console.log(res.data)
  }
})
```

### 响应示例
```json
{
  "total": 1,
  "page": 1,
  "page_size": 5,
  "items": [
    {
      "id": "uuid",
      "name": "Lightning Bolt",
      "type": "Instant",
      "mana_cost": "{R}",
      "oracle_text": "Lightning Bolt deals 3 damage to any target.",
      "set_name": "Core Set 2019",
      "collector_number": "149"
    }
  ]
}
```

### 小程序使用示例
```javascript
// 搜索卡牌
function searchCard(cardName, page = 1) {
  wx.showLoading({ title: '搜索中...' })
  
  wx.request({
    url: 'https://magic-rules-assistant-0a1904c329-1410769303.ap-shanghai.app.tcloudbase.com/wechat/api/mtgch/search',
    data: { 
      q: cardName,
      page,
      page_size: 5
    },
    method: 'GET',
    success(res) {
      wx.hideLoading()
      const { items, total } = res.data
      
      if (items && items.length > 0) {
        console.log('找到卡牌:', items)
        // 显示结果列表
      } else {
        wx.showToast({ title: '未找到该卡牌', icon: 'none' })
      }
    },
    fail(err) {
      wx.hideLoading()
      wx.showToast({ title: '请求失败', icon: 'none' })
    }
  })
}

// 使用
searchCard('Lightning Bolt')
```

---

## 错误处理

### 错误响应格式
```json
{
  "error": "错误描述信息"
}
```

### 常见错误码

| 错误 | 说明 | 解决方案 |
|------|------|----------|
| 网络错误 | 请求超时或网络连接失败 | 检查网络连接，重试请求 |
| 400 Bad Request | 缺少必需参数 | 检查请求参数是否完整 |
| 404 Not Found | 未找到数据 | 尝试其他搜索关键词 |
| 500 Server Error | 服务器内部错误 | 稍后重试或联系管理员 |

### 小程序错误处理示例
```javascript
wx.request({
  url: 'https://magic-rules-assistant-0a1904c329-1410769303.ap-shanghai.app.tcloudbase.com/wechat/api/search',
  data: { q: keyword },
  method: 'GET',
  success(res) {
    if (res.data.error) {
      // 业务错误
      wx.showToast({ 
        title: res.data.error,
        icon: 'none'
      })
    } else {
      // 成功处理
      handleSuccess(res.data)
    }
  },
  fail(err) {
    // 网络错误
    console.error('请求失败:', err)
    wx.showModal({
      title: '网络错误',
      content: '请检查网络连接后重试',
      showCancel: false
    })
  }
})
```

---

## 最佳实践

### 1. 请求节流
避免频繁请求，建议添加防抖：

```javascript
let timer = null

function debouncedSearch(keyword) {
  clearTimeout(timer)
  timer = setTimeout(() => {
    searchRules(keyword)
  }, 300)
}
```

### 2. 缓存策略
使用小程序缓存减少重复请求：

```javascript
// 缓存搜索结果
function searchWithCache(keyword) {
  const cacheKey = `search_${keyword}`
  const cached = wx.getStorageSync(cacheKey)
  
  if (cached && Date.now() - cached.time < 300000) {
    return Promise.resolve(cached.data)
  }
  
  return new Promise((resolve) => {
    wx.request({
      url: API_URL + '/wechat/api/search',
      data: { q: keyword },
      success(res) {
        wx.setStorageSync(cacheKey, {
          data: res.data,
          time: Date.now()
        })
        resolve(res.data)
      }
    })
  })
}
```

### 3. 加载状态
始终显示加载状态，提升用户体验：

```javascript
function apiRequest(options) {
  wx.showLoading({ title: '加载中...' })
  
  return new Promise((resolve, reject) => {
    wx.request({
      ...options,
      success: (res) => {
        wx.hideLoading()
        resolve(res.data)
      },
      fail: (err) => {
        wx.hideLoading()
        reject(err)
      }
    })
  })
}

// 使用
apiRequest({
  url: API_URL + '/wechat/api/search',
  data: { q: 'combat' }
}).then(data => {
  console.log(data)
})
```

---

## 完整示例

### Page 完整代码
```javascript
// pages/index/index.js
const API_BASE = 'https://magic-rules-assistant-0a1904c329-1410769303.ap-shanghai.app.tcloudbase.com'

Page({
  data: {
    keyword: '',
    results: [],
    loading: false
  },

  // 搜索规则
  handleSearch() {
    const { keyword } = this.data
    if (!keyword) {
      wx.showToast({ title: '请输入关键词', icon: 'none' })
      return
    }
    
    this.setData({ loading: true })
    
    wx.request({
      url: `${API_BASE}/wechat/api/search`,
      data: { q: keyword },
      method: 'GET',
      success: (res) => {
        const { results } = res.data
        const rules = results.rules || []
        this.setData({ results: rules })
      },
      fail: (err) => {
        console.error(err)
        wx.showToast({ title: '请求失败', icon: 'none' })
      },
      complete: () => {
        this.setData({ loading: false })
      }
    })
  },

  // 查询关键词
  handleKeyword() {
    const { keyword } = this.data
    if (!keyword) return
    
    wx.request({
      url: `${API_BASE}/wechat/api/keyword`,
      data: { k: keyword },
      method: 'GET',
      success: (res) => {
        const { result } = res.data
        if (result) {
          wx.showModal({
            title: result.keyword_name,
            content: result.full_text
          })
        } else {
          wx.showToast({ title: '未找到该关键词', icon: 'none' })
        }
      }
    })
  },

  // 搜索卡牌
  handleCardSearch() {
    const { keyword } = this.data
    if (!keyword) return
    
    wx.request({
      url: `${API_BASE}/wechat/api/mtgch/search`,
      data: { q: keyword },
      method: 'GET',
      success: (res) => {
        const { items } = res.data
        if (items && items.length > 0) {
          console.log('卡牌:', items)
          // 导航到卡牌详情页
          wx.navigateTo({
            url: `/pages/card/card?data=${JSON.stringify(items[0])}`
          })
        } else {
          wx.showToast({ title: '未找到该卡牌', icon: 'none' })
        }
      }
    })
  }
})
```

---

## 5. 单张卡牌详情

### 接口
```
GET /wechat/api/mtgch/card?id={card_id}
GET /wechat/api/mtgch/card?set={set_code}&number={collector_number}
```

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string | 否 | 卡牌 UUID（与 set+number 二选一） |
| set | string | 否 | 系列代码（如 M19） |
| number | string | 否 | 收集编号 |

### 请求示例
```javascript
// 通过 UUID 查询
wx.request({
  url: 'https://magic-rules-assistant-0a1904c329-1410769303.ap-shanghai.app.tcloudbase.com/wechat/api/mtgch/card',
  data: { id: 'card-uuid' },
  method: 'GET'
})

// 通过系列代码+编号查询
wx.request({
  url: 'https://magic-rules-assistant-0a1904c329-1410769303.ap-shanghai.app.tcloudbase.com/wechat/api/mtgch/card',
  data: { set: 'M19', number: '149' },
  method: 'GET'
})
```

### 响应示例
```json
{
  "id": "uuid",
  "name": "Lightning Bolt",
  "type": "Instant",
  "mana_cost": "{R}",
  "oracle_text": "Lightning Bolt deals 3 damage to any target.",
  "set_name": "Core Set 2019",
  "collector_number": "149",
  "rarity": "common",
  "image_uris": {
    "normal": "https://..."
  }
}
```

---

## 6. 自动补全

### 接口
```
GET /wechat/api/mtgch/autocomplete?q={query}&size={size}
```

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| q | string | 是 | 搜索前缀 |
| size | number | 否 | 返回数量（默认 10） |
| is_for_deck | boolean | 否 | 是否用于套牌构建（默认 false） |

### 请求示例
```javascript
wx.request({
  url: 'https://magic-rules-assistant-0a1904c329-1410769303.ap-shanghai.app.tcloudbase.com/wechat/api/mtgch/autocomplete',
  data: { q: 'light', size: 5 },
  method: 'GET',
  success(res) {
    console.log(res.data)
  }
})
```

### 响应示例
```json
{
  "suggestions": [
    "Lightning Bolt",
    "Lightning Strike",
    "Light of Promise",
    "Lightning Greaves",
    "Light-Paws, Emperor's Voice"
  ]
}
```

### 小程序使用示例
```javascript
// 搜索框自动补全
function autocomplete(query) {
  return new Promise((resolve) => {
    wx.request({
      url: `${API_BASE}/wechat/api/mtgch/autocomplete`,
      data: { q: query, size: 10 },
      method: 'GET',
      success(res) {
        const suggestions = res.data.suggestions || []
        resolve(suggestions)
      },
      fail() {
        resolve([])
      }
    })
  })
}

// 使用（带防抖）
let timer = null
function onInput(e) {
  const value = e.detail.value
  clearTimeout(timer)
  timer = setTimeout(() => {
    autocomplete(value).then(suggestions => {
      this.setData({ suggestions })
    })
  }, 300)
}
```

---

## 技术支持

如有问题，请联系开发团队或查看项目文档：
- 项目文档: `/docs`
- 部署指南: `/docs/云端API部署完整指南.md`
- MTGCH API: `/docs/MTGCH API接入说明.md`

---

## 更新日志

| 日期 | 版本 | 更新内容 |
|------|------|----------|
| 2026-03-14 | 1.0 | 初始版本，提供规则搜索、关键词查询、卡牌搜索 API |
| 2026-03-14 | 1.1 | 补充 MTGCH 单张卡牌详情、自动补全接口 |
