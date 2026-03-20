# API 快速参考

## ⚠️ 重要更新

> 后端当前**只支持英文规则查询**，**支持中文卡牌查询**（通过 MTGCH API）。

## 基础配置

```javascript
// API 基础地址
const API_BASE = 'https://magic-rules-assistant-0a1904c329.service.tcloudbase.com'
```

## 快速示例

### 1. 搜索规则
```javascript
wx.request({
  url: `${API_BASE}/wechat/api/search`,
  data: { q: 'combat' },
  success(res) {
    const rules = res.data.results.rules || []
    console.log('找到', rules.length, '条规则')
  }
})
```

### 2. 查询关键词
```javascript
wx.request({
  url: `${API_BASE}/wechat/api/keyword`,
  data: { k: 'Flying' },
  success(res) {
    const result = res.data.result
    console.log(result.keyword_name, result.full_text)
  }
})
```

### 3. 搜索卡牌
```javascript
wx.request({
  url: `${API_BASE}/wechat/api/mtgch/search`,
  data: { q: 'Lightning Bolt' },
  method: 'GET',
  success(res) {
    const cards = res.data.items || []
    console.log('找到', cards.length, '张卡牌')
  }
})
```

### 4. 获取单张卡牌详情
```javascript
wx.request({
  url: `${API_BASE}/wechat/api/mtgch/card`,
  data: { id: 'card-uuid' },
  method: 'GET',
  success(res) {
    console.log('卡牌详情:', res.data)
  }
})
```

### 5. 自动补全
```javascript
wx.request({
  url: `${API_BASE}/wechat/api/mtgch/autocomplete`,
  data: { q: 'light', size: 5 },
  method: 'GET',
  success(res) {
    const suggestions = res.data.suggestions || []
    console.log('补全建议:', suggestions)
  }
})
```

### 6. AI 裁判问答
```javascript
wx.request({
  url: `${API_BASE}/api/ai-judge/chat`,
  method: 'POST',
  header: {
    'Content-Type': 'application/json'
  },
  data: {
    message: '闪电击的伤害何时结算？',
    session_id: 'miniprogram'
  },
  success(res) {
    if (res.data.success) {
      console.log('AI 回答:', res.data.reply)
    }
  }
})
```

## 完整封装

```javascript
// utils/api.js
const API_BASE = 'https://magic-rules-assistant-0a1904c329.service.tcloudbase.com'

const api = {
  // 搜索规则
  searchRules(keyword) {
    return this.request('/wechat/api/search', { q: keyword })
  },

  // 查询关键词
  getKeyword(keyword) {
    return this.request('/wechat/api/keyword', { k: keyword })
  },

  // 搜索卡牌
  searchCard(cardName, page = 1, pageSize = 5) {
    return this.request('/wechat/api/mtgch/search', {
      q: cardName,
      page,
      page_size: pageSize
    })
  },

  // 获取单张卡牌详情
  getCardById(cardId) {
    return this.request('/wechat/api/mtgch/card', { id: cardId })
  },

  // 自动补全
  autocomplete(query, size = 10) {
    return this.request('/wechat/api/mtgch/autocomplete', { q: query, size })
  },

  // 通用请求方法
  request(url, data = {}) {
    return new Promise((resolve, reject) => {
      wx.showLoading({ title: '加载中...' })

      wx.request({
        url: API_BASE + url,
        data,
        method: 'GET',
        success(res) {
          wx.hideLoading()
          if (res.data.error) {
            reject(res.data.error)
          } else {
            resolve(res.data)
          }
        },
        fail(err) {
          wx.hideLoading()
          reject('网络请求失败')
        }
      })
    })
  }
}

module.exports = api
```

## 使用封装后的 API

```javascript
// pages/index/index.js
const api = require('../../utils/api.js')

Page({
  handleSearch() {
    api.searchRules('combat')
      .then(data => {
        const rules = data.results.rules || []
        this.setData({ rules })
      })
      .catch(err => {
        wx.showToast({ title: err, icon: 'none' })
      })
  },

  handleKeyword() {
    api.getKeyword('Flying')
      .then(data => {
        wx.showModal({
          title: data.result.keyword_name,
          content: data.result.full_text
        })
      })
      .catch(err => {
        wx.showToast({ title: err, icon: 'none' })
      })
  },

  handleCardSearch() {
    api.searchCard('Lightning Bolt')
      .then(data => {
        const card = data.items[0]
        if (card) {
          this.setData({ card })
        }
      })
      .catch(err => {
        wx.showToast({ title: err, icon: 'none' })
      })
  },

  handleRandomCard() {
    api.getRandomCard()
      .then(data => {
        this.setData({ card: data })
      })
      .catch(err => {
        wx.showToast({ title: err, icon: 'none' })
      })
  },

  handleAutocomplete(e) {
    const value = e.detail.value
    api.autocomplete(value, 5)
      .then(data => {
        this.setData({ suggestions: data.suggestions })
      })
  }
})
```

## 常用关键词

> ⚠️ **注意**: 关键词查询仅支持**英文**，中文为参考翻译。

| 关键词(英文) | 中文 |
|-------------|------|
| Flying | 飞行 |
| Deathtouch | 触死/死触 |
| First Strike | 先攻 |
| Trample | 践踏 |
| Vigilance | 警戒 |
| Flash | 闪现 |
| Menace | 威慑 |
| Evoke | 祭献 |
| Haste | 加速 |
| Lifelink | 系命 |
| etc. | ... |

> 更多关键词请参考完整文档: `/miniprogram/API.md`
