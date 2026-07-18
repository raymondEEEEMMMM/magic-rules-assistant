# mtgAsk Token 页面搜索体验 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 升级 mtgAsk 小程序 token 页面搜索体验，支持中文/英文/拼音首字母/全拼前 3 字符匹配，并加历史记录 + 热门 token 快捷入口 + 搜索语法 hint。

**Architecture:** 单一页面增强 — 在 `miniprogram/pages/token/*` 内扩展：
- 拼音映射表（initial + full）放在 token.js
- 搜索算法升级为 OR 过滤（4 种匹配）
- WXML 新增 3 个区块：建议下拉、历史+热门、语法 hint
- WXSS 新增对应样式
- localStorage 持久化最近 5 个搜索

**Tech Stack:** 微信原生小程序 + 已有的 P5.5 token 页面（紧凑搜索 + 颜色 chips + 卡片化列表）

**依赖 spec:** `docs/superpowers/specs/2026-07-17-token-page-search-experience-design.md`

**前置状态:** P5.5 token 优化已上线（commit `7993762`），本计划基于其继续增强

---

## 文件结构

**修改：**
- `miniprogram/pages/token/token.wxml` — 新增 hint / suggestions / history+hot 区块
- `miniprogram/pages/token/token.wxss` — 新增样式
- `miniprogram/pages/token/token.js` — 新增 pinyinMap / data 字段 / 方法

**无需新建：** 拼音匹配 + 历史持久化都用现有 utils 能力

---

## Task 1: 添加拼音匹配单元测试 + 数据

**Files:**
- Modify: `miniprogram/pages/token/token.js`（在 data 之前添加常量）

- [ ] **Step 1: 在 `miniprogram/pages/token/token.js` 顶部添加拼音映射表（minitest 格式）**

首先在文件顶部（`const cnToEnMap = { ... }` 之后）添加拼音映射表：

```javascript
// 拼音映射：每条 token 包含 initial (首字母) + full (全拼前 3 字符)
const pinyinMap = {
  // 万能 / 无色
  '珍宝':     { initial: 'zb',  full: 'zhen'   },
  '复制品':   { initial: 'fzp', full: 'fuzhi'  },
  '组构体':   { initial: 'zgzt',full: 'zugo'   },
  '衍生':     { initial: 'ys',  full: 'yans'   },
  // 白 (W)
  '士兵':     { initial: 'sb',  full: 'shib'   },
  '天使':     { initial: 'ts',  full: 'tian'   },
  '猫':       { initial: 'm',   full: 'mao'    },
  '狗':       { initial: 'g',   full: 'gou'    },
  '人类':     { initial: 'rl',  full: 'renl'   },
  '僧侣':     { initial: 'sl',  full: 'seng'   },
  '骑士':     { initial: 'qs',  full: 'qish'   },
  '狮鹫':     { initial: 'sy',  full: 'shij'   },
  '精怪':     { initial: 'jg',  full: 'jing'   },
  // 蓝 (U)
  '精灵':     { initial: 'jl',  full: 'jing'   },
  '龙兽':     { initial: 'll',  full: 'long'   },
  '虚影':     { initial: 'xy',  full: 'xuyi'   },
  '维多肯':   { initial: 'wdk', full: 'weid'   },
  '法师':     { initial: 'fs',  full: 'fash'   },
  '螃蟹':     { initial: 'px',  full: 'pang'   },
  '蛇':       { initial: 's',   full: 'she'    },
  '海怪':     { initial: 'hg',  full: 'haig'   },
  // 黑 (B)
  '灵俑':     { initial: 'ly',  full: 'ling'   },
  '鬼怪':     { initial: 'gg',  full: 'guig'   },
  '吸血鬼':   { initial: 'xxg', full: 'xixu'   },
  '蝙蝠':     { initial: 'bf',  full: 'bian'   },
  '骷髅':     { initial: 'kl',  full: 'kul'    },
  '恶魔':     { initial: 'em',  full: 'emo'    },
  '恐惧':     { initial: 'kj',  full: 'kong'   },
  '老鼠':     { initial: 'ls',  full: 'laos'   },
  '阴影':     { initial: 'yy',  full: 'yiny'   },
  '幽灵':     { initial: 'yl',  full: 'youl'   },
  // 红 (R)
  '野狼':     { initial: 'yl',  full: 'yela'   },
  '蜥蜴':     { initial: 'xy',  full: 'xiyi'   },
  '地精':     { initial: 'dj',  full: 'diji'   },
  '元素':     { initial: 'ys',  full: 'yuas'   },
  '龙':       { initial: 'l',   full: 'long'   },
  '巨魔':     { initial: 'jm',  full: 'jumo'   },
  '食人魔':   { initial: 'srm', full: 'shir'   },
  '火焰':     { initial: 'hy',  full: 'huoy'   },
  '半兽人':   { initial: 'brl', full: 'banr'   },
  // 绿 (G)
  '树妖':     { initial: 'sy',  full: 'shuy'   },
  '狼':       { initial: 'l',   full: 'lang'   },
  '昆虫':     { initial: 'kc',  full: 'kunc'   },
  '熊':       { initial: 'x',   full: 'xion'   },
  '象':       { initial: 'x',   full: 'xian'   },
  '蛇颈龙':   { initial: 'sjl', full: 'shej'   },
  '植物':     { initial: 'zw',  full: 'zhiw'   },
  '鹿':       { initial: 'l',   full: 'lu'     },
  '犀牛':     { initial: 'xn',  full: 'xini'   },
  '变形兽':   { initial: 'bx',  full: 'bian'   },
  '藤蔓':     { initial: 'tm',  full: 'tenm'   },
  '甲虫':     { initial: 'jc',  full: 'jiac'   },
  '德鲁伊':   { initial: 'dly', full: 'delu'   }
}
```

- [ ] **Step 2: 提交**

```bash
git add miniprogram/pages/token/token.js
git commit -m "feat(token): 添加 55+ 常用 token 的拼音映射表"
```

---

## Task 2: 添加建议下拉 + hint 区块到 WXML

**Files:**
- Modify: `miniprogram/pages/token/token.wxml`

- [ ] **Step 1: 修改搜索栏 input 添加 `bindfocus` 和 `bindblur`**

将现有的 input 元素替换为：

```xml
<input
  class="search-input"
  placeholder="输入 Token 名称"
  placeholder-class="search-placeholder"
  bindinput="onTokenSearch"
  bindfocus="onSearchFocus"
  bindblur="onSearchBlur"
  bindconfirm="onSearchConfirm"
  value="{{searchQuery}}"
/>
```

- [ ] **Step 2: 在搜索栏和颜色 chips 之间插入 hint 区块**

紧跟在 `</view>` 之后（关闭 `.search-bar`），`<!-- 颜色筛选 chips -->` 之前，插入：

```xml
<text wx:if="{{showHint}}" class="search-hint">支持：中文 / 英文 / 拼音首字母 / 英文首字母</text>
```

- [ ] **Step 3: 在颜色 chips 之前插入建议下拉**

紧跟在 `</scroll-view>` 之后（关闭 `.color-chips`），`<!-- 加载中 -->` 之前，插入：

```xml
<view wx:if="{{showSuggestions && filteredSuggestions.length > 0}}" class="suggestions">
  <view class="suggestion-item"
    wx:for="{{filteredSuggestions}}"
    wx:key="enName"
    bindtap="onSelectSuggestion"
    data-token="{{item}}"
  >
    <view class="suggestion-color color-{{item.color}}"></view>
    <view class="suggestion-icon">{{item.icon}}</view>
    <view class="suggestion-info">
      <text class="suggestion-name">{{item.name}}</text>
      <text class="suggestion-en">{{item.enName}}</text>
    </view>
  </view>
</view>
```

- [ ] **Step 4: 在建议下拉之后，token 列表之前插入历史+热门区块**

紧跟在 `</view>` 之后（关闭 `.suggestions`），`<!-- 默认按颜色分组列表 -->` 之前，插入：

```xml
<view wx:if="{{!searchQuery && !showSearchResults && !showSuggestions}}" class="history-section">
  <view wx:if="{{searchHistory.length > 0}}" class="history-block">
    <text class="block-title">最近搜索</text>
    <view class="history-chips">
      <view class="history-chip" wx:for="{{searchHistory}}" wx:key="*this"
        data-q="{{item}}" bindtap="onHistoryTap">{{item}} ✕</view>
      <view class="history-clear" bindtap="onClearHistory">清空</view>
    </view>
  </view>

  <view class="hot-block">
    <text class="block-title">热门 Token</text>
    <view class="hot-list">
      <view class="hot-chip" wx:for="{{hotTokens}}" wx:key="name"
        data-token="{{item}}" bindtap="onSelectSuggestion">
        <view class="hot-color color-{{item.color}}"></view>
        <text>{{item.icon}} {{item.name}}</text>
      </view>
    </view>
  </view>
</view>
```

- [ ] **Step 5: 提交**

```bash
git add miniprogram/pages/token/token.wxml
git commit -m "feat(token): WXML 新增 hint / suggestions / history+hot 区块"
```

---

## Task 3: 添加新 data 字段 + 方法到 token.js

**Files:**
- Modify: `miniprogram/pages/token/token.js`

- [ ] **Step 1: 在 data 对象里新增字段**

找到 data 块（已含 `searchQuery`, `searchResults`, `tokens` 等），在末尾添加：

```javascript
searchHistory: [],
showSuggestions: false,
filteredSuggestions: [],
showHint: false,
hotTokens: []
```

- [ ] **Step 2: 在 onLoad 末尾添加加载历史和热门**

```javascript
onLoad() {
  this.setData({ isLightTheme: app.globalData.isLightTheme })
  this.fetchTokenList()
  this.loadSearchHistory()
}
```

- [ ] **Step 3: 在文件末尾（最后一个 method 后）添加新方法**

```javascript
// 加载搜索历史（localStorage）
loadSearchHistory() {
  try {
    const history = wx.getStorageSync('tokenSearchHistory') || []
    this.setData({ searchHistory: history })
  } catch (e) {
    console.warn('loadSearchHistory failed', e)
  }
},

// 保存搜索历史（去重 + 最多 5 项 + 移到最前）
saveSearchHistory(query) {
  if (!query) return
  let history = this.data.searchHistory || []
  history = [query, ...history.filter(q => q !== query)].slice(0, 5)
  this.setData({ searchHistory: history })
  try {
    wx.setStorageSync('tokenSearchHistory', history)
  } catch (e) {
    console.warn('saveSearchHistory failed', e)
  }
},

// 清空历史
onClearHistory() {
  this.setData({ searchHistory: [] })
  try {
    wx.removeStorageSync('tokenSearchHistory')
  } catch (e) {
    console.warn('onClearHistory failed', e)
  }
},

// 点击历史项 → 填入搜索框
onHistoryTap(e) {
  const q = e.currentTarget.dataset.q
  if (q) {
    this.setData({ searchQuery: q })
    this.onTokenSearch({ detail: { value: q } })
  }
},

// 搜索框聚焦 → 显示 hint
onSearchFocus() {
  this.setData({ showHint: true })
},

// 搜索框失焦 → 隐藏 hint（但保留建议下拉）
onSearchBlur() {
  this.setData({ showHint: false })
},

// 搜索确认（按回车）
onSearchConfirm(e) {
  const q = (e.detail.value || '').trim()
  if (q) this.saveSearchHistory(q)
  this.setData({ showSuggestions: false, filteredSuggestions: [] })
},

// 选择建议项 → 选中并关闭建议
onSelectSuggestion(e) {
  const token = e.currentTarget.dataset.token
  if (!token) return
  if (this.data.searchQuery) this.saveSearchHistory(this.data.searchQuery)
  this.setData({
    showSuggestions: false,
    filteredSuggestions: [],
    searchQuery: '',
    showHint: false
  })
  // 复用现有 selectToken 逻辑
  this.selectToken({ currentTarget: { dataset: { token } } })
},

// 计算热门 token（取每色一个，最多 6 个）
computeHotTokens() {
  const all = Object.values(this.data.tokenGroups).flatMap(g => g.tokens)
  // 优先取每色第一个 token（珍宝/士兵/精灵/鬼怪/灵俑/复制品）
  const colorOrder = ['C', 'W', 'U', 'B', 'R', 'G']
  const hot = []
  colorOrder.forEach(color => {
    const t = all.find(t => t.color === color)
    if (t) hot.push(t)
  })
  this.setData({ hotTokens: hot.slice(0, 6) })
}
```

- [ ] **Step 4: 在 fetchTokenList 末尾调用 computeHotTokens**

找到 `this.recomputeFilteredGroup()` 之后，添加：

```javascript
this.computeHotTokens()
```

- [ ] **Step 5: 替换 onTokenSearch 升级匹配算法**

找到现有的 `onTokenSearch` 方法（接受 `e` 参数），替换为：

```javascript
onTokenSearch(e) {
  const query = (e.detail.value || '').toLowerCase().trim()
  this.setData({ searchQuery: e.detail.value || '' })

  if (!query) {
    this.setData({ showSuggestions: false, filteredSuggestions: [] })
    return
  }

  const all = Object.values(this.data.tokenGroups).flatMap(g => g.tokens)
  const matches = all.filter(t => {
    // 1. 中文名包含
    if (t.name && t.name.toLowerCase().includes(query)) return true
    // 2. 英文名包含
    if (t.enName && t.enName.toLowerCase().includes(query)) return true
    // 3. 英文首字母
    if (t.enName && t.enName.toLowerCase().startsWith(query)) return true
    // 4. 拼音匹配（首字母 + 全拼前 3 字符）
    const py = pinyinMap[t.name]
    if (py && (py.initial.startsWith(query) || py.full.startsWith(query))) return true
    return false
  })

  this.setData({
    filteredSuggestions: matches.slice(0, 5),
    showSuggestions: matches.length > 0
  })
}
```

- [ ] **Step 6: 在 onTokenSearch 末尾添加保存历史逻辑**

在 `onTokenSearch` 末尾（`this.setData({ filteredSuggestions, ... })` 之后），添加：

```javascript
// 输入即保存历史（去重 + 限制 5 项）
if (matches.length > 0) this.saveSearchHistory(query)
```

- [ ] **Step 7: 提交**

```bash
git add miniprogram/pages/token/token.js
git commit -m "feat(token): 添加 5 种匹配算法 + 历史持久化 + 热门 token"
```

---

## Task 4: 添加新样式到 WXSS

**Files:**
- Modify: `miniprogram/pages/token/token.wxss`

- [ ] **Step 1: 在文件末尾追加新样式**

```css
/* P5.6: 搜索语法提示 */
.search-hint {
  display: block;
  font-size: 22rpx;
  color: var(--text-muted);
  padding: 0 8rpx 16rpx;
}

/* P5.6: 建议下拉 */
.suggestions { display: flex; flex-direction: column; gap: 8rpx; margin-bottom: 16rpx; }
.suggestion-item {
  background: var(--bg-card);
  border-radius: 16rpx;
  box-shadow: var(--shadow-card);
  padding: 16rpx 20rpx;
  display: flex;
  align-items: center;
  gap: 12rpx;
}
.suggestion-item:active { opacity: 0.7; }
.suggestion-color { width: 6rpx; height: 32rpx; border-radius: 3rpx; flex-shrink: 0; }
.suggestion-color.color-W { background: var(--color-white); border: 1rpx solid var(--border-default); }
.suggestion-color.color-U { background: var(--color-blue); }
.suggestion-color.color-B { background: var(--color-black); }
.suggestion-color.color-R { background: var(--color-red); }
.suggestion-color.color-G { background: var(--color-green); }
.suggestion-color.color-C { background: var(--text-muted); }
.suggestion-icon { font-size: 28rpx; flex-shrink: 0; }
.suggestion-info { flex: 1; min-width: 0; }
.suggestion-name { font-size: 26rpx; color: var(--text-primary); display: block; }
.suggestion-en { font-size: 22rpx; color: var(--text-secondary); }

/* P5.6: 历史 + 热门 */
.history-section { margin-bottom: 24rpx; }
.block-title {
  font-size: 26rpx;
  font-weight: 600;
  color: var(--text-secondary);
  display: block;
  margin-bottom: 16rpx;
}
.history-chips { display: flex; flex-wrap: wrap; gap: 12rpx; align-items: center; margin-bottom: 24rpx; }
.history-chip {
  padding: 8rpx 20rpx;
  background: var(--bg-input);
  border-radius: 24rpx;
  font-size: 24rpx;
  color: var(--text-primary);
}
.history-chip:active { opacity: 0.7; }
.history-clear {
  font-size: 24rpx;
  color: var(--text-muted);
  padding: 0 8rpx;
}
.history-clear:active { color: var(--accent-dark); }
.hot-list { display: flex; flex-wrap: wrap; gap: 12rpx; }
.hot-chip {
  display: flex;
  align-items: center;
  gap: 8rpx;
  padding: 8rpx 16rpx;
  background: var(--bg-card);
  border-radius: 20rpx;
  font-size: 24rpx;
  box-shadow: var(--shadow-card);
}
.hot-chip:active { opacity: 0.7; }
.hot-color { width: 12rpx; height: 12rpx; border-radius: 50%; flex-shrink: 0; }
.hot-color.color-W { background: var(--color-white); border: 1rpx solid var(--border-default); }
.hot-color.color-U { background: var(--color-blue); }
.hot-color.color-B { background: var(--color-black); }
.hot-color.color-R { background: var(--color-red); }
.hot-color.color-G { background: var(--color-green); }
.hot-color.color-C { background: var(--text-muted); }
```

- [ ] **Step 2: 提交**

```bash
git add miniprogram/pages/token/token.wxss
git commit -m "feat(token): WXSS 新增 hint / suggestions / history+hot 样式"
```

---

## Task 5: 手动测试 + 修复

**Files:**
- Modify: 可能 `token.wxml` / `token.wxss` / `token.js`

- [ ] **Step 1: 在 WeChat DevTools 中编译**

打开微信开发者工具 → 编译 → 进入 `pages/token/token`

- [ ] **Step 2: 验证默认页（无搜索）**

**期望**：
- 搜索框显示
- 颜色 chips 一行（"全部 8" 等）
- "最近搜索" 区块（首次为空，不显示该区块）
- "热门 Token" 区块显示 6 个 chips（珍宝/士兵/精灵/鬼怪/灵俑/复制品）
- 颜色分组列表

- [ ] **Step 3: 测试拼音匹配 — 输入 "gui"**

**期望**：
- 搜索框下方显示 hint："支持：中文/英文/拼音首字母/英文首字母"
- 建议下拉显示"鬼怪"（full `guig` 匹配）

- [ ] **Step 4: 测试中文匹配 — 输入 "宝"**

**期望**：
- 建议下拉显示"珍宝"（中文包含）

- [ ] **Step 5: 测试英文匹配 — 输入 "tr"**

**期望**：
- 建议下拉显示"复制品"（enName 包含 "tr"... 等等，复制品 enName 是 "Copy"，不匹配 "tr"）
- 实际：没有匹配。改输入 "so" → "Soldier" 士兵
- 期望：建议下拉显示"士兵"（英文包含 "so"）

- [ ] **Step 6: 测试建议点击**

**期望**：
- 点击建议项 → 触发 `onSelectSuggestion` → `selectToken` → 弹出 token 详情弹窗
- 同时清空 searchQuery、关闭 suggestions

- [ ] **Step 7: 测试历史持久化**

**期望**：
- 搜索"珍宝"→ 关闭→ 重新打开页面 → "最近搜索"显示"珍宝"
- 多个搜索后 → "最近搜索"显示最近 5 个，按时间倒序
- 点"清空"→ 历史清空（localStorage 也清空）

- [ ] **Step 8: 测试暗色主题**

切换到暗色主题：
- hint 文字应仍可读
- 建议项背景应是深色（`var(--bg-card)` 暗色版 = #1a1f2e）
- 历史 chips 背景应是深色

- [ ] **Step 9: 修复发现的问题（如果有）**

如有问题，针对性修复。commit：

```bash
git add miniprogram/pages/token/
git commit -m "fix(token): [描述问题]"
```

---

## Task 6: 合并 dev 到 main + 推送

- [ ] **Step 1: 切到 main + 拉**

```bash
git checkout main
git pull origin main
```

- [ ] **Step 2: 合并 dev**

```bash
git merge dev --no-ff -m "merge: token 页面搜索体验优化（5 种匹配 + 历史 + 热门）"
```

- [ ] **Step 3: 推送**

```bash
git push origin main
git push origin dev
```

---

## P5.6 验收清单

- [ ] 默认页显示历史（复访）+ 热门
- [ ] 搜索框聚焦显示语法 hint
- [ ] 中文包含匹配（"宝" → 珍宝）
- [ ] 英文包含匹配（"so" → Soldier 士兵）
- [ ] 英文首字母匹配（"so" → Soldier 士兵）
- [ ] 拼音首字母匹配（"gg" → 鬼怪）
- [ ] 拼音全拼前 3 字符匹配（"gui" → 鬼怪）
- [ ] 建议下拉点击进入 token 详情
- [ ] 搜索成功后写入历史
- [ ] 历史最多 5 项，去重 + 倒序
- [ ] 暗色主题兼容
- [ ] iOS / Android 真机各验证一次

---

## 完成度

P5.6 完成后，token 页面有：
- 紧凑搜索（P5.5）
- 颜色 chips 筛选（P5.5）
- 卡片化 token 列表（P5.5）
- **5 种匹配方式**（P5.6 新增）
- **历史记录 + 热门 token**（P5.6 新增）
- **搜索语法 hint**（P5.6 新增）
- **建议下拉**（P5.6 新增）

完整 P1-P5.6 阶段：20 个页面视觉统一 + 设计系统 + 暗色主题 + 搜索智能化
