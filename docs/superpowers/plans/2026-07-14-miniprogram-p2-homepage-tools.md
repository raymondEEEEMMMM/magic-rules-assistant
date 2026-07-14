# mtgAsk 小程序前端 P2 首页+工具页 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 升级首页 + 5 个工具页（token、token-generate、decks、deck-detail、counter、dice）的视觉为明亮日间风，建立设计系统应用样板。

**Architecture:** 自上而下——
1. 全局：隐藏暗色主题切换入口（锁定亮色）
2. 首页：用 `card-list-item` 替换工具入口，AI 裁判用深底横幅
3. 工具页：白底+微阴影，5 色图标色块，空/加载态统一

**Tech Stack:** 微信原生小程序 + P1 设计系统（tokens / 7 组件 / utils）

**依赖：** P1 完成（`f3aee45` on main），所有 utils 和组件已就位

**Spec 参考：** `docs/superpowers/specs/2026-07-14-miniprogram-frontend-optimization-design.md` 第 2、6.2 节

---

## 文件结构

**修改**：
- `miniprogram/app.js` — 隐藏暗色主题切换
- `miniprogram/pages/index/index.wxml` + `.wxss` + `.js` — 新首页
- `miniprogram/pages/token/token.wxml` + `.wxss` + `.js` — Token 列表
- `miniprogram/pages/token-generate/token-generate.wxml` + `.wxss` + `.js` — Token 生成器
- `miniprogram/pages/decks/decks.wxml` + `.wxss` + `.js` — 我的套牌
- `miniprogram/pages/deck-detail/deck-detail.wxml` + `.wxss` + `.js` — 套牌详情
- `miniprogram/pages/counter/counter.wxml` + `.wxss` + `.js` — 生命值
- `miniprogram/pages/dice/dice.wxml` + `.wxss` + `.js` — 骰子

**无需修改**：各页面的 .json（组件引用沿用 P1）

---

## Task 1: 隐藏暗色主题切换

**Files:**
- Modify: `miniprogram/app.js`
- Modify: `miniprogram/app.wxss`

- [ ] **Step 1: app.js 添加 lightOnly 标志**

修改 `miniprogram/app.js` 的 `globalData` 和 `toggleTheme`：

```javascript
const themeUtil = require('./utils/theme.js')

wx.cloud.init({
  env: 'magic-rules-assistant-0a1904c329',
  traceUser: true
})

const db = wx.cloud.database()

App({
  globalData: {
    functionName: 'mtgAsk',
    userInfo: null,
    isLightTheme: true,        // P2: 锁定亮色
    lightOnly: true,            // P2: 新增标志
    showAIJudgeCard: false,
    db: db
  },

  version: '1.0.0',

  onLaunch() {
    this.globalData.isLightTheme = true
  },

  onShow() {},

  // P2: 锁定亮色，toggleTheme 改为 noop
  toggleTheme() {
    console.log('[app] P2: 暗色主题已锁定为亮色，P3 阶段开放')
    return true
  },

  updateTheme(isLight) {
    // P2: 强制忽略，锁定为 true
    const pages = getCurrentPages()
    pages.forEach(page => {
      if (page.updateTheme) page.updateTheme(true)
    })
  },

  checkLogin() {
    wx.getSetting({
      success: res => {
        if (res.authSetting['scope.userInfo']) {
          wx.getUserInfo({
            success: res => { this.globalData.userInfo = res.userInfo }
          })
        }
      }
    })
  }
})
```

- [ ] **Step 2: app.wxss 移除暗色 theme-light 兼容**

修改 `miniprogram/app.wxss`：

```css
/* 全局样式入口 */
@import './styles/tokens.wxss';
@import './styles/base.wxss';
@import './styles/utilities.wxss';

/* P2: 暗色主题兼容代码已迁移到 .theme-dark（P3 阶段启用），此处不再使用 */
```

- [ ] **Step 3: 提交**

```bash
git add miniprogram/app.js miniprogram/app.wxss
git commit -m "feat(p2): 锁定亮色主题（隐藏暗色切换入口，P3 阶段恢复）"
```

---

## Task 2: 首页视觉升级 - 顶部 + 搜索

**Files:**
- Modify: `miniprogram/pages/index/index.wxml`
- Modify: `miniprogram/pages/index/index.wxss`

- [ ] **Step 1: 重写 index.wxml 顶部区**

替换 `miniprogram/pages/index/index.wxml` 顶部（line 1-43，banner + 搜索框部分）：

```xml
<!--pages/index/index.wxml-->
<view class="container {{isLightTheme ? 'page-light' : ''}}">
  <!-- 顶部品牌区（明亮日间风） -->
  <view class="brand-section">
    <view class="brand-content">
      <text class="brand-title">MTGAsk</text>
      <text class="brand-subtitle">万智牌规则问答助手</text>
    </view>
  </view>

  <!-- 搜索框（卡片包裹） -->
  <view class="search-card">
    <view class="search-row">
      <text class="search-icon">🔍</text>
      <input
        class="search-input"
        placeholder="异能关键词、卡牌、规则编号..."
        placeholder-class="search-placeholder"
        bindinput="onInput"
        bindconfirm="onSearch"
        confirm-type="search"
        value="{{keyword}}"
      />
      <view class="search-clear" wx:if="{{keyword}}" bindtap="clearSearch">
        <text>✕</text>
      </view>
    </view>
    <view class="search-btn" bindtap="onSearch">搜索</view>
  </view>

  <!-- 后续：AI 裁判横幅 / 工具列表 / 系列 / SLD / 历史 保持不变 -->
  <!-- ... 保留 index.wxml line 12 起原有结构（去掉 banner 主题按钮已隐藏） -->
</view>
```

- [ ] **Step 2: 重写 index.wxss 顶部样式**

修改 `miniprogram/pages/index/index.wxss`，替换旧 banner + search 样式（line 14-100 部分）：

```css
/* pages/index/index.wxss */

/* 全局 - 保留 */
page {
  background-color: var(--bg-page);
  color: var(--text-primary);
}

.container {
  min-height: 100vh;
  padding: 0;
  display: flex;
  flex-direction: column;
}

/* 顶部品牌区（明亮日间风） */
.brand-section {
  padding: 60rpx 40rpx 40rpx;
  padding-top: calc(60rpx + env(safe-area-inset-top));
  text-align: center;
  background: var(--bg-page);
}
.brand-content {
  display: flex;
  flex-direction: column;
  align-items: center;
}
.brand-title {
  display: block;
  font-size: 56rpx;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -1rpx;
}
.brand-subtitle {
  display: block;
  font-size: 24rpx;
  color: var(--text-secondary);
  margin-top: 8rpx;
}

/* 搜索框卡片 */
.search-card {
  margin: 24rpx 32rpx;
  background: var(--bg-card);
  border-radius: 24rpx;
  box-shadow: var(--shadow-card);
  padding: 16rpx 20rpx;
  display: flex;
  align-items: center;
  gap: 16rpx;
}
.search-row {
  flex: 1;
  display: flex;
  align-items: center;
  background: var(--bg-input);
  border-radius: 20rpx;
  padding: 16rpx 20rpx;
}
.search-icon {
  font-size: 28rpx;
  margin-right: 12rpx;
  opacity: 0.5;
}
.search-input {
  flex: 1;
  font-size: 28rpx;
  color: var(--text-primary);
}
.search-placeholder {
  color: var(--text-muted);
}
.search-clear {
  padding: 8rpx;
  color: var(--text-muted);
}
.search-btn {
  background: var(--accent-dark);
  color: var(--text-inverse);
  border-radius: 20rpx;
  padding: 16rpx 32rpx;
  font-size: 28rpx;
  font-weight: 600;
  display: flex;
  align-items: center;
}
.search-btn:active { opacity: 0.7; }

/* 后续部分样式（保持原样，仅替换颜色为 tokens） */
```

- [ ] **Step 3: 提交**

```bash
git add miniprogram/pages/index/index.wxml miniprogram/pages/index/index.wxss
git commit -m "feat(p2): 首页顶部品牌区 + 搜索框视觉升级（明亮日间风）"
```

---

## Task 3: 首页 - AI 裁判入口（深底横幅 + 金色图标）

**Files:**
- Modify: `miniprogram/pages/index/index.wxml`
- Modify: `miniprogram/pages/index/index.wxss`

- [ ] **Step 1: 修改 WXML 的 AI 裁判区块（line 12-23）**

在 `miniprogram/pages/index/index.wxml` 中，AI 裁判区块改为：

```xml
<!-- AI 裁判入口 - 深底横幅 + 金色图标 -->
<view class="ai-banner" wx:if="{{showAIJudgeCard && !keyword && !hiddenCards.aiJudge}}" bindtap="goToAIJudge">
  <view class="ai-icon-block">
    <image class="ai-icon" src="/images/mtgask_logo.png" mode="aspectFit"></image>
  </view>
  <view class="ai-info">
    <text class="ai-title">AI 裁判</text>
    <text class="ai-desc">智能规则问答 · 随时随地</text>
  </view>
  <text class="ai-arrow">›</text>
</view>
```

- [ ] **Step 2: 添加 AI 横幅样式**

在 `miniprogram/pages/index/index.wxss` 添加：

```css
/* AI 裁判横幅 */
.ai-banner {
  margin: 24rpx 32rpx;
  background: var(--accent-dark);
  color: var(--text-inverse);
  border-radius: 20rpx;
  padding: 24rpx;
  display: flex;
  align-items: center;
  gap: 20rpx;
  box-shadow: var(--shadow-card);
}
.ai-banner:active { opacity: 0.9; }
.ai-icon-block {
  width: 72rpx;
  height: 72rpx;
  background: var(--accent-gold);
  border-radius: 16rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.ai-icon {
  width: 40rpx;
  height: 40rpx;
}
.ai-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4rpx;
}
.ai-title {
  font-size: 32rpx;
  font-weight: 600;
  color: var(--text-inverse);
}
.ai-desc {
  font-size: 22rpx;
  color: rgba(255, 255, 255, 0.7);
}
.ai-arrow {
  font-size: 40rpx;
  color: rgba(255, 255, 255, 0.5);
  margin-left: auto;
}
```

- [ ] **Step 3: 提交**

```bash
git add miniprogram/pages/index/index.wxml miniprogram/pages/index/index.wxss
git commit -m "feat(p2): 首页 AI 裁判入口改深底横幅 + 金色图标"
```

---

## Task 4: 首页 - 工具入口（card-list-item 纵向列表）

**Files:**
- Modify: `miniprogram/pages/index/index.wxml`
- Modify: `miniprogram/pages/index/index.json`
- Modify: `miniprogram/pages/index/index.wxss`

- [ ] **Step 1: 修改 WXML 的工具入口区块**

在 `miniprogram/pages/index/index.wxml` 中，将原工具入口区块（Promo / 套牌 / Token / 生命值 / 骰子）替换为：

```xml
<!-- 工具入口 - 纵向列表（5 色图标色块） -->
<view class="tools-section" wx:if="{{!keyword}}">
  <view class="section-title-wrap">
    <text class="section-title">工具</text>
  </view>
  <view class="tools-card">
    <view class="tool-item" bindtap="goToToken">
      <view class="tool-icon-block" style="background-color: var(--color-blue);">
        <image class="tool-icon" src="{{toolIcons.token}}" mode="aspectFit"></image>
      </view>
      <view class="tool-info">
        <text class="tool-name">Token 生成器</text>
        <text class="tool-desc">衍生物卡片速查</text>
      </view>
      <image class="tool-chevron" src="{{toolIcons.chevron}}" mode="aspectFit"></image>
    </view>

    <view class="tool-divider"></view>

    <view class="tool-item" bindtap="goToDecks">
      <view class="tool-icon-block" style="background-color: var(--color-black);">
        <image class="tool-icon" src="{{toolIcons.deck}}" mode="aspectFit"></image>
      </view>
      <view class="tool-info">
        <text class="tool-name">我的套牌</text>
        <text class="tool-desc">导入导出 · 增删改查</text>
      </view>
      <image class="tool-chevron" src="{{toolIcons.chevron}}" mode="aspectFit"></image>
    </view>

    <view class="tool-divider"></view>

    <view class="tool-item" bindtap="goToCounter">
      <view class="tool-icon-block" style="background-color: var(--color-red);">
        <image class="tool-icon" src="{{toolIcons.heart}}" mode="aspectFit"></image>
      </view>
      <view class="tool-info">
        <text class="tool-name">生命值计数器</text>
        <text class="tool-desc">指挥官 · 2-4 人游戏</text>
      </view>
      <image class="tool-chevron" src="{{toolIcons.chevron}}" mode="aspectFit"></image>
    </view>

    <view class="tool-divider"></view>

    <view class="tool-item" bindtap="goToDice">
      <view class="tool-icon-block" style="background-color: var(--color-green);">
        <image class="tool-icon" src="{{toolIcons.dice}}" mode="aspectFit"></image>
      </view>
      <view class="tool-info">
        <text class="tool-name">骰子 & 随机</text>
        <text class="tool-desc">掷骰子 · 随机抽卡</text>
      </view>
      <image class="tool-chevron" src="{{toolIcons.chevron}}" mode="aspectFit"></image>
    </view>
  </view>
</view>
```

- [ ] **Step 2: 在 index.js 加载工具图标 data**

在 `miniprogram/pages/index/index.js` 的 `onLoad` 中添加：

```javascript
const iconUtil = require('../../utils/icon.js')

// ... 在 onLoad 末尾添加
this.setData({
  toolIcons: {
    token: iconUtil.getDataUrl('card', { color: '#ffffff' }),
    deck: iconUtil.getDataUrl('book', { color: '#ffffff' }),
    heart: iconUtil.getDataUrl('heart', { color: '#ffffff' }),
    dice: iconUtil.getDataUrl('dice', { color: '#ffffff' }),
    chevron: iconUtil.getDataUrl('chevron-right')
  }
})
```

- [ ] **Step 3: 添加工具列表样式**

在 `miniprogram/pages/index/index.wxss` 添加：

```css
/* 工具入口 - 纵向列表 */
.tools-section {
  margin: 32rpx;
}
.section-title-wrap {
  padding: 0 8rpx 16rpx;
}
.section-title {
  font-size: 28rpx;
  font-weight: 600;
  color: var(--text-primary);
}
.tools-card {
  background: var(--bg-card);
  border-radius: 20rpx;
  box-shadow: var(--shadow-card);
  overflow: hidden;
}
.tool-item {
  display: flex;
  align-items: center;
  gap: 24rpx;
  padding: 28rpx 24rpx;
}
.tool-item:active { background: var(--bg-input); }
.tool-divider {
  height: 1rpx;
  background: var(--border-subtle);
  margin: 0 24rpx;
}
.tool-icon-block {
  width: 68rpx;
  height: 68rpx;
  border-radius: 16rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.tool-icon {
  width: 36rpx;
  height: 36rpx;
}
.tool-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4rpx;
  min-width: 0;
}
.tool-name {
  font-size: 30rpx;
  font-weight: 600;
  color: var(--text-primary);
}
.tool-desc {
  font-size: 22rpx;
  color: var(--text-secondary);
}
.tool-chevron {
  width: 32rpx;
  height: 32rpx;
  opacity: 0.3;
  flex-shrink: 0;
}
```

- [ ] **Step 4: 提交**

```bash
git add miniprogram/pages/index/
git commit -m "feat(p2): 首页工具入口改纵向列表 + 5 色图标色块"
```

---

## Task 5: 首页 - 删除旧主题切换按钮 + 清理调试日志

**Files:**
- Modify: `miniprogram/pages/index/index.wxml`
- Modify: `miniprogram/pages/index/index.js`

- [ ] **Step 1: 删除 WXML 主题按钮**

删除 `miniprogram/pages/index/index.wxml` 中 line 9 的主题按钮：
```xml
    <view class="theme-btn" bindtap="toggleTheme">{{isLightTheme ? '🌙' : '☀️'}}</view>
```

- [ ] **Step 2: 清理 JS 调试日志**

```bash
sed -i '' '/console\.log.*CODEBUDDY_DEBUG/d' miniprogram/pages/index/index.js
grep -c CODEBUDDY_DEBUG miniprogram/pages/index/index.js
# Expected: 0
```

- [ ] **Step 3: 提交**

```bash
git add miniprogram/pages/index/
git commit -m "refactor(p2): 首页删除主题按钮 + 清理调试日志"
```

---

## Task 6: Token 页面视觉升级

**Files:**
- Modify: `miniprogram/pages/token/token.wxml`
- Modify: `miniprogram/pages/token/token.wxss`
- Modify: `miniprogram/pages/token/token.js`

- [ ] **Step 1: 简化 WXML（保留功能性，精简结构）**

替换 `miniprogram/pages/token/token.wxml`：

```xml
<view class="container">
  <view class="nav-bar">
    <view class="back-btn" bindtap="goBack">‹</view>
    <text class="nav-title">Token 列表</text>
  </view>

  <!-- 搜索 -->
  <view class="search-card">
    <view class="search-row">
      <text class="search-icon">🔍</text>
      <input
        class="search-input"
        placeholder="输入英文 Token 名"
        placeholder-class="search-placeholder"
        bindinput="onSearchInput"
        value="{{searchQuery}}"
      />
    </view>
    <view class="search-btn" bindtap="onSearch">搜索</view>
  </view>

  <!-- 加载中 -->
  <view class="loading" wx:if="{{loading}}">
    <view class="loading-spinner"></view>
    <text class="loading-text">加载中...</text>
  </view>

  <!-- 搜索结果 -->
  <view class="results" wx:if="{{showSearchResults && !loading}}">
    <view wx:if="{{searchResults.length === 0}}" class="empty-hint">
      <text>未找到结果</text>
    </view>
    <view class="result-list" wx:else>
      <view class="result-card" wx:for="{{searchResults}}" wx:key="id" bindtap="onSelectToken" data-item="{{item}}">
        <view class="result-name">{{item.name}}</view>
        <view class="result-meta">{{item.type_line || ''}}</view>
      </view>
    </view>
  </view>

  <!-- 默认按颜色分组列表 -->
  <view class="token-groups" wx:if="{{!showSearchResults && !loading}}">
    <view class="group" wx:for="{{tokenGroupList}}" wx:key="color" wx:for-item="group">
      <view class="group-header">
        <view class="color-dot" style="background-color: {{group.color}};"></view>
        <text class="group-name">{{group.name}}</text>
        <text class="group-count">{{group.tokens.length}}</text>
      </view>
      <view class="token-list">
        <view class="token-item" wx:for="{{group.tokens}}" wx:key="name" bindtap="onTokenTap" data-token="{{item}}">
          <text class="token-name">{{item.name}}</text>
          <text class="token-type">{{item.power}}/{{item.toughness}}</text>
        </view>
      </view>
    </view>
  </view>
</view>
```

- [ ] **Step 2: 重置 token.wxss（明亮日间风）**

完整替换 `miniprogram/pages/token/token.wxss`：

```css
/* pages/token/token.wxss */
page {
  background: var(--bg-page);
}
.container {
  min-height: 100vh;
  padding: 24rpx 32rpx;
}
.nav-bar {
  display: flex;
  align-items: center;
  padding: 16rpx 0 32rpx;
  background: var(--bg-page);
}
.back-btn {
  width: 64rpx;
  height: 64rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 48rpx;
  color: var(--text-primary);
  margin-right: 16rpx;
}
.back-btn:active { opacity: 0.5; }
.nav-title {
  font-size: 36rpx;
  font-weight: 700;
  color: var(--text-primary);
}

/* 搜索卡 */
.search-card {
  background: var(--bg-card);
  border-radius: 24rpx;
  box-shadow: var(--shadow-card);
  padding: 16rpx 20rpx;
  display: flex;
  align-items: center;
  gap: 16rpx;
  margin-bottom: 32rpx;
}
.search-row {
  flex: 1;
  display: flex;
  align-items: center;
  background: var(--bg-input);
  border-radius: 20rpx;
  padding: 16rpx 20rpx;
}
.search-icon { font-size: 28rpx; margin-right: 12rpx; opacity: 0.5; }
.search-input { flex: 1; font-size: 28rpx; color: var(--text-primary); }
.search-placeholder { color: var(--text-muted); }
.search-btn {
  background: var(--accent-dark);
  color: var(--text-inverse);
  border-radius: 20rpx;
  padding: 16rpx 32rpx;
  font-size: 28rpx;
  font-weight: 600;
}
.search-btn:active { opacity: 0.7; }

/* 加载 */
.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 80rpx 0;
}
.loading-spinner {
  width: 48rpx;
  height: 48rpx;
  border: 4rpx solid var(--bg-input);
  border-top-color: var(--accent-dark);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.loading-text {
  font-size: 24rpx;
  color: var(--text-secondary);
  margin-top: 16rpx;
}

/* 搜索结果 */
.results { padding: 16rpx 0; }
.empty-hint {
  text-align: center;
  padding: 60rpx 0;
  color: var(--text-muted);
  font-size: 28rpx;
}
.result-list { display: flex; flex-direction: column; gap: 16rpx; }
.result-card {
  background: var(--bg-card);
  border-radius: 16rpx;
  box-shadow: var(--shadow-card);
  padding: 20rpx 24rpx;
}
.result-card:active { opacity: 0.7; }
.result-name {
  font-size: 30rpx;
  font-weight: 600;
  color: var(--text-primary);
}
.result-meta {
  font-size: 22rpx;
  color: var(--text-secondary);
  margin-top: 4rpx;
}

/* Token 分组 */
.token-groups { display: flex; flex-direction: column; gap: 32rpx; }
.group {
  background: var(--bg-card);
  border-radius: 20rpx;
  box-shadow: var(--shadow-card);
  padding: 20rpx 24rpx;
}
.group-header {
  display: flex;
  align-items: center;
  gap: 12rpx;
  padding: 8rpx 0 16rpx;
  border-bottom: 1rpx solid var(--border-subtle);
  margin-bottom: 16rpx;
}
.color-dot {
  width: 24rpx;
  height: 24rpx;
  border-radius: 50%;
}
.group-name {
  font-size: 30rpx;
  font-weight: 600;
  color: var(--text-primary);
  flex: 1;
}
.group-count {
  font-size: 22rpx;
  color: var(--text-muted);
  background: var(--bg-input);
  padding: 4rpx 12rpx;
  border-radius: 12rpx;
}
.token-list { display: flex; flex-direction: column; gap: 8rpx; }
.token-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16rpx 12rpx;
  border-radius: 12rpx;
}
.token-item:active { background: var(--bg-input); }
.token-name { font-size: 28rpx; color: var(--text-primary); }
.token-type {
  font-size: 24rpx;
  color: var(--text-secondary);
  font-weight: 600;
}
```

- [ ] **Step 3: 清理 token.js 调试日志 + 添加返回方法**

修改 `miniprogram/pages/token/token.js`：

```bash
sed -i '' '/console\.log.*CODEBUDDY_DEBUG/d' miniprogram/pages/token/token.js
```

在 Page 末尾添加：
```javascript
goBack() {
  wx.navigateBack({ fail: () => wx.redirectTo({ url: '/pages/index/index' }) })
}
```

- [ ] **Step 4: 提交**

```bash
git add miniprogram/pages/token/
git commit -m "feat(p2): Token 页面视觉升级（明亮日间风）"
```

---

## Task 7: Token 生成器页面视觉升级

**Files:**
- Modify: `miniprogram/pages/token-generate/token-generate.wxml`
- Modify: `miniprogram/pages/token-generate/token-generate.wxss`
- Modify: `miniprogram/pages/token-generate/token-generate.js`

- [ ] **Step 1: 重置 WXML**

完整替换 `miniprogram/pages/token-generate/token-generate.wxml`：

```xml
<view class="container">
  <view class="nav-bar">
    <view class="back-btn" bindtap="goBack">‹</view>
    <text class="nav-title">Token 生成器</text>
  </view>

  <!-- 颜色选择 -->
  <view class="color-picker">
    <text class="section-title">选择颜色</text>
    <view class="color-list">
      <view
        wx:for="{{colors}}"
        wx:key="key"
        class="color-item {{selectedColor === item.key ? 'active' : ''}}"
        style="background-color: {{item.color}};"
        bindtap="onSelectColor"
        data-color="{{item.key}}"
      >
        <text class="color-name">{{item.name}}</text>
      </view>
    </view>
  </view>

  <!-- Token 列表 -->
  <view class="token-list">
    <view class="token-card" wx:for="{{tokens}}" wx:key="name">
      <view class="token-stats">
        <text class="token-pt">{{item.power}}/{{item.toughness}}</text>
      </view>
      <view class="token-info">
        <text class="token-name">{{item.name}}</text>
        <text class="token-type">{{item.typeLine || 'Token'}}</text>
        <text wx:if="{{item.abilities}}" class="token-abilities">{{item.abilities}}</text>
      </view>
    </view>
    <view wx:if="{{tokens.length === 0}}" class="empty">
      <text>该颜色暂无 Token</text>
    </view>
  </view>
</view>
```

- [ ] **Step 2: 重置 WXSS**

完整替换 `miniprogram/pages/token-generate/token-generate.wxss`：

```css
/* pages/token-generate/token-generate.wxss */
page { background: var(--bg-page); }
.container { min-height: 100vh; padding: 24rpx 32rpx; }
.nav-bar { display: flex; align-items: center; padding: 16rpx 0 32rpx; }
.back-btn {
  width: 64rpx; height: 64rpx;
  display: flex; align-items: center; justify-content: center;
  font-size: 48rpx; color: var(--text-primary);
  margin-right: 16rpx;
}
.back-btn:active { opacity: 0.5; }
.nav-title { font-size: 36rpx; font-weight: 700; color: var(--text-primary); }

.section-title {
  font-size: 28rpx; font-weight: 600; color: var(--text-primary);
  margin-bottom: 16rpx;
  display: block;
}
.color-picker { margin-bottom: 32rpx; }
.color-list { display: flex; gap: 12rpx; flex-wrap: wrap; }
.color-item {
  flex: 1;
  min-width: 100rpx;
  padding: 20rpx 16rpx;
  border-radius: 16rpx;
  text-align: center;
  opacity: 0.5;
  transition: opacity 0.2s;
}
.color-item.active { opacity: 1; box-shadow: var(--shadow-card); }
.color-item:active { opacity: 0.7; }
.color-name {
  color: var(--text-inverse);
  font-size: 26rpx;
  font-weight: 600;
}

.token-list { display: flex; flex-direction: column; gap: 16rpx; }
.token-card {
  background: var(--bg-card);
  border-radius: 20rpx;
  box-shadow: var(--shadow-card);
  padding: 24rpx;
  display: flex;
  gap: 24rpx;
  align-items: center;
}
.token-stats {
  width: 100rpx; height: 100rpx;
  background: var(--bg-input);
  border-radius: 16rpx;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.token-pt {
  font-size: 28rpx; font-weight: 700; color: var(--text-primary);
}
.token-info { flex: 1; display: flex; flex-direction: column; gap: 4rpx; }
.token-name { font-size: 30rpx; font-weight: 600; color: var(--text-primary); }
.token-type { font-size: 22rpx; color: var(--text-secondary); }
.token-abilities { font-size: 22rpx; color: var(--text-muted); margin-top: 4rpx; }

.empty {
  text-align: center;
  padding: 60rpx 0;
  color: var(--text-muted);
  font-size: 28rpx;
}
```

- [ ] **Step 3: 简化 token-generate.js**

完整重写 `miniprogram/pages/token-generate/token-generate.js`（保留原有 token 数据逻辑，仅删除调试日志 + 适配新结构）：

```javascript
// pages/token-generate/token-generate.js
const app = getApp()

Page({
  data: {
    isLightTheme: true,
    colors: [
      { key: 'W', name: '白', color: '#f5f5f5' },
      { key: 'U', name: '蓝', color: '#3a7bc8' },
      { key: 'B', name: '黑', color: '#1a1a2e' },
      { key: 'R', name: '红', color: '#c83a3a' },
      { key: 'G', name: '绿', color: '#3a9b5c' }
    ],
    selectedColor: 'W',
    tokens: []
  },

  onLoad() {
    this.setData({ isLightTheme: true })
    this.loadTokens(this.data.selectedColor)
  },

  onShow() {
    this.setData({ isLightTheme: app.globalData.isLightTheme })
  },

  goBack() {
    wx.navigateBack({ fail: () => wx.redirectTo({ url: '/pages/index/index' }) })
  },

  onSelectColor(e) {
    const color = e.currentTarget.dataset.color
    this.setData({ selectedColor: color })
    this.loadTokens(color)
  },

  // 加载 Token 数据（保留原数据源逻辑）
  loadTokens(color) {
    // 从 data 文件加载（保留原有 token 列表数据）
    try {
      const data = require('./tokens-data.js')
      this.setData({ tokens: data[color] || [] })
    } catch (e) {
      this.setData({ tokens: [] })
    }
  }
})
```

注意：如果原项目没有 `tokens-data.js`，则保留原 token-generate.js 中的 token 列表数据（仅删除调试日志 + 添加 `goBack`、`onSelectColor` 方法）。

- [ ] **Step 4: 提交**

```bash
git add miniprogram/pages/token-generate/
git commit -m "feat(p2): Token 生成器页面视觉升级"
```

---

## Task 8: Decks 页面视觉升级

**Files:**
- Modify: `miniprogram/pages/decks/decks.wxml`
- Modify: `miniprogram/pages/decks/decks.wxss`
- Modify: `miniprogram/pages/decks/decks.js`

- [ ] **Step 1: 替换 decks.wxml 顶部 + 列表**

修改 `miniprogram/pages/decks/decks.wxml` 的导航 + 列表区块。完整替换 WXML：

```xml
<view class="container">
  <view class="nav-bar">
    <view class="back-btn" bindtap="goBack">‹</view>
    <text class="nav-title">我的套牌</text>
  </view>

  <!-- 加载 -->
  <view wx:if="{{loading}}" class="loading">
    <view class="loading-spinner"></view>
    <text class="loading-text">加载中...</text>
  </view>

  <!-- 空态 -->
  <view wx:elif="{{decks.length === 0}}" class="empty">
    <view class="empty-icon">📚</view>
    <text class="empty-title">还没有套牌</text>
    <text class="empty-desc">从 MTGGoldfish / Moxfield 导入或新建</text>
    <view class="empty-btn" bindtap="onAdd">新建套牌</view>
  </view>

  <!-- 套牌列表 -->
  <view wx:else class="deck-list">
    <view class="deck-card" wx:for="{{decks}}" wx:key="id" bindtap="onViewDeck" data-id="{{item.id}}">
      <view class="deck-info">
        <text class="deck-name">{{item.name}}</text>
        <text class="deck-meta">{{item.format || ''}} · {{item.cardCount || 0}} 张</text>
      </view>
      <view class="deck-actions">
        <view class="action-btn" catchtap="onEditDeck" data-id="{{item.id}}">编辑</view>
        <view class="action-btn danger" catchtap="onDeleteDeck" data-id="{{item.id}}">删除</view>
      </view>
    </view>

    <view class="add-btn" bindtap="onAdd">+ 新建套牌</view>
  </view>
</view>
```

- [ ] **Step 2: 重置 decks.wxss**

完整替换 `miniprogram/pages/decks/decks.wxss`：

```css
/* pages/decks/decks.wxss */
page { background: var(--bg-page); }
.container { min-height: 100vh; padding: 24rpx 32rpx; }
.nav-bar { display: flex; align-items: center; padding: 16rpx 0 32rpx; }
.back-btn {
  width: 64rpx; height: 64rpx;
  display: flex; align-items: center; justify-content: center;
  font-size: 48rpx; color: var(--text-primary);
  margin-right: 16rpx;
}
.back-btn:active { opacity: 0.5; }
.nav-title { font-size: 36rpx; font-weight: 700; color: var(--text-primary); }

.loading {
  display: flex; flex-direction: column; align-items: center; padding: 80rpx 0;
}
.loading-spinner {
  width: 48rpx; height: 48rpx;
  border: 4rpx solid var(--bg-input);
  border-top-color: var(--accent-dark);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.loading-text { font-size: 24rpx; color: var(--text-secondary); margin-top: 16rpx; }

.empty {
  display: flex; flex-direction: column; align-items: center; padding: 120rpx 0;
}
.empty-icon { font-size: 96rpx; opacity: 0.5; margin-bottom: 24rpx; }
.empty-title { font-size: 32rpx; font-weight: 600; color: var(--text-primary); }
.empty-desc { font-size: 24rpx; color: var(--text-secondary); margin-top: 8rpx; }
.empty-btn {
  margin-top: 32rpx;
  background: var(--accent-dark);
  color: var(--text-inverse);
  padding: 20rpx 48rpx;
  border-radius: 32rpx;
  font-size: 28rpx;
  font-weight: 600;
}
.empty-btn:active { opacity: 0.7; }

.deck-list { display: flex; flex-direction: column; gap: 16rpx; }
.deck-card {
  background: var(--bg-card);
  border-radius: 20rpx;
  box-shadow: var(--shadow-card);
  padding: 24rpx;
}
.deck-card:active { opacity: 0.7; }
.deck-info { margin-bottom: 16rpx; }
.deck-name { font-size: 30rpx; font-weight: 600; color: var(--text-primary); }
.deck-meta { font-size: 22rpx; color: var(--text-secondary); margin-top: 4rpx; display: block; }
.deck-actions { display: flex; gap: 12rpx; }
.action-btn {
  flex: 1;
  background: var(--bg-input);
  color: var(--text-primary);
  padding: 12rpx 0;
  border-radius: 12rpx;
  font-size: 24rpx;
  text-align: center;
}
.action-btn:active { opacity: 0.7; }
.action-btn.danger { color: var(--color-red); }

.add-btn {
  margin-top: 16rpx;
  background: var(--bg-card);
  border: 2rpx dashed var(--border-default);
  border-radius: 20rpx;
  padding: 28rpx;
  text-align: center;
  font-size: 28rpx;
  color: var(--text-secondary);
}
.add-btn:active { opacity: 0.7; }
```

- [ ] **Step 3: 清理 decks.js 调试日志 + 适配新事件**

```bash
sed -i '' '/console\.log.*CODEBUDDY_DEBUG/d' miniprogram/pages/decks/decks.js
```

在 Page 末尾添加：
```javascript
goBack() {
  wx.navigateBack({ fail: () => wx.redirectTo({ url: '/pages/index/index' }) })
}
```

并确保 `onViewDeck`, `onAdd`, `onEditDeck`, `onDeleteDeck` 方法存在（保留原方法）。

- [ ] **Step 4: 提交**

```bash
git add miniprogram/pages/decks/
git commit -m "feat(p2): Decks 页面视觉升级"
```

---

## Task 9: Deck Detail 页面视觉升级

**Files:**
- Modify: `miniprogram/pages/deck-detail/deck-detail.wxml`
- Modify: `miniprogram/pages/deck-detail/deck-detail.wxss`
- Modify: `miniprogram/pages/deck-detail/deck-detail.js`

- [ ] **Step 1: 重置 deck-detail.wxml**

完整替换：

```xml
<view class="container">
  <view class="nav-bar">
    <view class="back-btn" bindtap="goBack">‹</view>
    <text class="nav-title">{{deck.name || '套牌详情'}}</text>
  </view>

  <view wx:if="{{loading}}" class="loading">
    <view class="loading-spinner"></view>
    <text class="loading-text">加载中...</text>
  </view>

  <view wx:elif="{{!deck}}" class="empty">
    <text>套牌不存在或已删除</text>
  </view>

  <view wx:else class="deck-content">
    <view class="meta-card">
      <text class="meta-format">{{deck.format || 'Standard'}}</text>
      <text class="meta-count">{{deck.cardCount || 0}} 张</text>
    </view>

    <view class="cards-list">
      <view class="card-item" wx:for="{{deck.cards}}" wx:key="name">
        <text class="card-qty">{{item.quantity}}×</text>
        <text class="card-name">{{item.name}}</text>
        <text wx:if="{{item.cmc !== undefined}}" class="card-cmc">CMC {{item.cmc}}</text>
      </view>
    </view>
  </view>
</view>
```

- [ ] **Step 2: 重置 deck-detail.wxss**

完整替换：

```css
/* pages/deck-detail/deck-detail.wxss */
page { background: var(--bg-page); }
.container { min-height: 100vh; padding: 24rpx 32rpx; }
.nav-bar { display: flex; align-items: center; padding: 16rpx 0 32rpx; }
.back-btn {
  width: 64rpx; height: 64rpx;
  display: flex; align-items: center; justify-content: center;
  font-size: 48rpx; color: var(--text-primary);
  margin-right: 16rpx;
}
.back-btn:active { opacity: 0.5; }
.nav-title {
  font-size: 36rpx; font-weight: 700; color: var(--text-primary);
  flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}

.loading {
  display: flex; flex-direction: column; align-items: center; padding: 80rpx 0;
}
.loading-spinner {
  width: 48rpx; height: 48rpx;
  border: 4rpx solid var(--bg-input);
  border-top-color: var(--accent-dark);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.loading-text { font-size: 24rpx; color: var(--text-secondary); margin-top: 16rpx; }

.empty {
  text-align: center; padding: 80rpx 0;
  color: var(--text-muted); font-size: 28rpx;
}

.deck-content { display: flex; flex-direction: column; gap: 24rpx; }
.meta-card {
  background: var(--bg-card);
  border-radius: 20rpx;
  box-shadow: var(--shadow-card);
  padding: 24rpx;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.meta-format {
  font-size: 32rpx; font-weight: 600; color: var(--text-primary);
}
.meta-count {
  font-size: 22rpx; color: var(--text-secondary);
  background: var(--bg-input);
  padding: 6rpx 16rpx;
  border-radius: 12rpx;
}

.cards-list {
  background: var(--bg-card);
  border-radius: 20rpx;
  box-shadow: var(--shadow-card);
  overflow: hidden;
}
.card-item {
  display: flex;
  align-items: center;
  gap: 16rpx;
  padding: 20rpx 24rpx;
  border-bottom: 1rpx solid var(--border-subtle);
}
.card-item:last-child { border-bottom: none; }
.card-item:active { background: var(--bg-input); }
.card-qty {
  font-size: 24rpx; font-weight: 600; color: var(--text-secondary);
  min-width: 48rpx;
}
.card-name {
  flex: 1; font-size: 28rpx; color: var(--text-primary);
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.card-cmc {
  font-size: 22rpx; color: var(--text-muted);
  background: var(--bg-input);
  padding: 4rpx 12rpx;
  border-radius: 12rpx;
}
```

- [ ] **Step 3: 添加 deck-detail.js goBack**

修改 `miniprogram/pages/deck-detail/deck-detail.js`，在 Page 中添加：

```javascript
goBack() {
  wx.navigateBack({ fail: () => wx.redirectTo({ url: '/pages/decks/decks' }) })
}
```

- [ ] **Step 4: 提交**

```bash
git add miniprogram/pages/deck-detail/
git commit -m "feat(p2): Deck Detail 页面视觉升级"
```

---

## Task 10: Counter 页面视觉升级（生命值计数器）

**Files:**
- Modify: `miniprogram/pages/counter/counter.wxml`
- Modify: `miniprogram/pages/counter/counter.wxss`
- Modify: `miniprogram/pages/counter/counter.js`

- [ ] **Step 1: 重置 counter.wxml**

完整替换：

```xml
<view class="container">
  <view class="nav-bar">
    <view class="back-btn" bindtap="goToIndex">‹</view>
    <text class="nav-title">生命值计数器</text>
  </view>

  <!-- 赛制选择 -->
  <view class="format-tabs">
    <view
      wx:for="{{formats}}"
      wx:key="key"
      class="format-tab {{format === item.key ? 'active' : ''}}"
      bindtap="onSelectFormat"
      data-key="{{item.key}}"
    >
      {{item.name}}
    </view>
  </view>

  <!-- 玩家卡片 -->
  <view class="players">
    <view class="player-card" wx:for="{{players}}" wx:key="index">
      <text class="player-name">{{item.name}}</text>
      <text class="player-life">{{item.life}}</text>
      <view class="life-controls">
        <view class="life-btn minus" data-index="{{index}}" data-delta="-1" bindtap="adjustLife">-1</view>
        <view class="life-btn minus-big" data-index="{{index}}" data-delta="-5" bindtap="adjustLife">-5</view>
        <view class="life-btn plus-big" data-index="{{index}}" data-delta="5" bindtap="adjustLife">+5</view>
        <view class="life-btn plus" data-index="{{index}}" data-delta="1" bindtap="adjustLife">+1</view>
      </view>
    </view>
  </view>

  <!-- 操作按钮 -->
  <view class="actions">
    <view class="action-btn" bindtap="toggleMana" wx:if="{{format === 'solo'}}">
      {{showMana ? '隐藏' : '显示'}} 法力
    </view>
    <view class="action-btn primary" bindtap="resetAll">重置</view>
  </view>

  <!-- 法力池 -->
  <view wx:if="{{showMana && format === 'solo'}}" class="mana-pool">
    <text class="section-title">法力池</text>
    <view class="mana-list">
      <view
        wx:for="{{manaColors}}"
        wx:key="*this"
        class="mana-item mana-{{item}}"
      >
        <text class="mana-key">{{item}}</text>
        <text class="mana-qty">{{manaPool[item]}}</text>
        <view class="mana-controls">
          <view class="mana-btn" data-color="{{item}}" data-delta="-1" bindtap="adjustMana">-</view>
          <view class="mana-btn" data-color="{{item}}" data-delta="1" bindtap="adjustMana">+</view>
        </view>
      </view>
    </view>
  </view>
</view>
```

- [ ] **Step 2: 重置 counter.wxss**

完整替换：

```css
/* pages/counter/counter.wxss */
page { background: var(--bg-page); }
.container { min-height: 100vh; padding: 24rpx 32rpx 120rpx; }
.nav-bar { display: flex; align-items: center; padding: 16rpx 0 32rpx; }
.back-btn {
  width: 64rpx; height: 64rpx;
  display: flex; align-items: center; justify-content: center;
  font-size: 48rpx; color: var(--text-primary);
  margin-right: 16rpx;
}
.back-btn:active { opacity: 0.5; }
.nav-title { font-size: 36rpx; font-weight: 700; color: var(--text-primary); }

/* 赛制选择 */
.format-tabs {
  display: flex;
  background: var(--bg-card);
  border-radius: 20rpx;
  box-shadow: var(--shadow-card);
  padding: 8rpx;
  margin-bottom: 32rpx;
  gap: 8rpx;
}
.format-tab {
  flex: 1;
  text-align: center;
  padding: 16rpx 0;
  font-size: 26rpx;
  color: var(--text-secondary);
  border-radius: 16rpx;
}
.format-tab.active {
  background: var(--accent-dark);
  color: var(--text-inverse);
  font-weight: 600;
}

/* 玩家 */
.players { display: flex; flex-direction: column; gap: 24rpx; }
.player-card {
  background: var(--bg-card);
  border-radius: 24rpx;
  box-shadow: var(--shadow-card);
  padding: 32rpx 24rpx;
  text-align: center;
}
.player-name {
  font-size: 26rpx;
  color: var(--text-secondary);
  margin-bottom: 16rpx;
}
.player-life {
  font-size: 120rpx;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1;
  margin-bottom: 24rpx;
  font-family: var(--font-family);
}
.life-controls { display: flex; gap: 12rpx; }
.life-btn {
  flex: 1;
  padding: 20rpx 0;
  border-radius: 16rpx;
  font-size: 28rpx;
  font-weight: 600;
  background: var(--bg-input);
  color: var(--text-primary);
}
.life-btn:active { opacity: 0.7; }
.life-btn.plus, .life-btn.plus-big { background: var(--color-green); color: var(--text-inverse); }
.life-btn.minus, .life-btn.minus-big { background: var(--color-red); color: var(--text-inverse); }

/* 操作 */
.actions { display: flex; gap: 16rpx; margin-top: 32rpx; }
.action-btn {
  flex: 1;
  text-align: center;
  background: var(--bg-card);
  border-radius: 16rpx;
  padding: 24rpx;
  font-size: 28rpx;
  color: var(--text-primary);
  box-shadow: var(--shadow-card);
}
.action-btn.primary { background: var(--accent-dark); color: var(--text-inverse); font-weight: 600; }
.action-btn:active { opacity: 0.7; }

/* 法力池 */
.mana-pool { margin-top: 32rpx; }
.section-title {
  font-size: 28rpx; font-weight: 600; color: var(--text-primary);
  margin-bottom: 16rpx; display: block;
}
.mana-list {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16rpx;
}
.mana-item {
  background: var(--bg-card);
  border-radius: 16rpx;
  box-shadow: var(--shadow-card);
  padding: 20rpx;
  text-align: center;
}
.mana-key { font-size: 36rpx; font-weight: 700; }
.mana-qty { font-size: 32rpx; color: var(--text-primary); margin: 8rpx 0; display: block; }
.mana-controls { display: flex; gap: 8rpx; }
.mana-btn {
  flex: 1;
  padding: 8rpx 0;
  background: var(--bg-input);
  border-radius: 8rpx;
  font-size: 24rpx;
  color: var(--text-primary);
}
.mana-btn:active { opacity: 0.7; }
.mana-W .mana-key { color: #f5d76e; }
.mana-U .mana-key { color: #3a7bc8; }
.mana-B .mana-key { color: #1a1a2e; }
.mana-R .mana-key { color: #c83a3a; }
.mana-G .mana-key { color: #3a9b5c; }
.mana-C .mana-key { color: #999; }
```

- [ ] **Step 3: 适配 counter.js**

在 Page 中添加 `onSelectFormat` 方法：

```javascript
onSelectFormat(e) {
  const key = e.currentTarget.dataset.key
  this.setData({ format: key })
  this.initPlayers()
}
```

并将 `adjustLife` / `adjustMana` 改为从 dataset 读取：

```javascript
adjustLife(e) {
  const { index, delta } = e.currentTarget.dataset
  const players = this.data.players
  players[index].life += parseInt(delta)
  if (players[index].life < 0) players[index].life = 0
  this.setData({ players })
},

adjustMana(e) {
  const { color, delta } = e.currentTarget.dataset
  const manaPool = { ...this.data.manaPool }
  manaPool[color] += parseInt(delta)
  if (manaPool[color] < 0) manaPool[color] = 0
  this.setData({ manaPool })
}
```

并把 `setFormat` 改为包装：

```javascript
setFormat(e) {
  // 兼容旧 picker
  this.onSelectFormat({ currentTarget: { dataset: { key: this.data.formats[e.detail.value].key } } })
}
```

- [ ] **Step 4: 提交**

```bash
git add miniprogram/pages/counter/
git commit -m "feat(p2): Counter 页面视觉升级（明亮日间风）"
```

---

## Task 11: Dice 页面视觉升级

**Files:**
- Modify: `miniprogram/pages/dice/dice.wxml`
- Modify: `miniprogram/pages/dice/dice.wxss`
- Modify: `miniprogram/pages/dice/dice.js`

- [ ] **Step 1: 重置 dice.wxml**

完整替换：

```xml
<view class="container">
  <view class="nav-bar">
    <view class="back-btn" bindtap="goToIndex">‹</view>
    <text class="nav-title">骰子 & 随机</text>
  </view>

  <!-- 骰子类型选择 -->
  <view class="dice-tabs">
    <view
      wx:for="{{diceOptions}}"
      wx:key="value"
      class="dice-tab {{selectedDice === item.value && !isCustom ? 'active' : ''}}"
      bindtap="selectDice"
      data-value="{{item.value}}"
    >
      {{item.label}}
    </view>
  </view>

  <!-- 自定义 -->
  <view class="custom-card">
    <view class="custom-row">
      <text class="custom-label">自定义面数</text>
      <input
        type="number"
        class="custom-input"
        value="{{customSides}}"
        bindinput="inputCustomSides"
        bindtap="toggleCustom"
      />
    </view>
  </view>

  <!-- 骰子结果 -->
  <view class="dice-display">
    <text wx:if="{{diceResult !== null}}" class="dice-result">{{diceResult}}</text>
    <text wx:else class="dice-placeholder">点击掷骰</text>
  </view>

  <view class="roll-btn {{isRolling ? 'rolling' : ''}}" bindtap="rollDice">
    {{isRolling ? '掷骰中...' : '掷骰子'}}
  </view>

  <!-- 丢硬币 -->
  <view class="coin-section">
    <text class="section-title">丢硬币</text>
    <view class="coin-display">
      <text wx:if="{{coinResult}}" class="coin-result">{{coinResult}}</text>
      <text wx:else class="coin-placeholder">点击丢币</text>
    </view>
    <view class="roll-btn secondary {{coinAnimating ? 'rolling' : ''}}" bindtap="flipCoin">
      {{coinAnimating ? '旋转中...' : '丢硬币'}}
    </view>
  </view>
</view>
```

- [ ] **Step 2: 重置 dice.wxss**

完整替换：

```css
/* pages/dice/dice.wxss */
page { background: var(--bg-page); }
.container { min-height: 100vh; padding: 24rpx 32rpx 80rpx; }
.nav-bar { display: flex; align-items: center; padding: 16rpx 0 32rpx; }
.back-btn {
  width: 64rpx; height: 64rpx;
  display: flex; align-items: center; justify-content: center;
  font-size: 48rpx; color: var(--text-primary);
  margin-right: 16rpx;
}
.back-btn:active { opacity: 0.5; }
.nav-title { font-size: 36rpx; font-weight: 700; color: var(--text-primary); }

.dice-tabs {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12rpx;
  margin-bottom: 24rpx;
}
.dice-tab {
  background: var(--bg-card);
  border-radius: 16rpx;
  padding: 20rpx 0;
  text-align: center;
  font-size: 28rpx;
  font-weight: 600;
  color: var(--text-secondary);
  box-shadow: var(--shadow-card);
}
.dice-tab.active {
  background: var(--accent-dark);
  color: var(--text-inverse);
}
.dice-tab:active { opacity: 0.7; }

.custom-card {
  background: var(--bg-card);
  border-radius: 20rpx;
  box-shadow: var(--shadow-card);
  padding: 24rpx;
  margin-bottom: 32rpx;
}
.custom-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16rpx;
}
.custom-label { font-size: 28rpx; color: var(--text-primary); }
.custom-input {
  background: var(--bg-input);
  border-radius: 12rpx;
  padding: 16rpx 20rpx;
  font-size: 28rpx;
  color: var(--text-primary);
  width: 200rpx;
  text-align: center;
}

.dice-display {
  background: var(--bg-card);
  border-radius: 24rpx;
  box-shadow: var(--shadow-card);
  padding: 60rpx 32rpx;
  text-align: center;
  margin-bottom: 32rpx;
}
.dice-result {
  font-size: 160rpx;
  font-weight: 700;
  color: var(--accent-dark);
  line-height: 1;
  font-family: var(--font-family);
}
.dice-placeholder {
  font-size: 32rpx;
  color: var(--text-muted);
}

.roll-btn {
  background: var(--accent-dark);
  color: var(--text-inverse);
  border-radius: 24rpx;
  padding: 28rpx;
  text-align: center;
  font-size: 32rpx;
  font-weight: 600;
  box-shadow: var(--shadow-card);
}
.roll-btn:active { opacity: 0.7; }
.roll-btn.rolling {
  background: var(--text-muted);
}
.roll-btn.secondary {
  background: var(--bg-card);
  color: var(--text-primary);
  border: 1rpx solid var(--border-default);
}

.coin-section {
  margin-top: 48rpx;
  background: var(--bg-card);
  border-radius: 24rpx;
  box-shadow: var(--shadow-card);
  padding: 32rpx;
}
.section-title {
  font-size: 28rpx; font-weight: 600; color: var(--text-primary);
  margin-bottom: 24rpx; display: block;
}
.coin-display {
  text-align: center;
  padding: 32rpx;
  margin-bottom: 24rpx;
  background: var(--bg-input);
  border-radius: 16rpx;
}
.coin-result {
  font-size: 64rpx;
  font-weight: 700;
  color: var(--accent-dark);
}
.coin-placeholder {
  font-size: 24rpx;
  color: var(--text-muted);
}
```

- [ ] **Step 3: 修改 dice.js selectDice/toggleCustom 以接受 data-value**

保持 `selectDice`, `toggleCustom`, `inputCustomSides`, `rollDice`, `flipCoin`, `goToIndex` 方法不变（数据结构和事件都符合 WXML 期望）。

- [ ] **Step 4: 提交**

```bash
git add miniprogram/pages/dice/
git commit -m "feat(p2): Dice 页面视觉升级"
```

---

## Task 12: 整体验证 + 真机测试

**Files:**
- Modify: 无（仅验证）

- [ ] **Step 1: 重新截屏所有 7 个页面**

在微信开发者工具中：
1. 首页：检查 brand 区 + 搜索卡 + AI 横幅 + 工具纵向列表 + 系列资讯
2. token：检查分组列表
3. token-generate：检查颜色选择 + token 列表
4. decks：检查空态 vs 列表态
5. deck-detail：检查 meta + 卡牌列表
6. counter：检查 1v1/commander tabs + 生命值按钮
7. dice：检查骰子类型 + 结果

- [ ] **Step 2: 验证空/加载/错误态**

- 清空网络 → 访问 decks → 看到空态
- 访问 token → 看到 loading
- 故意搜索不存在关键词 → 看到空态

- [ ] **Step 3: 主题锁定验证**

- 首页不应看到主题切换按钮
- 在设置中改 `app.js` 的 `lightOnly = false` 应无效（toggleTheme 锁定为 true）

- [ ] **Step 4: iOS / Android 真机测试**

用微信开发者工具扫码真机调试：
- iPhone 真机：首页 + 工具页 + counter 实际交互
- Android 真机：同上

- [ ] **Step 5: 提交验收报告（可选）**

如果发现 P2 阶段 bug，记录到 `docs/superpowers/specs/2026-07-14-p2-known-issues.md`，否则此步可跳过。

---

## Task 13: 合并 P2 到 main + 推送

- [ ] **Step 1: 切换到 main**

```bash
git checkout main
git pull origin main
```

- [ ] **Step 2: 合并 dev（dev 已含 P2）**

```bash
git merge dev --no-ff -m "merge: P2 首页+工具页视觉升级（11 任务）"
```

如果有冲突，按 P1 经验逐个解决（一般不会冲突，因为 P1 已经在 main）。

- [ ] **Step 3: 推送**

```bash
git push origin main
git push origin dev
```

---

## P2 验收清单

- [ ] 首页：brand + 搜索 + AI 横幅 + 工具纵向列表 + 5 色色块
- [ ] token：颜色分组 + 搜索
- [ ] token-generate：5 色选择 + token 卡片
- [ ] decks：空态 + 列表 + 增删
- [ ] deck-detail：meta + 卡牌列表
- [ ] counter：1v1/commander tabs + 大数字生命值 + 4 按钮控制
- [ ] dice：D4-D20 tabs + 自定义 + 掷骰动画 + 丢硬币
- [ ] 暗色主题切换入口在所有页面已隐藏
- [ ] 空/加载/错误态在所有页面统一
- [ ] iOS / Android 真机各验证一次
- [ ] 控制台无 error/warning
- [ ] 7 个页面无遗留 `console.log("CODEBUDDY_DEBUG")`

---

## 下一步

P2 完成后，按相同模式生成 P3 plan（核心交互页：search、card、rule、keyword、agent）：
- 文档：`docs/superpowers/plans/2026-07-14-miniprogram-p3-core-pages.md`
- 重点：在 P2 基础上重做暗色主题（spec 1.4 计划）

P3 完成后是 P4 剩余页（8 个）。