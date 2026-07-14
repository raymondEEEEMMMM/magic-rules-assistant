# mtgAsk 小程序前端 P4 剩余页 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 迁移最后 8 个页面至设计系统（明亮日间风 + 暗色主题支持），完成全量 UI/UX 升级。

**Architecture:** 沿用 P1-P3 模式 — 替换 WXSS 为 token 化样式 + 应用 root container `theme-dark` class binding + 添加 `updateTheme` 方法 + 清理调试日志。

**Tech Stack:** 微信原生小程序 + P1 设计系统 + 已有的 P2/P3 视觉模式

**依赖 spec：** `docs/superpowers/specs/2026-07-14-miniprogram-frontend-optimization-design.md` 第 6.4 节

**P1-P3 状态：** 已完成（`868f31a` on main）

---

## 文件结构

**修改**（8 个页面，每页 3-4 个文件）：
- `miniprogram/pages/setcards/*` — 系列卡牌列表
- `miniprogram/pages/sldcards/*` — Secret Lair 专区
- `miniprogram/pages/promos/*` — Promo 卡快讯
- `miniprogram/pages/feedback/*` — 反馈表单
- `miniprogram/pages/devlog/*` — 开发日志
- `miniprogram/pages/apitest/*` — API 测试
- `miniprogram/pages/loading/*` — 加载页
- `miniprogram/pages/odds/*` — 概率计算

---

## 共用模式（每个页面都执行）

每个 P4 页面都执行以下 4 个改动：

### A. WXML 改动
- 根 `<view class="container">` 添加 `{{isLightTheme ? '' : 'theme-dark'}}` class binding
- 添加返回按钮（如果还没有）
- 重命名为新设计结构（如 nav-bar 统一）

### B. WXSS 改动
- 完整替换为 token 化明亮日间风
- 使用 `var(--bg-page)`, `var(--bg-card)`, `var(--text-primary)`, `var(--accent-dark)`, `var(--shadow-card)` 等

### C. JS 改动
- 添加 `updateTheme(isLight)` 方法
- 移除硬编码 `setData({isLightTheme: true})`，改为从 `app.globalData.isLightTheme` 读取
- 清理 `CODEBUDDY_DEBUG` 调试日志
- 添加 `goBack()` 方法（如果还没有）

### D. JSON 改动（如需要）
- 添加 `usingComponents` 引用（`empty-state`, `tag-chip` 等）

---

## Task 1: Setcards 页面（系列卡牌列表）

**Files:**
- Modify: `miniprogram/pages/setcards/setcards.wxml`
- Modify: `miniprogram/pages/setcards/setcards.wxss`
- Modify: `miniprogram/pages/setcards/setcards.js`
- Modify: `miniprogram/pages/setcards/setcards.json`

- [ ] **Step 1: 读 setcards.js 了解所有 data 字段**

Read `setcards.js` to see data fields: `setCode`, `setName`, `cards[]`, `loading`, `currentPage`, `hasMore`, etc.

- [ ] **Step 2: setcards.json**

```json
{
  "navigationBarTitleText": "{{setName || '系列卡牌'}}",
  "usingComponents": {
    "empty-state": "/components/empty-state/empty-state"
  }
}
```

- [ ] **Step 3: setcards.wxml** — full replacement:

```xml
<view class="container {{isLightTheme ? '' : 'theme-dark'}}">
  <view class="nav-bar">
    <view class="back-btn" bindtap="goBack">‹</view>
    <text class="nav-title">{{setName || '系列卡牌'}}</text>
  </view>

  <view wx:if="{{loading && cards.length === 0}}" class="loading">
    <view class="loading-spinner"></view>
    <text class="loading-text">加载中...</text>
  </view>

  <view wx:else>
    <!-- 网格视图 -->
    <view class="card-grid">
      <view
        wx:for="{{cards}}"
        wx:key="id"
        class="grid-card"
        bindtap="onCardTap"
        data-id="{{item.id}}"
      >
        <image
          wx:if="{{item.image_uris && item.image_uris.normal}}"
          class="grid-card-image"
          src="{{item.image_uris.normal}}"
          mode="aspectFit"
        />
        <view wx:else class="grid-card-placeholder">
          <text>{{item.name || item.zhs_name}}</text>
        </view>
        <text class="grid-card-name">{{item.zhs_name || item.name}}</text>
        <text wx:if="{{item.mana_cost}}" class="grid-card-mana">{{item.mana_cost}}</text>
      </view>
    </view>

    <!-- 加载更多 -->
    <view wx:if="{{loading}}" class="loading-more">
      <text>加载中...</text>
    </view>
    <view wx:elif="{{!hasMore && cards.length > 0}}" class="no-more">
      <text>— 没有更多了 —</text>
    </view>

    <!-- 空态 -->
    <empty-state wx:if="{{!loading && cards.length === 0}}" icon="search" title="未找到卡牌" desc="该系列暂无卡牌数据" />
  </view>
</view>
```

- [ ] **Step 4: setcards.wxss** — full replacement:

```css
/* pages/setcards/setcards.wxss */
page { background: var(--bg-page); }
.container { min-height: 100vh; padding: 24rpx 32rpx; }
.nav-bar { display: flex; align-items: center; padding: 16rpx 0 24rpx; }
.back-btn { width: 64rpx; height: 64rpx; display: flex; align-items: center; justify-content: center; font-size: 48rpx; color: var(--text-primary); margin-right: 16rpx; }
.back-btn:active { opacity: 0.5; }
.nav-title { font-size: 32rpx; font-weight: 700; color: var(--text-primary); flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.loading { display: flex; flex-direction: column; align-items: center; padding: 120rpx 0; }
.loading-spinner { width: 48rpx; height: 48rpx; border: 4rpx solid var(--bg-input); border-top-color: var(--accent-dark); border-radius: 50%; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.loading-text { font-size: 24rpx; color: var(--text-secondary); margin-top: 16rpx; }

.card-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16rpx; }
.grid-card { background: var(--bg-card); border-radius: 12rpx; box-shadow: var(--shadow-card); padding: 12rpx; display: flex; flex-direction: column; }
.grid-card:active { opacity: 0.7; }
.grid-card-image { width: 100%; aspect-ratio: 5/7; height: auto; border-radius: 8rpx; }
.grid-card-placeholder { width: 100%; aspect-ratio: 5/7; background: var(--bg-input); border-radius: 8rpx; display: flex; align-items: center; justify-content: center; font-size: 22rpx; color: var(--text-muted); padding: 16rpx; text-align: center; }
.grid-card-name { font-size: 22rpx; color: var(--text-primary); margin-top: 8rpx; text-align: center; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.grid-card-mana { font-size: 18rpx; color: var(--accent-dark); font-family: monospace; text-align: center; margin-top: 2rpx; }

.loading-more { text-align: center; padding: 32rpx; color: var(--text-secondary); font-size: 24rpx; }
.no-more { text-align: center; padding: 32rpx; color: var(--text-muted); font-size: 22rpx; }
```

- [ ] **Step 5: setcards.js** — clean logs + add methods:

```bash
sed -i '' '/console\.log.*CODEBUDDY_DEBUG/d' miniprogram/pages/setcards/setcards.js
```

Add `goBack` and `updateTheme` methods:

```javascript
goBack() {
  wx.navigateBack({ fail: () => wx.redirectTo({ url: '/pages/index/index' }) })
},

updateTheme(isLight) {
  this.setData({ isLightTheme: isLight })
}
```

If existing has `setData({isLightTheme: true})` in onLoad or onShow, change to:
```javascript
this.setData({ isLightTheme: app.globalData.isLightTheme })
```

- [ ] **Step 6: 提交**

```bash
git add miniprogram/pages/setcards/
git commit -m "feat(p4): Setcards 页面视觉升级"
```

---

## Task 2: SLDCards 页面（Secret Lair 专区）

**Files:**
- Modify: `miniprogram/pages/sldcards/sldcards.wxml`
- Modify: `miniprogram/pages/sldcards/sldcards.wxss`
- Modify: `miniprogram/pages/sldcards/sldcards.js`
- Modify: `miniprogram/pages/sldcards/sldcards.json`

- [ ] **Step 1: 读 sldcards.js 了解 data 字段**

Read `sldcards.js`. Key fields: `groups[]` (each with `date`, `cards[]`).

- [ ] **Step 2: sldcards.json**

```json
{
  "navigationBarTitleText": "Secret Lair",
  "usingComponents": {
    "empty-state": "/components/empty-state/empty-state"
  }
}
```

- [ ] **Step 3: sldcards.wxml** — full replacement:

```xml
<view class="container {{isLightTheme ? '' : 'theme-dark'}}">
  <view class="nav-bar">
    <view class="back-btn" bindtap="goBack">‹</view>
    <text class="nav-title">Secret Lair 专区</text>
  </view>

  <view wx:if="{{loading}}" class="loading">
    <view class="loading-spinner"></view>
    <text class="loading-text">加载中...</text>
  </view>

  <view wx:elif="{{groups.length === 0 && !loading}}" class="empty-wrap">
    <empty-state icon="sparkle" title="暂无 Secret Lair" desc="稍后再来看看" />
  </view>

  <view wx:else class="groups">
    <view class="group" wx:for="{{groups}}" wx:key="date" wx:for-item="group">
      <view class="group-header">
        <text class="group-date">{{group.date}}</text>
        <text class="group-count">{{group.cards.length}} 张</text>
      </view>
      <scroll-view class="group-scroll" scroll-x enable-flex>
        <view class="card-list">
          <view class="card-item" wx:for="{{group.cards}}" wx:key="id" wx:for-item="card" bindtap="onCardTap" data-id="{{card.id}}">
            <image wx:if="{{card.image_url}}" class="card-image" src="{{card.image_url}}" mode="aspectFit" />
            <view wx:else class="card-placeholder">
              <text>{{card.name}}</text>
            </view>
            <text class="card-name">{{card.name}}</text>
          </view>
        </view>
      </scroll-view>
    </view>
  </view>
</view>
```

- [ ] **Step 4: sldcards.wxss** — full replacement:

```css
/* pages/sldcards/sldcards.wxss */
page { background: var(--bg-page); }
.container { min-height: 100vh; padding: 24rpx 32rpx; }
.nav-bar { display: flex; align-items: center; padding: 16rpx 0 24rpx; }
.back-btn { width: 64rpx; height: 64rpx; display: flex; align-items: center; justify-content: center; font-size: 48rpx; color: var(--text-primary); margin-right: 16rpx; }
.back-btn:active { opacity: 0.5; }
.nav-title { font-size: 36rpx; font-weight: 700; color: var(--text-primary); }

.loading { display: flex; flex-direction: column; align-items: center; padding: 120rpx 0; }
.loading-spinner { width: 48rpx; height: 48rpx; border: 4rpx solid var(--bg-input); border-top-color: var(--accent-dark); border-radius: 50%; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.loading-text { font-size: 24rpx; color: var(--text-secondary); margin-top: 16rpx; }

.empty-wrap { padding: 120rpx 0; }

.groups { display: flex; flex-direction: column; gap: 32rpx; }
.group { background: var(--bg-card); border-radius: 20rpx; box-shadow: var(--shadow-card); padding: 20rpx 24rpx; }
.group-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16rpx; }
.group-date { font-size: 28rpx; font-weight: 600; color: var(--text-primary); }
.group-count { font-size: 22rpx; color: var(--text-muted); background: var(--bg-input); padding: 4rpx 12rpx; border-radius: 12rpx; }
.group-scroll { white-space: nowrap; }
.card-list { display: inline-flex; gap: 16rpx; }
.card-item { display: inline-flex; flex-direction: column; align-items: center; width: 200rpx; }
.card-item:active { opacity: 0.7; }
.card-image { width: 180rpx; height: 252rpx; border-radius: 8rpx; background: var(--bg-input); }
.card-placeholder { width: 180rpx; height: 252rpx; background: var(--bg-input); border-radius: 8rpx; display: flex; align-items: center; justify-content: center; font-size: 22rpx; color: var(--text-muted); padding: 16rpx; text-align: center; }
.card-name { font-size: 22rpx; color: var(--text-primary); margin-top: 8rpx; text-align: center; max-width: 180rpx; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
```

- [ ] **Step 5: sldcards.js** — clean logs + add methods:

```bash
sed -i '' '/console\.log.*CODEBUDDY_DEBUG/d' miniprogram/pages/sldcards/sldcards.js
```

Add methods:
```javascript
goBack() {
  wx.navigateBack({ fail: () => wx.redirectTo({ url: '/pages/index/index' }) })
},

updateTheme(isLight) {
  this.setData({ isLightTheme: isLight })
}
```

- [ ] **Step 6: 提交**

```bash
git add miniprogram/pages/sldcards/
git commit -m "feat(p4): SLDCards 页面视觉升级"
```

---

## Task 3: Promos 页面（Promo 卡快讯）

**Files:**
- Modify: `miniprogram/pages/promos/promos.wxml`
- Modify: `miniprogram/pages/promos/promos.wxss`
- Modify: `miniprogram/pages/promos/promos.js`
- Modify: `miniprogram/pages/promos/promos.json`

- [ ] **Step 1: 读 promos.js**

Read `promos.js` to see data fields (likely `promos[]` with `name`, `description`, `image_url`, etc.).

- [ ] **Step 2: promos.json**

```json
{
  "navigationBarTitleText": "Promo 卡快讯",
  "usingComponents": {
    "empty-state": "/components/empty-state/empty-state"
  }
}
```

- [ ] **Step 3: promos.wxml** — full replacement:

```xml
<view class="container {{isLightTheme ? '' : 'theme-dark'}}">
  <view class="nav-bar">
    <view class="back-btn" bindtap="goBack">‹</view>
    <text class="nav-title">Promo 卡快讯</text>
  </view>

  <view wx:if="{{loading}}" class="loading">
    <view class="loading-spinner"></view>
    <text class="loading-text">加载中...</text>
  </view>

  <view wx:elif="{{promos.length === 0 && !loading}}" class="empty-wrap">
    <empty-state icon="sparkle" title="暂无 Promo 卡" />
  </view>

  <view wx:else class="promo-list">
    <view class="promo-card" wx:for="{{promos}}" wx:key="id" bindtap="onPromoTap" data-promo="{{item}}">
      <image wx:if="{{item.image_url}}" class="promo-image" src="{{item.image_url}}" mode="aspectFit" />
      <view wx:else class="promo-image-placeholder">
        <text>无图片</text>
      </view>
      <view class="promo-info">
        <text class="promo-name">{{item.name || item.zhs_name}}</text>
        <text wx:if="{{item.description}}" class="promo-desc">{{item.description}}</text>
        <text wx:if="{{item.promo_type}}" class="promo-type">{{item.promo_type}}</text>
      </view>
    </view>
  </view>
</view>
```

- [ ] **Step 4: promos.wxss** — full replacement:

```css
/* pages/promos/promos.wxss */
page { background: var(--bg-page); }
.container { min-height: 100vh; padding: 24rpx 32rpx; }
.nav-bar { display: flex; align-items: center; padding: 16rpx 0 24rpx; }
.back-btn { width: 64rpx; height: 64rpx; display: flex; align-items: center; justify-content: center; font-size: 48rpx; color: var(--text-primary); margin-right: 16rpx; }
.back-btn:active { opacity: 0.5; }
.nav-title { font-size: 36rpx; font-weight: 700; color: var(--text-primary); }

.loading { display: flex; flex-direction: column; align-items: center; padding: 120rpx 0; }
.loading-spinner { width: 48rpx; height: 48rpx; border: 4rpx solid var(--bg-input); border-top-color: var(--accent-dark); border-radius: 50%; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.loading-text { font-size: 24rpx; color: var(--text-secondary); margin-top: 16rpx; }

.empty-wrap { padding: 120rpx 0; }

.promo-list { display: flex; flex-direction: column; gap: 16rpx; }
.promo-card { background: var(--bg-card); border-radius: 20rpx; box-shadow: var(--shadow-card); padding: 20rpx; display: flex; gap: 20rpx; }
.promo-card:active { opacity: 0.7; }
.promo-image { width: 200rpx; height: 280rpx; border-radius: 12rpx; flex-shrink: 0; background: var(--bg-input); }
.promo-image-placeholder { width: 200rpx; height: 280rpx; background: var(--bg-input); border-radius: 12rpx; display: flex; align-items: center; justify-content: center; color: var(--text-muted); font-size: 24rpx; flex-shrink: 0; }
.promo-info { flex: 1; display: flex; flex-direction: column; gap: 8rpx; }
.promo-name { font-size: 30rpx; font-weight: 600; color: var(--text-primary); }
.promo-desc { font-size: 24rpx; color: var(--text-secondary); line-height: 1.5; }
.promo-type { font-size: 22rpx; color: var(--accent-dark); font-weight: 500; }
```

- [ ] **Step 5: promos.js** — add methods:

```javascript
goBack() {
  wx.navigateBack({ fail: () => wx.redirectTo({ url: '/pages/index/index' }) })
},

updateTheme(isLight) {
  this.setData({ isLightTheme: isLight })
},

onPromoTap(e) {
  const promo = e.currentTarget.dataset.promo
  if (promo && promo.id) {
    wx.navigateTo({ url: `/pages/card/card?id=${encodeURIComponent(promo.id)}&from=promo` })
  }
}
```

- [ ] **Step 6: 提交**

```bash
git add miniprogram/pages/promos/
git commit -m "feat(p4): Promos 页面视觉升级"
```

---

## Task 4: Feedback 页面

**Files:**
- Modify: `miniprogram/pages/feedback/feedback.wxml`
- Modify: `miniprogram/pages/feedback/feedback.wxss`
- Modify: `miniprogram/pages/feedback/feedback.js`
- Modify: `miniprogram/pages/feedback/feedback.json`

- [ ] **Step 1: feedback.json**

```json
{
  "navigationBarTitleText": "意见反馈",
  "usingComponents": {
    "tag-chip": "/components/tag-chip/tag-chip"
  }
}
```

- [ ] **Step 2: feedback.wxml** — full replacement:

```xml
<view class="container {{isLightTheme ? '' : 'theme-dark'}}">
  <view class="nav-bar">
    <view class="back-btn" bindtap="goBack">‹</view>
    <text class="nav-title">意见反馈</text>
  </view>

  <view class="form-card">
    <view class="form-label">反馈类型</view>
    <view class="type-list">
      <tag-chip
        wx:for="{{feedbackTypes}}"
        wx:key="key"
        text="{{item.name}}"
        active="{{selectedType === item.key}}"
        data-key="{{item.key}}"
        bindtap="onSelectType"
      />
    </view>

    <view class="form-label">反馈内容</view>
    <textarea
      class="form-textarea"
      placeholder="请描述您的建议或问题..."
      value="{{content}}"
      bindinput="onContentInput"
      maxlength="500"
      auto-height
    ></textarea>
    <text class="form-counter">{{content.length}}/500</text>

    <view class="form-btn {{submitting || !content ? 'disabled' : ''}}" bindtap="submitFeedback">
      <text>{{submitting ? '提交中...' : '提交反馈'}}</text>
    </view>
  </view>
</view>
```

- [ ] **Step 3: feedback.wxss** — full replacement:

```css
/* pages/feedback/feedback.wxss */
page { background: var(--bg-page); }
.container { min-height: 100vh; padding: 24rpx 32rpx; }
.nav-bar { display: flex; align-items: center; padding: 16rpx 0 24rpx; }
.back-btn { width: 64rpx; height: 64rpx; display: flex; align-items: center; justify-content: center; font-size: 48rpx; color: var(--text-primary); margin-right: 16rpx; }
.back-btn:active { opacity: 0.5; }
.nav-title { font-size: 36rpx; font-weight: 700; color: var(--text-primary); }

.form-card { background: var(--bg-card); border-radius: 20rpx; box-shadow: var(--shadow-card); padding: 32rpx 24rpx; }
.form-label { font-size: 28rpx; font-weight: 600; color: var(--text-primary); margin-top: 24rpx; margin-bottom: 16rpx; }
.form-label:first-child { margin-top: 0; }
.type-list { display: flex; gap: 12rpx; flex-wrap: wrap; }

.form-textarea { width: 100%; min-height: 240rpx; background: var(--bg-input); border-radius: 16rpx; padding: 20rpx; font-size: 28rpx; color: var(--text-primary); box-sizing: border-box; }
.form-counter { display: block; text-align: right; font-size: 22rpx; color: var(--text-muted); margin-top: 8rpx; }

.form-btn { background: var(--accent-dark); color: var(--text-inverse); border-radius: 24rpx; padding: 28rpx; text-align: center; font-size: 32rpx; font-weight: 600; margin-top: 32rpx; box-shadow: var(--shadow-card); }
.form-btn:active { opacity: 0.7; }
.form-btn.disabled { background: var(--bg-input); color: var(--text-muted); }
```

- [ ] **Step 4: feedback.js** — add methods + update onSelectType:

```javascript
goBack() {
  wx.navigateBack({ fail: () => wx.redirectTo({ url: '/pages/index/index' }) })
},

updateTheme(isLight) {
  this.setData({ isLightTheme: isLight })
},

onSelectType(e) {
  this.setData({ selectedType: e.currentTarget.dataset.key })
}
```

Note: Existing `selectType` uses `dataset.index`. New WXML uses `dataset.key`. Either:
- Update existing `selectType` to read `dataset.key`
- Or rename to `onSelectType` and update WXML

If existing has `onContentInput`, leave it. If not, add:
```javascript
onContentInput(e) {
  this.setData({ content: e.detail.value })
}
```

- [ ] **Step 5: 提交**

```bash
git add miniprogram/pages/feedback/
git commit -m "feat(p4): Feedback 页面视觉升级"
```

---

## Task 5: Devlog 页面（开发日志）

**Files:**
- Modify: `miniprogram/pages/devlog/devlog.wxml`
- Modify: `miniprogram/pages/devlog/devlog.wxss`
- Modify: `miniprogram/pages/devlog/devlog.js`
- Modify: `miniprogram/pages/devlog/devlog.json`

- [ ] **Step 1: 读 devlog.js**

Read `devlog.js` to see data structure. Likely `logs[]` with `version`, `date`, `changes[]`.

- [ ] **Step 2: devlog.json**

```json
{
  "navigationBarTitleText": "开发日志",
  "usingComponents": {
    "tag-chip": "/components/tag-chip/tag-chip",
    "empty-state": "/components/empty-state/empty-state"
  }
}
```

- [ ] **Step 3: devlog.wxml** — full replacement:

```xml
<view class="container {{isLightTheme ? '' : 'theme-dark'}}">
  <view class="nav-bar">
    <view class="back-btn" bindtap="goBack">‹</view>
    <text class="nav-title">开发日志</text>
  </view>

  <view wx:if="{{loading}}" class="loading">
    <view class="loading-spinner"></view>
    <text class="loading-text">加载中...</text>
  </view>

  <view wx:elif="{{logs.length === 0 && !loading}}" class="empty-wrap">
    <empty-state icon="search" title="暂无日志" />
  </view>

  <view wx:else class="logs">
    <view class="log-card" wx:for="{{logs}}" wx:key="version" wx:for-item="log">
      <view class="log-header">
        <tag-chip text="v{{log.version}}" active="{{true}}" color="var(--accent-gold)" />
        <text class="log-date">{{log.date}}</text>
      </view>
      <view wx:if="{{log.changes && log.changes.length > 0}}" class="log-changes">
        <view wx:for="{{log.changes}}" wx:key="*this" wx:for-item="change" class="log-change">
          <text class="change-bullet">•</text>
          <text class="change-text">{{change}}</text>
        </view>
      </view>
    </view>
  </view>
</view>
```

- [ ] **Step 4: devlog.wxss** — full replacement:

```css
/* pages/devlog/devlog.wxss */
page { background: var(--bg-page); }
.container { min-height: 100vh; padding: 24rpx 32rpx; }
.nav-bar { display: flex; align-items: center; padding: 16rpx 0 24rpx; }
.back-btn { width: 64rpx; height: 64rpx; display: flex; align-items: center; justify-content: center; font-size: 48rpx; color: var(--text-primary); margin-right: 16rpx; }
.back-btn:active { opacity: 0.5; }
.nav-title { font-size: 36rpx; font-weight: 700; color: var(--text-primary); }

.loading { display: flex; flex-direction: column; align-items: center; padding: 120rpx 0; }
.loading-spinner { width: 48rpx; height: 48rpx; border: 4rpx solid var(--bg-input); border-top-color: var(--accent-dark); border-radius: 50%; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.loading-text { font-size: 24rpx; color: var(--text-secondary); margin-top: 16rpx; }

.empty-wrap { padding: 120rpx 0; }

.logs { display: flex; flex-direction: column; gap: 16rpx; }
.log-card { background: var(--bg-card); border-radius: 20rpx; box-shadow: var(--shadow-card); padding: 24rpx; }
.log-header { display: flex; align-items: center; gap: 12rpx; margin-bottom: 16rpx; }
.log-date { font-size: 24rpx; color: var(--text-muted); }
.log-changes { display: flex; flex-direction: column; gap: 8rpx; }
.log-change { display: flex; gap: 12rpx; font-size: 26rpx; color: var(--text-primary); line-height: 1.6; }
.change-bullet { color: var(--accent-dark); flex-shrink: 0; }
```

- [ ] **Step 5: devlog.js** — add methods:

```javascript
goBack() {
  wx.navigateBack({ fail: () => wx.redirectTo({ url: '/pages/index/index' }) })
},

updateTheme(isLight) {
  this.setData({ isLightTheme: isLight })
}
```

- [ ] **Step 6: 提交**

```bash
git add miniprogram/pages/devlog/
git commit -m "feat(p4): Devlog 页面视觉升级"
```

---

## Task 6: APITest 页面

**Files:**
- Modify: `miniprogram/pages/apitest/apitest.wxml`
- Modify: `miniprogram/pages/apitest/apitest.wxss`
- Modify: `miniprogram/pages/apitest/apitest.js`
- Modify: `miniprogram/pages/apitest/apitest.json`

- [ ] **Step 1: 读 apitest.js**

Read `apitest.js` to understand current API testing UI. It's likely a form + response viewer.

- [ ] **Step 2: apitest.json**

```json
{
  "navigationBarTitleText": "API 测试",
  "usingComponents": {
    "tag-chip": "/components/tag-chip/tag-chip"
  }
}
```

- [ ] **Step 3: apitest.wxml** — full replacement (preserve existing functionality):

```xml
<view class="container {{isLightTheme ? '' : 'theme-dark'}}">
  <view class="nav-bar">
    <view class="back-btn" bindtap="goBack">‹</view>
    <text class="nav-title">API 测试</text>
  </view>

  <view class="form-card">
    <view class="form-label">请求方法</view>
    <view class="method-tabs">
      <tag-chip wx:for="{{methods}}" wx:key="key" text="{{item.name}}" active="{{method === item.key}}" data-key="{{item.key}}" bindtap="onSelectMethod" />
    </view>

    <view class="form-label">请求路径</view>
    <input class="form-input" placeholder="/api/..." value="{{path}}" bindinput="onPathInput" />

    <view class="form-label">请求参数（JSON）</view>
    <textarea class="form-textarea" placeholder="{}" value="{{params}}" bindinput="onParamsInput" auto-height></textarea>

    <view class="form-btn" bindtap="sendRequest">发送请求</view>
  </view>

  <view wx:if="{{response}}" class="response-card">
    <view class="response-header">
      <text class="response-title">响应</text>
      <text class="response-status">{{responseStatus}}</text>
    </view>
    <view class="response-body">
      <text user-select="true">{{responseText}}</text>
    </view>
  </view>
</view>
```

Note: The exact WXML depends on the existing apitest.js data fields. Read the file first to see the actual interface (e.g., `requestBody`, `responseBody`, `statusCode`).

- [ ] **Step 4: apitest.wxss** — full replacement:

```css
/* pages/apitest/apitest.wxss */
page { background: var(--bg-page); }
.container { min-height: 100vh; padding: 24rpx 32rpx; }
.nav-bar { display: flex; align-items: center; padding: 16rpx 0 24rpx; }
.back-btn { width: 64rpx; height: 64rpx; display: flex; align-items: center; justify-content: center; font-size: 48rpx; color: var(--text-primary); margin-right: 16rpx; }
.back-btn:active { opacity: 0.5; }
.nav-title { font-size: 36rpx; font-weight: 700; color: var(--text-primary); }

.form-card { background: var(--bg-card); border-radius: 20rpx; box-shadow: var(--shadow-card); padding: 24rpx; margin-bottom: 24rpx; }
.form-label { font-size: 28rpx; font-weight: 600; color: var(--text-primary); margin-top: 20rpx; margin-bottom: 12rpx; }
.form-label:first-child { margin-top: 0; }
.method-tabs { display: flex; gap: 12rpx; flex-wrap: wrap; }
.form-input { width: 100%; background: var(--bg-input); border-radius: 12rpx; padding: 16rpx 20rpx; font-size: 28rpx; color: var(--text-primary); font-family: monospace; box-sizing: border-box; }
.form-textarea { width: 100%; min-height: 160rpx; background: var(--bg-input); border-radius: 12rpx; padding: 16rpx 20rpx; font-size: 26rpx; color: var(--text-primary); font-family: monospace; box-sizing: border-box; }
.form-btn { background: var(--accent-dark); color: var(--text-inverse); border-radius: 16rpx; padding: 24rpx; text-align: center; font-size: 28rpx; font-weight: 600; margin-top: 24rpx; }
.form-btn:active { opacity: 0.7; }

.response-card { background: var(--bg-card); border-radius: 20rpx; box-shadow: var(--shadow-card); padding: 24rpx; }
.response-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16rpx; }
.response-title { font-size: 28rpx; font-weight: 600; color: var(--text-primary); }
.response-status { font-size: 24rpx; color: var(--accent-dark); font-weight: 600; font-family: monospace; }
.response-body { background: var(--bg-input); border-radius: 12rpx; padding: 16rpx; }
.response-body text { font-family: monospace; font-size: 24rpx; color: var(--text-primary); word-break: break-all; }
```

- [ ] **Step 5: apitest.js** — add methods + minimal:

```javascript
goBack() {
  wx.navigateBack({ fail: () => wx.redirectTo({ url: '/pages/index/index' }) })
},

updateTheme(isLight) {
  this.setData({ isLightTheme: isLight })
},

onSelectMethod(e) {
  this.setData({ method: e.currentTarget.dataset.key })
},

onPathInput(e) {
  this.setData({ path: e.detail.value })
},

onParamsInput(e) {
  this.setData({ params: e.detail.value })
}
```

Preserve all existing API testing logic (sendRequest, response handling).

- [ ] **Step 6: 提交**

```bash
git add miniprogram/pages/apitest/
git commit -m "feat(p4): APITest 页面视觉升级"
```

---

## Task 7: Loading 页面

**Files:**
- Modify: `miniprogram/pages/loading/loading.wxml`
- Modify: `miniprogram/pages/loading/loading.wxss`
- Modify: `miniprogram/pages/loading/loading.js`
- Modify: `miniprogram/pages/loading/loading.json`

- [ ] **Step 1: loading.json**

```json
{ "navigationBarTitleText": "" }
```

- [ ] **Step 2: loading.wxml** — full replacement:

```xml
<view class="container {{isLightTheme ? '' : 'theme-dark'}}">
  <view class="loading-content">
    <view class="spinner"></view>
    <text class="loading-text">{{text || '加载中...'}}</text>
  </view>
</view>
```

- [ ] **Step 3: loading.wxss** — full replacement:

```css
/* pages/loading/loading.wxss */
page { background: var(--bg-page); }
.container { min-height: 100vh; display: flex; align-items: center; justify-content: center; }
.loading-content { display: flex; flex-direction: column; align-items: center; }
.spinner { width: 80rpx; height: 80rpx; border: 6rpx solid var(--bg-input); border-top-color: var(--accent-dark); border-radius: 50%; animation: spin 0.8s linear infinite; margin-bottom: 32rpx; }
@keyframes spin { to { transform: rotate(360deg); } }
.loading-text { font-size: 28rpx; color: var(--text-secondary); }
```

- [ ] **Step 4: loading.js** — add methods:

```javascript
updateTheme(isLight) {
  this.setData({ isLightTheme: isLight })
}
```

- [ ] **Step 5: 提交**

```bash
git add miniprogram/pages/loading/
git commit -m "feat(p4): Loading 页面视觉升级"
```

---

## Task 8: Odds 页面（概率计算）

**Files:**
- Modify: `miniprogram/pages/odds/odds.wxml`
- Modify: `miniprogram/pages/odds/odds.wxss`
- Modify: `miniprogram/pages/odds/odds.js`
- Modify: `miniprogram/pages/odds/odds.json`

- [ ] **Step 1: 读 odds.js**

Read `odds.js` to understand probability calculation fields.

- [ ] **Step 2: odds.json**

```json
{
  "navigationBarTitleText": "概率计算",
  "usingComponents": {
    "tag-chip": "/components/tag-chip/tag-chip"
  }
}
```

- [ ] **Step 3: odds.wxml** — full replacement (adapt to actual data):

```xml
<view class="container {{isLightTheme ? '' : 'theme-dark'}}">
  <view class="nav-bar">
    <view class="back-btn" bindtap="goBack">‹</view>
    <text class="nav-title">概率计算</text>
  </view>

  <view class="form-card">
    <view class="form-label">场景</view>
    <view class="scene-tabs">
      <tag-chip wx:for="{{scenes}}" wx:key="key" text="{{item.name}}" active="{{scene === item.key}}" data-key="{{item.key}}" bindtap="onSelectScene" />
    </view>

    <view class="form-label">参数</view>
    <view wx:for="{{inputs}}" wx:key="key" wx:for-item="input" class="form-row">
      <text class="form-row-label">{{input.label}}</text>
      <input class="form-row-input" type="number" value="{{inputValues[input.key]}}" data-key="{{input.key}}" bindinput="onInput" />
    </view>

    <view class="form-btn" bindtap="calculate">计算</view>
  </view>

  <view wx:if="{{result}}" class="result-card">
    <view class="result-header">
      <text class="result-title">结果</text>
    </view>
    <view wx:for="{{result.lines}}" wx:key="*this" class="result-line">
      <text>{{item}}</text>
    </view>
  </view>
</view>
```

Note: Adapt the WXML to match the actual `inputs`, `result`, `scenes` data fields in odds.js. Read the file first to see what's there.

- [ ] **Step 4: odds.wxss** — full replacement:

```css
/* pages/odds/odds.wxss */
page { background: var(--bg-page); }
.container { min-height: 100vh; padding: 24rpx 32rpx; }
.nav-bar { display: flex; align-items: center; padding: 16rpx 0 24rpx; }
.back-btn { width: 64rpx; height: 64rpx; display: flex; align-items: center; justify-content: center; font-size: 48rpx; color: var(--text-primary); margin-right: 16rpx; }
.back-btn:active { opacity: 0.5; }
.nav-title { font-size: 36rpx; font-weight: 700; color: var(--text-primary); }

.form-card { background: var(--bg-card); border-radius: 20rpx; box-shadow: var(--shadow-card); padding: 24rpx; margin-bottom: 24rpx; }
.form-label { font-size: 28rpx; font-weight: 600; color: var(--text-primary); margin-top: 20rpx; margin-bottom: 12rpx; }
.form-label:first-child { margin-top: 0; }
.scene-tabs { display: flex; gap: 12rpx; flex-wrap: wrap; }
.form-row { display: flex; align-items: center; gap: 16rpx; margin-bottom: 16rpx; }
.form-row-label { font-size: 28rpx; color: var(--text-primary); min-width: 200rpx; }
.form-row-input { flex: 1; background: var(--bg-input); border-radius: 12rpx; padding: 16rpx 20rpx; font-size: 28rpx; color: var(--text-primary); }

.form-btn { background: var(--accent-dark); color: var(--text-inverse); border-radius: 16rpx; padding: 24rpx; text-align: center; font-size: 28rpx; font-weight: 600; margin-top: 16rpx; }
.form-btn:active { opacity: 0.7; }

.result-card { background: var(--bg-card); border-radius: 20rpx; box-shadow: var(--shadow-card); padding: 24rpx; }
.result-header { margin-bottom: 16rpx; }
.result-title { font-size: 28rpx; font-weight: 600; color: var(--text-primary); }
.result-line { font-size: 26rpx; color: var(--text-primary); line-height: 1.8; padding: 8rpx 0; }
```

- [ ] **Step 5: odds.js** — add methods:

```javascript
goBack() {
  wx.navigateBack({ fail: () => wx.redirectTo({ url: '/pages/index/index' }) })
},

updateTheme(isLight) {
  this.setData({ isLightTheme: isLight })
}
```

Preserve all calculation logic. If existing has `onSelectScene`, `onInput`, `calculate` methods, leave them. If they use different event names, adapt WXML.

- [ ] **Step 6: 提交**

```bash
git add miniprogram/pages/odds/
git commit -m "feat(p4): Odds 页面视觉升级"
```

---

## Task 9: 整体验证 + 合并

- [ ] **Step 1: 切到 main**

```bash
git checkout main
git pull origin main
```

- [ ] **Step 2: 合并 dev**

```bash
git merge dev --no-ff -m "merge: P4 剩余 8 页面视觉升级"
```

- [ ] **Step 3: 推送**

```bash
git push origin main
git push origin dev
```

- [ ] **Step 4: 验收（开发自测）**

- [ ] 8 个页面在亮色下视觉一致
- [ ] 暗色主题切换在 8 个页面均生效
- [ ] 所有 CODEBUDDY_DEBUG 已清理
- [ ] 无 `wx.showLoading` 直接调用（走 http.js）
- [ ] 控制台无 error/warning

---

## P4 验收清单

- [ ] setcards 网格视图
- [ ] sldcards 分组滚动
- [ ] promos 卡片列表
- [ ] feedback 表单 + tag-chip
- [ ] devlog 版本日志
- [ ] apitest 请求/响应查看器
- [ ] loading 加载动画
- [ ] odds 概率计算
- [ ] 暗色主题在 8 个页面均生效
- [ ] 返回按钮统一使用 goBack
- [ ] 控制台无 error/warning
- [ ] iOS / Android 真机各验证一次

---

## 完成度

P4 完成后，整个 UI/UX 升级项目（P1 + P2 + P3 + P4）共 20 个页面、4 个阶段全部完成。

**最终验收**：
- 设计系统：✅ P1
- 主页 + 工具页：✅ P2
- 核心交互页 + 暗色主题：✅ P3
- 剩余 8 页：✅ P4