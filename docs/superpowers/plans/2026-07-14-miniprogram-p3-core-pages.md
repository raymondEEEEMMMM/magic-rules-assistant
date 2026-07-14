# mtgAsk 小程序前端 P3 核心交互页 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 升级 5 个核心交互页（search / card / rule / keyword / agent）至明亮日间风，并回归暗色主题切换。

**Architecture:**
1. 全局：扩展 tokens 暗色覆盖 + 启用 toggleTheme
2. 搜索：tag-chip tabs + 结果区明亮日间风
3. 详情页（card / rule / keyword）：统一布局（顶图 + 标题 + 标签 + 正文 + 操作）
4. AI 裁判：聊天气泡 + 流式动画 + 消息状态

**Tech Stack:** 微信原生小程序 + P1 设计系统（tokens / 7 组件）+ P2 主页与工具页

**依赖 spec：** `docs/superpowers/specs/2026-07-14-miniprogram-frontend-optimization-design.md` 第 1.4、6.3 节

**P1 + P2 状态：** 已完成（`6d670fc` on main）

---

## 文件结构

**修改**：
- `miniprogram/styles/tokens.wxss` — 完善 `.theme-dark` 覆盖
- `miniprogram/app.js` — 启用 toggleTheme
- `miniprogram/app.wxss` — 添加 `.theme-dark` 选择器
- `miniprogram/pages/search/*` — 搜索结果页视觉升级
- `miniprogram/pages/card/*` — 卡牌详情（已有 promo 流程，保留）
- `miniprogram/pages/rule/*` — 规则详情
- `miniprogram/pages/keyword/*` — 关键词异能
- `miniprogram/pages/agent/*` — AI 裁判（保留所有聊天逻辑）

---

## Task 1: 完善暗色主题 tokens

**Files:**
- Modify: `miniprogram/styles/tokens.wxss`

- [ ] **Step 1: 扩展 .theme-dark 覆盖**

在 `miniprogram/styles/tokens.wxss` 文件末尾，将 `.theme-dark { ... }` 块扩展为完整覆盖（用 Read 工具先读现有内容，再 Edit 替换）。完整内容如下：

```css
/* 暗色主题覆盖（保留兼容旧 .theme-light 类名） */
.theme-dark {
  --bg-page: #0f1419;
  --bg-card: #1a1f2e;
  --bg-input: rgba(255, 255, 255, 0.08);
  --text-primary: #ffffff;
  --text-secondary: rgba(255, 255, 255, 0.7);
  --text-muted: rgba(255, 255, 255, 0.4);
  --text-inverse: #1a1a1a;
  --border-subtle: rgba(255, 255, 255, 0.1);
  --border-default: rgba(255, 255, 255, 0.2);
  --accent-gold: #ffd700;
  --accent-dark: #ffd700;
  --shadow-card: 0 2rpx 12rpx rgba(0, 0, 0, 0.4);
  --shadow-hover: 0 4rpx 20rpx rgba(0, 0, 0, 0.5);
  /* MTG 五色保持不变 */
  --color-white: #f5f5f5;
  --color-blue: #3a7bc8;
  --color-black: #1a1a1a;
  --color-red: #c83a3a;
  --color-green: #3a9b5c;
}

/* 兼容旧 .theme-light 选择器（指向亮色变量） */
.theme-light {
  --bg-page: #faf8f3;
  --bg-card: #ffffff;
  --bg-input: #f5f5f5;
  --text-primary: #1a1a1a;
  --text-secondary: #666666;
  --text-muted: #999999;
  --text-inverse: #ffffff;
  --border-subtle: #f0f0f0;
  --border-default: #e0e0e0;
  --accent-gold: #ffd700;
  --accent-dark: #1a1a2e;
  --shadow-card: 0 2rpx 12rpx rgba(0, 0, 0, 0.04);
}
```

- [ ] **Step 2: 提交**

```bash
git add miniprogram/styles/tokens.wxss
git commit -m "feat(p3): 完善暗色主题 tokens 覆盖"
```

---

## Task 2: 启用 app.js 主题切换

**Files:**
- Modify: `miniprogram/app.js`
- Modify: `miniprogram/app.wxss`

- [ ] **Step 1: 修改 app.js toggleTheme 和 updateTheme**

用 Edit 工具，替换 `miniprogram/app.js` 中 `toggleTheme` 和 `updateTheme` 方法：

```javascript
onLaunch() {
  this.globalData.isLightTheme = themeUtil.isLight()
},

onShow() {},

// P3: 启用主题切换
toggleTheme() {
  return themeUtil.toggle()
},

updateTheme(isLight) {
  const pages = getCurrentPages()
  pages.forEach(page => {
    if (page.updateTheme) page.updateTheme(isLight)
  })
},
```

- [ ] **Step 2: 更新 globalData**

将 `lightOnly: true` 字段删除或设置为 `false`：

```javascript
globalData: {
  functionName: 'mtgAsk',
  userInfo: null,
  isLightTheme: themeUtil.isLight(),
  lightOnly: false,
  showAIJudgeCard: false,
  db: db
},
```

- [ ] **Step 3: 提交**

```bash
git add miniprogram/app.js
git commit -m "feat(p3): 启用 app.js 主题切换（删除 lightOnly 锁定）"
```

---

## Task 3: Search 页面 - tag-chip tabs

**Files:**
- Modify: `miniprogram/pages/search/search.wxml`
- Modify: `miniprogram/pages/search/search.wxss`
- Modify: `miniprogram/pages/search/search.json`
- Modify: `miniprogram/pages/search/search.js`

- [ ] **Step 1: 读 search.js 了解 data 字段**

Read `miniprogram/pages/search/search.js` first to understand current data fields, then proceed.

- [ ] **Step 2: 更新 search.json 引用 tag-chip 组件**

```json
{
  "navigationBarTitleText": "搜索结果",
  "usingComponents": {
    "tag-chip": "/components/tag-chip/tag-chip",
    "empty-state": "/components/empty-state/empty-state"
  }
}
```

- [ ] **Step 3: 重置 WXML**

完整替换 `miniprogram/pages/search/search.wxml`：

```xml
<view class="container">
  <view class="nav-bar">
    <view class="back-btn" bindtap="goBack">‹</view>
    <text class="nav-title">搜索结果</text>
  </view>

  <view class="search-bar">
    <view class="search-row">
      <text class="search-icon">🔍</text>
      <input
        class="search-input"
        placeholder="搜索..."
        value="{{keyword}}"
        bindinput="onInput"
        bindconfirm="onSearch"
        confirm-type="search"
      />
    </view>
  </view>

  <view wx:if="{{searching}}" class="loading">
    <view class="loading-spinner"></view>
    <text class="loading-text">搜索中...</text>
  </view>

  <view wx:else class="results">
    <!-- 标签切换 -->
    <view class="tabs">
      <tag-chip text="全部 ({{totalCount}})" data-tab="all" bindtap="onSwitchTab" />
      <tag-chip text="卡牌 ({{combinedResults.cards.length}})" data-tab="cards" bindtap="onSwitchTab" />
      <tag-chip text="规则 ({{combinedResults.rules.length}})" data-tab="rules" bindtap="onSwitchTab" />
      <tag-chip text="关键词 ({{combinedResults.keywords.length}})" data-tab="keywords" bindtap="onSwitchTab" />
    </view>

    <!-- 卡牌结果 -->
    <view wx:if="{{currentTab === 'all' || currentTab === 'cards'}}" wx:if="{{combinedResults.cards.length > 0}}" class="result-section">
      <view class="section-title-wrap">
        <text class="section-title">卡牌</text>
      </view>
      <view class="card-list">
        <view class="card-item" wx:for="{{combinedResults.cards}}" wx:key="id" bindtap="viewCardDetail" data-id="{{item.id}}">
          <view class="card-name">{{item.zhs_name || item.name}}</view>
          <view class="card-type">{{item.type_line}}</view>
        </view>
      </view>
    </view>

    <!-- 规则结果 -->
    <view wx:if="{{(currentTab === 'all' || currentTab === 'rules') && combinedResults.rules.length > 0}}" class="result-section">
      <view class="section-title-wrap">
        <text class="section-title">规则</text>
      </view>
      <view class="result-list">
        <view class="result-card" wx:for="{{combinedResults.rules}}" wx:key="rule_number" bindtap="viewRuleDetail" data-rule="{{item.rule_number}}">
          <view class="result-header">
            <text class="result-number">{{item.rule_number}}</text>
            <text class="result-title">{{item.rule_title}}</text>
          </view>
          <text class="result-content">{{item.rule_content}}</text>
        </view>
      </view>
    </view>

    <!-- 关键词结果 -->
    <view wx:if="{{(currentTab === 'all' || currentTab === 'keywords') && combinedResults.keywords.length > 0}}" class="result-section">
      <view class="section-title-wrap">
        <text class="section-title">关键词异能</text>
      </view>
      <view class="result-list">
        <view class="result-card keyword-card" wx:for="{{combinedResults.keywords}}" wx:key="keyword_name" bindtap="viewKeywordDetail" data-keyword="{{item.keyword_name}}">
          <view class="result-header">
            <text class="result-number">{{item.keyword_en}}</text>
            <text class="result-title">{{item.keyword_name}}</text>
          </view>
          <text class="result-content">{{item.description}}</text>
        </view>
      </view>
    </view>

    <!-- 空态 -->
    <empty-state wx:if="{{!searching && searchDone && totalCount === 0}}" icon="search" title="未找到结果" desc="试试其他关键词" />
  </view>
</view>
```

- [ ] **Step 4: 重置 WXSS**

完整替换 `miniprogram/pages/search/search.wxss`：

```css
/* pages/search/search.wxss */
page { background: var(--bg-page); }
.container { min-height: 100vh; padding: 24rpx 32rpx; }
.nav-bar { display: flex; align-items: center; padding: 16rpx 0 24rpx; }
.back-btn { width: 64rpx; height: 64rpx; display: flex; align-items: center; justify-content: center; font-size: 48rpx; color: var(--text-primary); margin-right: 16rpx; }
.back-btn:active { opacity: 0.5; }
.nav-title { font-size: 36rpx; font-weight: 700; color: var(--text-primary); }

.search-bar { margin-bottom: 24rpx; }
.search-row { display: flex; align-items: center; background: var(--bg-card); border-radius: 20rpx; padding: 16rpx 20rpx; box-shadow: var(--shadow-card); }
.search-icon { font-size: 28rpx; margin-right: 12rpx; opacity: 0.5; }
.search-input { flex: 1; font-size: 28rpx; color: var(--text-primary); }

.loading { display: flex; flex-direction: column; align-items: center; padding: 80rpx 0; }
.loading-spinner { width: 48rpx; height: 48rpx; border: 4rpx solid var(--bg-input); border-top-color: var(--accent-dark); border-radius: 50%; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.loading-text { font-size: 24rpx; color: var(--text-secondary); margin-top: 16rpx; }

.tabs { display: flex; gap: 12rpx; margin-bottom: 24rpx; flex-wrap: wrap; }

.result-section { margin-bottom: 32rpx; }
.section-title-wrap { padding: 0 8rpx 16rpx; }
.section-title { font-size: 28rpx; font-weight: 600; color: var(--text-primary); }

.card-list, .result-list { display: flex; flex-direction: column; gap: 12rpx; }
.card-item { background: var(--bg-card); border-radius: 16rpx; box-shadow: var(--shadow-card); padding: 20rpx 24rpx; }
.card-item:active { opacity: 0.7; }
.card-name { font-size: 30rpx; font-weight: 600; color: var(--text-primary); }
.card-type { font-size: 22rpx; color: var(--text-secondary); margin-top: 4rpx; }

.result-card { background: var(--bg-card); border-radius: 16rpx; box-shadow: var(--shadow-card); padding: 20rpx 24rpx; }
.result-card:active { opacity: 0.7; }
.result-header { display: flex; align-items: center; gap: 16rpx; margin-bottom: 8rpx; }
.result-number { font-size: 24rpx; font-weight: 600; color: var(--accent-dark); font-family: monospace; }
.result-title { font-size: 28rpx; font-weight: 600; color: var(--text-primary); }
.result-content { font-size: 24rpx; color: var(--text-secondary); line-height: 1.6; }
```

- [ ] **Step 5: 清理 search.js 调试日志 + 添加 goBack/onSwitchTab**

```bash
sed -i '' '/console\.log.*CODEBUDDY_DEBUG/d' miniprogram/pages/search/search.js
grep -c CODEBUDDY_DEBUG miniprogram/pages/search/search.js
# Expected: 0
```

在 `miniprogram/pages/search/search.js` 添加：

```javascript
data: {
  // ... existing data
  currentTab: 'all'
},

onSwitchTab(e) {
  this.setData({ currentTab: e.currentTarget.dataset.tab })
},

goBack() {
  wx.navigateBack({ fail: () => wx.redirectTo({ url: '/pages/index/index' }) })
}
```

- [ ] **Step 6: 提交**

```bash
git add miniprogram/pages/search/
git commit -m "feat(p3): Search 页面视觉升级（tag-chip tabs + 明亮日间风）"
```

---

## Task 4: Card 详情页视觉升级

**Files:**
- Modify: `miniprogram/pages/card/card.wxml`
- Modify: `miniprogram/pages/card/card.wxss`
- Modify: `miniprogram/pages/card/card.js`
- Modify: `miniprogram/pages/card/card.json`

- [ ] **Step 1: 读 card.js 了解 currentCard 字段**

Read `miniprogram/pages/card/card.js` to see all fields in `currentCard` data object (e.g., `name`, `mana_cost`, `type_line`, `oracle_text`, `power`, `toughness`, `image_uris`, etc.). Adapt WXML accordingly.

- [ ] **Step 2: 更新 card.json**

```json
{
  "navigationBarTitleText": "卡牌详情",
  "usingComponents": {
    "empty-state": "/components/empty-state/empty-state",
    "tag-chip": "/components/tag-chip/tag-chip"
  }
}
```

- [ ] **Step 3: 重置 WXML**

完整替换 `miniprogram/pages/card/card.wxml`：

```xml
<view class="container">
  <view class="nav-bar">
    <view class="back-btn" bindtap="goBack">‹</view>
    <text class="nav-title">卡牌详情</text>
  </view>

  <view wx:if="{{loading}}" class="loading">
    <view class="loading-spinner"></view>
    <text class="loading-text">加载中...</text>
  </view>

  <view wx:elif="{{error}}" class="error-state">
    <empty-state icon="search" title="加载失败" desc="{{error}}" actionText="重试" bindaction="onRetry" />
  </view>

  <view wx:elif="{{!currentCard}}" class="empty-state">
    <empty-state icon="search" title="未找到卡牌" />
  </view>

  <view wx:else class="card-content">
    <!-- 顶图 -->
    <view class="card-image-card">
      <image
        wx:if="{{currentCard.image_uris && currentCard.image_uris.normal}}"
        class="card-image"
        src="{{currentCard.image_uris.normal}}"
        mode="aspectFit"
      />
      <view wx:else class="card-image-placeholder">
        <text>无图片</text>
      </view>
    </view>

    <!-- 标题区 -->
    <view class="card-header">
      <text class="card-name">{{currentCard.zhs_name || currentCard.name}}</text>
      <text wx:if="{{currentCard.name && currentCard.zhs_name && currentCard.name !== currentCard.zhs_name}}" class="card-name-en">{{currentCard.name}}</text>
      <text wx:if="{{currentCard.mana_cost}}" class="card-mana">{{currentCard.mana_cost}}</text>
    </view>

    <!-- 标签 -->
    <view class="card-tags">
      <tag-chip wx:if="{{currentCard.type_line}}" text="{{currentCard.type_line}}" />
      <tag-chip wx:if="{{currentCard.rarity}}" text="{{currentCard.rarity}}" color="var(--accent-gold)" />
    </view>

    <!-- 正文 -->
    <view class="card-body">
      <view wx:if="{{currentCard.oracle_text}}" class="card-text">
        <text>{{currentCard.oracle_text}}</text>
      </view>
      <view wx:if="{{currentCard.flavor_text}}" class="card-flavor">
        <text>{{currentCard.flavor_text}}</text>
      </view>
      <view wx:if="{{currentCard.power !== undefined}}" class="card-stats">
        <text class="stats-value">{{currentCard.power}}/{{currentCard.toughness}}</text>
      </view>
    </view>

    <!-- 操作 -->
    <view class="card-actions">
      <view class="action-btn" bindtap="onShare">分享</view>
      <view class="action-btn" bindtap="onCopyName">复制牌名</view>
    </view>
  </view>
</view>
```

- [ ] **Step 4: 重置 WXSS**

完整替换 `miniprogram/pages/card/card.wxss`：

```css
/* pages/card/card.wxss */
page { background: var(--bg-page); }
.container { min-height: 100vh; padding: 24rpx 32rpx; }
.nav-bar { display: flex; align-items: center; padding: 16rpx 0 24rpx; }
.back-btn { width: 64rpx; height: 64rpx; display: flex; align-items: center; justify-content: center; font-size: 48rpx; color: var(--text-primary); margin-right: 16rpx; }
.back-btn:active { opacity: 0.5; }
.nav-title { font-size: 36rpx; font-weight: 700; color: var(--text-primary); }

.loading { display: flex; flex-direction: column; align-items: center; padding: 80rpx 0; }
.loading-spinner { width: 48rpx; height: 48rpx; border: 4rpx solid var(--bg-input); border-top-color: var(--accent-dark); border-radius: 50%; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.loading-text { font-size: 24rpx; color: var(--text-secondary); margin-top: 16rpx; }

.card-content { display: flex; flex-direction: column; gap: 24rpx; }
.card-image-card { background: var(--bg-card); border-radius: 20rpx; box-shadow: var(--shadow-card); padding: 32rpx; display: flex; align-items: center; justify-content: center; min-height: 400rpx; }
.card-image { width: 100%; max-width: 480rpx; height: auto; }
.card-image-placeholder { font-size: 28rpx; color: var(--text-muted); padding: 80rpx 0; }

.card-header { background: var(--bg-card); border-radius: 20rpx; box-shadow: var(--shadow-card); padding: 24rpx; }
.card-name { font-size: 36rpx; font-weight: 700; color: var(--text-primary); display: block; }
.card-name-en { font-size: 24rpx; color: var(--text-secondary); display: block; margin-top: 4rpx; }
.card-mana { font-size: 28rpx; color: var(--accent-dark); font-weight: 600; display: block; margin-top: 8rpx; font-family: monospace; }

.card-tags { display: flex; gap: 12rpx; flex-wrap: wrap; }

.card-body { background: var(--bg-card); border-radius: 20rpx; box-shadow: var(--shadow-card); padding: 24rpx; }
.card-text { font-size: 28rpx; color: var(--text-primary); line-height: 1.7; }
.card-flavor { font-size: 24rpx; color: var(--text-secondary); font-style: italic; margin-top: 16rpx; line-height: 1.6; }
.card-stats { margin-top: 16rpx; text-align: center; padding: 16rpx; background: var(--bg-input); border-radius: 12rpx; }
.stats-value { font-size: 40rpx; font-weight: 700; color: var(--text-primary); }

.card-actions { display: flex; gap: 16rpx; }
.action-btn { flex: 1; background: var(--bg-card); color: var(--text-primary); border-radius: 16rpx; padding: 24rpx; text-align: center; font-size: 28rpx; box-shadow: var(--shadow-card); }
.action-btn:active { opacity: 0.7; }
```

- [ ] **Step 5: card.js 清理 + 添加 goBack / onRetry / onShare / onCopyName**

```bash
sed -i '' '/console\.log.*CODEBUDDY_DEBUG/d' miniprogram/pages/card/card.js
```

在 Page methods 添加：

```javascript
goBack() {
  wx.navigateBack({ fail: () => wx.redirectTo({ url: '/pages/index/index' }) })
},

onRetry() {
  // 重新调用 fetchCardDetail 或 performApiSearch
  this.setData({ error: null })
  // 重新触发当前已加载的卡牌（需要在 data 中保留 id 或 keyword）
  const id = this.data.currentCard && this.data.currentCard.id
  if (id) this.fetchCardDetail(id)
},

onShare() {
  wx.showToast({ title: '点击右上角分享', icon: 'none' })
},

onCopyName() {
  const name = this.data.currentCard && (this.data.currentCard.zhs_name || this.data.currentCard.name)
  if (name) {
    wx.setClipboardData({ data: name, success: () => wx.showToast({ title: '已复制', icon: 'success' }) })
  }
}
```

- [ ] **Step 6: 提交**

```bash
git add miniprogram/pages/card/
git commit -m "feat(p3): Card 详情页视觉升级（统一详情布局）"
```

---

## Task 5: Rule 详情页视觉升级

**Files:**
- Modify: `miniprogram/pages/rule/rule.wxml`
- Modify: `miniprogram/pages/rule/rule.wxss`
- Modify: `miniprogram/pages/rule/rule.js`
- Modify: `miniprogram/pages/rule/rule.json`

- [ ] **Step 1: 更新 rule.json**

```json
{
  "navigationBarTitleText": "规则详情",
  "usingComponents": {
    "empty-state": "/components/empty-state/empty-state",
    "tag-chip": "/components/tag-chip/tag-chip"
  }
}
```

- [ ] **Step 2: 重置 WXML**

完整替换 `miniprogram/pages/rule/rule.wxml`：

```xml
<view class="container">
  <view class="nav-bar">
    <view class="back-btn" bindtap="goBack">‹</view>
    <text class="nav-title">规则详情</text>
  </view>

  <view wx:if="{{loading}}" class="loading">
    <view class="loading-spinner"></view>
    <text class="loading-text">加载中...</text>
  </view>

  <view wx:elif="{{error}}" class="error-state">
    <empty-state icon="search" title="加载失败" desc="{{error}}" actionText="重试" bindaction="onRetry" />
  </view>

  <view wx:elif="{{!ruleDetail}}" class="empty-state">
    <empty-state icon="search" title="未找到规则" />
  </view>

  <view wx:else class="rule-content">
    <view class="rule-header">
      <text class="rule-number">{{ruleDetail.rule_number}}</text>
      <text class="rule-title">{{ruleDetail.rule_title}}</text>
    </view>

    <view class="rule-tags">
      <tag-chip text="中文" data-lang="cn" bindtap="switchLang" />
      <tag-chip text="English" data-lang="en" bindtap="switchLang" />
    </view>

    <view class="rule-body">
      <view wx:if="{{showCn}}">
        <view class="rule-line" wx:for="{{ruleDetail.contentLines_cn}}" wx:key="*this">
          <text>{{item}}</text>
        </view>
      </view>
      <view wx:else>
        <view class="rule-line" wx:for="{{ruleDetail.contentLines_en}}" wx:key="*this">
          <text>{{item}}</text>
        </view>
      </view>
    </view>
  </view>
</view>
```

- [ ] **Step 3: 重置 WXSS**

完整替换 `miniprogram/pages/rule/rule.wxss`：

```css
/* pages/rule/rule.wxss */
page { background: var(--bg-page); }
.container { min-height: 100vh; padding: 24rpx 32rpx; }
.nav-bar { display: flex; align-items: center; padding: 16rpx 0 24rpx; }
.back-btn { width: 64rpx; height: 64rpx; display: flex; align-items: center; justify-content: center; font-size: 48rpx; color: var(--text-primary); margin-right: 16rpx; }
.back-btn:active { opacity: 0.5; }
.nav-title { font-size: 36rpx; font-weight: 700; color: var(--text-primary); }

.loading { display: flex; flex-direction: column; align-items: center; padding: 80rpx 0; }
.loading-spinner { width: 48rpx; height: 48rpx; border: 4rpx solid var(--bg-input); border-top-color: var(--accent-dark); border-radius: 50%; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.loading-text { font-size: 24rpx; color: var(--text-secondary); margin-top: 16rpx; }

.rule-content { display: flex; flex-direction: column; gap: 24rpx; }
.rule-header { background: var(--bg-card); border-radius: 20rpx; box-shadow: var(--shadow-card); padding: 24rpx; }
.rule-number { font-size: 24rpx; color: var(--accent-dark); font-weight: 600; font-family: monospace; display: block; margin-bottom: 4rpx; }
.rule-title { font-size: 32rpx; font-weight: 700; color: var(--text-primary); display: block; }

.rule-tags { display: flex; gap: 12rpx; }

.rule-body { background: var(--bg-card); border-radius: 20rpx; box-shadow: var(--shadow-card); padding: 24rpx; }
.rule-line { font-size: 28rpx; color: var(--text-primary); line-height: 1.8; padding: 8rpx 0; border-bottom: 1rpx solid var(--border-subtle); }
.rule-line:last-child { border-bottom: none; }
```

- [ ] **Step 4: rule.js 添加 goBack / onRetry**

修改 `miniprogram/pages/rule/rule.js`，在 Page methods 添加：

```javascript
goBack() {
  wx.navigateBack({ fail: () => wx.redirectTo({ url: '/pages/index/index' }) })
},

onRetry() {
  this.setData({ error: null })
  this.fetchRuleDetail()
}
```

并将 `switchLang` 改为从 dataset 读取：

```javascript
switchLang(e) {
  const lang = e.currentTarget.dataset.lang
  this.setData({ showCn: lang === 'cn' })
}
```

- [ ] **Step 5: 提交**

```bash
git add miniprogram/pages/rule/
git commit -m "feat(p3): Rule 详情页视觉升级（统一详情布局）"
```

---

## Task 6: Keyword 详情页视觉升级

**Files:**
- Modify: `miniprogram/pages/keyword/keyword.wxml`
- Modify: `miniprogram/pages/keyword/keyword.wxss`
- Modify: `miniprogram/pages/keyword/keyword.js`
- Modify: `miniprogram/pages/keyword/keyword.json`

- [ ] **Step 1: 更新 keyword.json**

```json
{
  "navigationBarTitleText": "关键词异能",
  "usingComponents": {
    "empty-state": "/components/empty-state/empty-state",
    "tag-chip": "/components/tag-chip/tag-chip"
  }
}
```

- [ ] **Step 2: 重置 WXML**

完整替换 `miniprogram/pages/keyword/keyword.wxml`：

```xml
<view class="container">
  <view class="nav-bar">
    <view class="back-btn" bindtap="goBack">‹</view>
    <text class="nav-title">关键词异能</text>
  </view>

  <view class="search-bar">
    <view class="search-row">
      <text class="search-icon">🔍</text>
      <input
        class="search-input"
        placeholder="输入关键词（如 飞行、Trample）"
        value="{{keyword}}"
        bindinput="onInput"
        bindconfirm="onSearch"
        confirm-type="search"
      />
    </view>
  </view>

  <!-- 搜索结果区 -->
  <view wx:if="{{searchDone && !showDetail}}" class="results">
    <view wx:if="{{searching}}" class="loading">
      <view class="loading-spinner"></view>
      <text class="loading-text">搜索中...</text>
    </view>

    <view wx:elif="{{keywordResults.length === 0 && ruleResults.length === 0}}" class="empty-state-wrap">
      <empty-state icon="search" title="未找到结果" desc="试试其他关键词" />
    </view>

    <view wx:else>
      <view wx:if="{{keywordResults.length > 0}}" class="result-section">
        <view class="section-title-wrap">
          <text class="section-title">关键词</text>
        </view>
        <view class="result-list">
          <view class="result-card" wx:for="{{keywordResults}}" wx:key="keyword_name" bindtap="viewKeywordDetail" data-keyword="{{item.keyword_name}}">
            <view class="result-header">
              <text class="result-title">{{item.keyword_name}}</text>
              <text class="result-en">{{item.keyword_en}}</text>
            </view>
            <text class="result-desc">{{item.description}}</text>
          </view>
        </view>
      </view>

      <view wx:if="{{ruleResults.length > 0}}" class="result-section">
        <view class="section-title-wrap">
          <text class="section-title">相关规则</text>
        </view>
        <view class="result-list">
          <view class="result-card" wx:for="{{ruleResults}}" wx:key="rule_number" bindtap="onRuleTap" data-rule="{{item.rule_number}}">
            <view class="result-header">
              <text class="result-number">{{item.rule_number}}</text>
              <text class="result-title">{{item.rule_title}}</text>
            </view>
          </view>
        </view>
      </view>
    </view>
  </view>

  <!-- 详情区 -->
  <view wx:if="{{showDetail && keywordDetail}}" class="detail">
    <view class="detail-header">
      <text class="detail-title">{{currentKeyword}}</text>
      <text wx:if="{{keywordDetail.keyword_en}}" class="detail-en">{{keywordDetail.keyword_en}}</text>
    </view>

    <view class="detail-body">
      <view class="detail-text">
        <text>{{keywordDetail.description || keywordDetail.definition}}</text>
      </view>

      <view wx:if="{{relatedRules.length > 0}}" class="related-rules">
        <view class="section-title-wrap">
          <text class="section-title">相关规则</text>
        </view>
        <view class="result-list">
          <view class="result-card" wx:for="{{relatedRules}}" wx:key="rule_number" bindtap="onRuleTap" data-rule="{{item.rule_number}}">
            <view class="result-header">
              <text class="result-number">{{item.rule_number}}</text>
              <text class="result-title">{{item.rule_title}}</text>
            </view>
          </view>
        </view>
      </view>
    </view>

    <view class="back-to-list" bindtap="closeDetail">‹ 返回列表</view>
  </view>
</view>
```

- [ ] **Step 3: 重置 WXSS**

完整替换 `miniprogram/pages/keyword/keyword.wxss`：

```css
/* pages/keyword/keyword.wxss */
page { background: var(--bg-page); }
.container { min-height: 100vh; padding: 24rpx 32rpx; }
.nav-bar { display: flex; align-items: center; padding: 16rpx 0 24rpx; }
.back-btn { width: 64rpx; height: 64rpx; display: flex; align-items: center; justify-content: center; font-size: 48rpx; color: var(--text-primary); margin-right: 16rpx; }
.back-btn:active { opacity: 0.5; }
.nav-title { font-size: 36rpx; font-weight: 700; color: var(--text-primary); }

.search-bar { margin-bottom: 24rpx; }
.search-row { display: flex; align-items: center; background: var(--bg-card); border-radius: 20rpx; padding: 16rpx 20rpx; box-shadow: var(--shadow-card); }
.search-icon { font-size: 28rpx; margin-right: 12rpx; opacity: 0.5; }
.search-input { flex: 1; font-size: 28rpx; color: var(--text-primary); }

.loading { display: flex; flex-direction: column; align-items: center; padding: 80rpx 0; }
.loading-spinner { width: 48rpx; height: 48rpx; border: 4rpx solid var(--bg-input); border-top-color: var(--accent-dark); border-radius: 50%; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.loading-text { font-size: 24rpx; color: var(--text-secondary); margin-top: 16rpx; }

.result-section { margin-bottom: 32rpx; }
.section-title-wrap { padding: 0 8rpx 16rpx; }
.section-title { font-size: 28rpx; font-weight: 600; color: var(--text-primary); }

.result-list { display: flex; flex-direction: column; gap: 12rpx; }
.result-card { background: var(--bg-card); border-radius: 16rpx; box-shadow: var(--shadow-card); padding: 20rpx 24rpx; }
.result-card:active { opacity: 0.7; }
.result-header { display: flex; align-items: center; gap: 16rpx; margin-bottom: 8rpx; }
.result-title { font-size: 30rpx; font-weight: 600; color: var(--text-primary); }
.result-en { font-size: 22rpx; color: var(--text-secondary); font-family: monospace; }
.result-number { font-size: 24rpx; font-weight: 600; color: var(--accent-dark); font-family: monospace; }
.result-desc { font-size: 24rpx; color: var(--text-secondary); line-height: 1.6; }

.detail { display: flex; flex-direction: column; gap: 24rpx; }
.detail-header { background: var(--bg-card); border-radius: 20rpx; box-shadow: var(--shadow-card); padding: 24rpx; }
.detail-title { font-size: 40rpx; font-weight: 700; color: var(--text-primary); display: block; }
.detail-en { font-size: 24rpx; color: var(--text-secondary); display: block; margin-top: 4rpx; font-family: monospace; }

.detail-body { background: var(--bg-card); border-radius: 20rpx; box-shadow: var(--shadow-card); padding: 24rpx; }
.detail-text { font-size: 28rpx; color: var(--text-primary); line-height: 1.8; }
.related-rules { margin-top: 24rpx; }

.back-to-list { text-align: center; padding: 24rpx; color: var(--accent-dark); font-size: 28rpx; }
.back-to-list:active { opacity: 0.7; }
```

- [ ] **Step 4: 清理 keyword.js + 添加 goBack / onRuleTap**

```bash
sed -i '' '/console\.log.*CODEBUDDY_DEBUG/d' miniprogram/pages/keyword/keyword.js
```

在 Page methods 添加：

```javascript
goBack() {
  wx.navigateBack({ fail: () => wx.redirectTo({ url: '/pages/index/index' }) })
},

onRuleTap(e) {
  const rule = e.currentTarget.dataset.rule
  if (rule) {
    wx.navigateTo({ url: `/pages/rule/rule?rule=${encodeURIComponent(rule)}` })
  }
}
```

- [ ] **Step 5: 提交**

```bash
git add miniprogram/pages/keyword/
git commit -m "feat(p3): Keyword 详情页视觉升级"
```

---

## Task 7: Agent (AI 裁判) 视觉升级

**Files:**
- Modify: `miniprogram/pages/agent/agent.wxml`
- Modify: `miniprogram/pages/agent/agent.wxss`
- Modify: `miniprogram/pages/agent/agent.js`

- [ ] **Step 1: 读 agent.js 了解所有 data 字段**

`miniprogram/pages/agent/agent.js` 已在上文读取过。关键字段：
- `messages[]`: `{ role, content, parsedNodes, time }`
- `inputValue`, `loading`, `scrollIntoView`
- `aiAvatar`, `shortMode`, `sessionId`, `openid`
- `isLoading`, `loadingStep`, `loadingText`, `thinkingStep`, `thinkingText`
- 方法：`initOpenid`, `loadHistory`, `sendMessage`, `chat`, `useExample`, `setShortMode`, `newSession`, `clearSession`, `retryLast`, `copyMessage`, `refreshMessages`, `goToIndex`, `toggleTheme`, `onInput`

- [ ] **Step 2: 重置 WXML**

完整替换 `miniprogram/pages/agent/agent.wxml`：

```xml
<view class="container">
  <view class="nav-bar">
    <view class="back-btn" bindtap="goToIndex">‹</view>
    <text class="nav-title">AI 裁判</text>
    <view class="nav-actions">
      <view class="nav-btn" bindtap="newSession">新会话</view>
    </view>
  </view>

  <!-- 加载中（init） -->
  <view wx:if="{{isLoading}}" class="loading-screen">
    <view class="loading-spinner"></view>
    <text class="loading-text">{{loadingText}}</text>
  </view>

  <!-- 消息列表 -->
  <view wx:else class="chat-container">
    <view wx:if="{{messages.length === 0}}" class="empty-chat">
      <view class="empty-icon">✦</view>
      <text class="empty-title">AI 裁判助手</text>
      <text class="empty-desc">智能规则问答 · 随时随地</text>
      <view class="example-list">
        <view wx:for="{{examples}}" wx:key="*this" class="example-item" bindtap="useExample" data-q="{{item}}">
          <text>{{item}}</text>
        </view>
      </view>
    </view>

    <view wx:else class="messages">
      <view
        wx:for="{{messages}}"
        wx:key="index"
        id="msg-{{index}}"
        class="message {{item.role === 'user' ? 'message-user' : 'message-assistant'}}"
      >
        <view wx:if="{{item.role === 'assistant'}}" class="message-avatar">
          <image class="avatar-img" src="{{aiAvatar}}" mode="aspectFit"></image>
        </view>
        <view class="message-bubble">
          <view class="message-content">
            <rich-text wx:if="{{item.parsedNodes}}" nodes="{{item.parsedNodes}}"></rich-text>
            <text wx:else>{{item.content}}</text>
          </view>
          <text class="message-time">{{item.time}}</text>
        </view>
        <view wx:if="{{item.role === 'user'}}" class="message-avatar user-avatar">
          <text>我</text>
        </view>
      </view>

      <!-- 思考中动画 -->
      <view wx:if="{{loading}}" class="message message-assistant">
        <view class="message-avatar">
          <image class="avatar-img" src="{{aiAvatar}}" mode="aspectFit"></image>
        </view>
        <view class="message-bubble thinking-bubble">
          <view class="thinking-dots">
            <view class="dot"></view>
            <view class="dot"></view>
            <view class="dot"></view>
          </view>
          <text class="thinking-text">{{thinkingText || '正在思考...'}}</text>
        </view>
      </view>
    </view>
  </view>

  <!-- 输入区 -->
  <view class="input-bar">
    <view class="input-row">
      <textarea
        class="input-field"
        placeholder="输入问题..."
        value="{{inputValue}}"
        bindinput="onInput"
        auto-height
        maxlength="500"
      ></textarea>
      <view class="send-btn {{inputValue.length > 0 ? 'active' : ''}}" bindtap="sendMessage">
        <text>发送</text>
      </view>
    </view>
  </view>
</view>
```

- [ ] **Step 3: 重置 WXSS**

完整替换 `miniprogram/pages/agent/agent.wxss`：

```css
/* pages/agent/agent.wxss */
page { background: var(--bg-page); }
.container { min-height: 100vh; display: flex; flex-direction: column; }

.nav-bar { display: flex; align-items: center; padding: 16rpx 24rpx; background: var(--bg-card); border-bottom: 1rpx solid var(--border-subtle); }
.back-btn { width: 64rpx; height: 64rpx; display: flex; align-items: center; justify-content: center; font-size: 48rpx; color: var(--text-primary); }
.back-btn:active { opacity: 0.5; }
.nav-title { font-size: 32rpx; font-weight: 700; color: var(--text-primary); flex: 1; }
.nav-actions { display: flex; gap: 12rpx; }
.nav-btn { background: var(--bg-input); color: var(--text-primary); padding: 12rpx 20rpx; border-radius: 12rpx; font-size: 24rpx; }
.nav-btn:active { opacity: 0.7; }

.loading-screen { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; }
.loading-spinner { width: 48rpx; height: 48rpx; border: 4rpx solid var(--bg-input); border-top-color: var(--accent-dark); border-radius: 50%; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.loading-text { font-size: 24rpx; color: var(--text-secondary); margin-top: 16rpx; }

.chat-container { flex: 1; padding: 24rpx 24rpx 0; overflow-y: auto; }
.empty-chat { display: flex; flex-direction: column; align-items: center; padding: 80rpx 0; }
.empty-icon { font-size: 80rpx; color: var(--accent-gold); margin-bottom: 24rpx; }
.empty-title { font-size: 32rpx; font-weight: 700; color: var(--text-primary); }
.empty-desc { font-size: 24rpx; color: var(--text-secondary); margin-top: 8rpx; margin-bottom: 32rpx; }
.example-list { display: flex; flex-direction: column; gap: 12rpx; width: 100%; max-width: 600rpx; }
.example-item { background: var(--bg-card); border-radius: 16rpx; padding: 20rpx 24rpx; font-size: 26rpx; color: var(--text-primary); box-shadow: var(--shadow-card); }
.example-item:active { opacity: 0.7; }

.messages { display: flex; flex-direction: column; gap: 24rpx; }
.message { display: flex; gap: 12rpx; align-items: flex-start; }
.message-user { flex-direction: row-reverse; }
.message-avatar { width: 64rpx; height: 64rpx; border-radius: 50%; background: var(--accent-gold); display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.avatar-img { width: 48rpx; height: 48rpx; border-radius: 50%; }
.user-avatar { background: var(--accent-dark); color: var(--text-inverse); font-size: 22rpx; font-weight: 600; }

.message-bubble { max-width: 75%; background: var(--bg-card); border-radius: 20rpx; padding: 20rpx 24rpx; box-shadow: var(--shadow-card); }
.message-user .message-bubble { background: var(--accent-dark); color: var(--text-inverse); }
.message-content { font-size: 28rpx; color: var(--text-primary); line-height: 1.7; }
.message-user .message-content { color: var(--text-inverse); }
.message-time { font-size: 20rpx; color: var(--text-muted); margin-top: 8rpx; display: block; }
.message-user .message-time { color: rgba(255, 255, 255, 0.5); }

.thinking-bubble { display: flex; align-items: center; gap: 16rpx; }
.thinking-dots { display: flex; gap: 8rpx; }
.dot { width: 16rpx; height: 16rpx; border-radius: 50%; background: var(--text-secondary); animation: pulse 1.4s infinite; }
.dot:nth-child(2) { animation-delay: 0.2s; }
.dot:nth-child(3) { animation-delay: 0.4s; }
@keyframes pulse { 0%, 60%, 100% { opacity: 0.4; } 30% { opacity: 1; } }
.thinking-text { font-size: 24rpx; color: var(--text-secondary); }

.input-bar { padding: 16rpx 24rpx; background: var(--bg-card); border-top: 1rpx solid var(--border-subtle); }
.input-row { display: flex; align-items: flex-end; gap: 12rpx; }
.input-field { flex: 1; background: var(--bg-input); border-radius: 20rpx; padding: 16rpx 20rpx; font-size: 28rpx; color: var(--text-primary); min-height: 80rpx; max-height: 200rpx; }
.send-btn { background: var(--bg-input); color: var(--text-muted); padding: 16rpx 28rpx; border-radius: 20rpx; font-size: 28rpx; font-weight: 600; }
.send-btn.active { background: var(--accent-dark); color: var(--text-inverse); }
.send-btn:active { opacity: 0.7; }
```

- [ ] **Step 4: agent.js 修改（保留所有 chat 逻辑）**

修改 `miniprogram/pages/agent/agent.js`：

1. **删除 `toggleTheme` 方法**（P3 启用全局 toggleTheme，agent 不再需要单独的）

2. **添加 `examples` 字段**：
```javascript
data: {
  // ... existing fields
  examples: [
    '什么是飞行异能？',
    '黑色莲花有什么特殊能力？',
    '战斗中如何计算伤害？',
    '什么是连击？'
  ]
}
```

3. **清理 CODEBUDDY_DEBUG**：
```bash
sed -i '' '/console\.log.*CODEBUDDY_DEBUG/d' miniprogram/pages/agent/agent.js
```

4. **确保 `useExample` 与 WXML 一致**（已存在 `data-q` 绑定）

- [ ] **Step 5: 提交**

```bash
git add miniprogram/pages/agent/
git commit -m "feat(p3): Agent 页面视觉升级（聊天气泡 + 思考动画）"
```

---

## Task 8: 整体验证 + 暗色主题测试

**Files:**
- Modify: 无（仅验证）

- [ ] **Step 1: 亮色主题验证**

微信开发者工具中验证 5 个页面：
1. search: 标签切换 + 结果区
2. card: 顶图 + 标题 + 标签 + 正文 + 操作
3. rule: 顶图 + 标题 + 中英切换 + 分段
4. keyword: 搜索 + 详情
5. agent: 聊天气泡 + 思考动画 + 输入区

- [ ] **Step 2: 暗色主题验证**

添加一个临时按钮到首页（仅测试用）调用 `app.toggleTheme()`，切换到暗色后验证 5 个页面：
- 背景应变为深色（`#0f1419`）
- 卡片应变为深色（`#1a1f2e`）
- 文字应变为白色
- 阴影应变更深
- 边框、accent 色（gold）保持不变

或者直接在 DevTools 控制台执行 `getApp().toggleTheme()` 测试。

- [ ] **Step 3: 主题切换功能验证**

- toggleTheme 应能切换亮/暗
- 切换后所有页面应响应（通过 `updateTheme` 广播）
- 刷新页面后主题设置保持（存储在 storage）

- [ ] **Step 4: 提交验收报告（可选）**

- [ ] **Step 5: 合并 dev 到 main**

```bash
git checkout main
git pull origin main
git merge dev --no-ff -m "merge: P3 核心交互页视觉升级 + 暗色主题回归（8 任务）"
git push origin main
git push origin dev
```

---

## P3 验收清单

- [ ] tokens.wxss 暗色变量完整覆盖
- [ ] app.js 启用主题切换
- [ ] 5 个页面视觉升级（明亮日间风）
- [ ] search 标签切换可用
- [ ] 详情页统一布局（顶图 + 标题 + 标签 + 正文 + 操作）
- [ ] agent 聊天气泡 + 思考动画
- [ ] 暗色主题在所有 5 个页面视觉一致
- [ ] 主题切换无闪烁
- [ ] iOS / Android 真机各验证一次
- [ ] 控制台无 error/warning

---

## 下一步

P3 完成后是 P4（剩余 8 个页面）：
- setcards / sldcards / promos / feedback / devlog / apitest / loading / odds

P4 计划在 P3 完成后生成。