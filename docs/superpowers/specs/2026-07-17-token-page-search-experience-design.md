# mtgAsk 小程序 Token 页面搜索体验优化 Design

**Date**: 2026-07-17
**Status**: Draft (pending user approval)
**Owner**: 梁皓铭
**Scope**: `miniprogram/pages/token/*` (token 页面)

---

## 1. 背景与目标

### 1.1 现状（P5.5 已完成）

- 紧凑搜索栏（无独立按钮）
- 颜色 chips 筛选（6 色 + 全部，含数量 badge）
- Token 卡片化列表（色条 + icon + 中英文 + 攻防）

### 1.2 痛点

- **首次进入**只看到搜索框 + chips，缺少"该看什么"引导
- **输入检索**只能全名匹配，不支持拼音 / 英文首字母
- **复访用户**没有"我上次查过什么"快速入口

### 1.3 目标

提升 token 页面搜索**发现性**和**效率**：
- 默认显示最近搜索 + 热门 token（首次打开有用）
- 支持多种匹配方式（中文 / 英文 / 拼音首字母 / 英文首字母）
- 输入时实时建议下拉
- 搜索框下方显示语法提示

### 1.4 非目标

- ❌ 不引入拼音库（用预生成映射表）
- ❌ 不做搜索结果分页（已有 token 数量小，~10 个）
- ❌ 不做模糊拼写纠错

---

## 2. 用户体验

### 2.1 状态机

```
┌─ 初始 (searchQuery == '') ─────────────────────┐
│ 搜索栏 + 历史+热门区 + chips + token 列表     │
└──────────────────────────────────────────────┘
         │ 输入
         ▼
┌─ 搜索中 (searchQuery > 0) ─────────────────────┐
│ 搜索栏 + 语法 hint + 建议下拉（≤5 个匹配）     │
└──────────────────────────────────────────────┘
         │ 清空 / 点击建议 / 失去焦点
         ▼
       回到初始
```

### 2.2 默认页（首次/复访）

```
[🔍 输入英文 Token 名] [✕]            ← 紧凑搜索栏
支持：中文 / 英文 / 拼音首字母 / 英文首字母    ← hint

最近搜索：                              ← 仅复访显示
[Treasure ✕] [士兵 ✕] [精灵 ✕] +2     ← chips

热门 Token：                            ← 固定 6 个
[⚪ 珍宝] [⚪ 士兵] [🔵 精灵] [🔴 鬼怪] [⚫ 灵俑] [⚪ 复制品]

[全部 8] [⚪白 2] [🔵蓝 1] [⚫黑 1] [🔴红 1] [🟢绿 1] [⚪无 2]

[token 卡片列表...]
```

### 2.3 输入中（输入"tr"）

```
[🔍 tr]                              [✕]
Treasure (英文首字母)
[⚪ Treasure] ⚔️                     ← 建议项

[token 列表（实时筛选）]
```

### 2.4 复制品（现有"复制品"token）

- 点击"复制品"→ 弹出现有复制品搜索模态
- 本次**不优化**复制品模态内部（用户本次没选复制品作为优化点）

---

## 3. 数据结构

### 3.1 拼音映射表（pre-generated）

```js
const pinyinMap = {
  '珍宝':   'zb',
  '复制品': 'zfp',
  '士兵':   'sb',
  '天使':   'ts',
  '鬼怪':   'gg',
  '灵俑':   'ly',
  '精灵':   'jl',
  '野狼':   'yl',
  '吸血鬼': 'xxxg',
  '猫':     'm'
}
```

仅 10 个常用 token 需要拼音（其他 token 量小不优先）

### 3.2 新增 data 字段

```js
data: {
  // 已有字段保持...
  searchHistory: [],     // 最多 5 个最近搜索
  showSuggestions: false, // 控制建议下拉显示
  filteredSuggestions: [], // ≤5 个匹配结果
  showHint: false,       // 控制 hint 显示（聚焦时显示）
  hotTokens: []          // 6 个热门 token（从 tokenGroups 计算）
}
```

### 3.3 持久化

- `searchHistory`: localStorage key `tokenSearchHistory`
- 最多 5 项，最近在前

---

## 4. 搜索匹配算法

```js
onTokenSearch(query) {
  query = (query || '').toLowerCase().trim()
  if (!query) {
    this.setData({ showSuggestions: false, filteredSuggestions: [] })
    return
  }
  
  const all = Object.values(this.data.tokenGroups).flatMap(g => g.tokens)
  const matches = all.filter(t => {
    if (t.name.toLowerCase().includes(query)) return true        // 中文包含
    if (t.enName.toLowerCase().includes(query)) return true      // 英文包含
    if (t.enName.toLowerCase().startsWith(query)) return true    // 英文首字母
    const py = pinyinMap[t.name]
    if (py && py.startsWith(query)) return true                   // 拼音首字母
    return false
  })
  
  this.setData({
    filteredSuggestions: matches.slice(0, 5),
    showSuggestions: matches.length > 0
  })
}
```

**匹配优先级**（按顺序）：
1. 中文名包含
2. 英文名包含
3. 英文首字母
4. 拼音首字母

（去重在 `matches.slice(0, 5)` 处理）

---

## 5. 组件 / UI

### 5.1 WXML 新增结构

```xml
<!-- 搜索栏（已有 + 调整） -->
<view class="search-bar">
  <view class="search-icon icon-bg-search"></view>
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
  <view wx:if="{{searchQuery}}" class="search-clear" bindtap="onClearSearch">✕</view>
</view>

<!-- 搜索语法提示（聚焦时显示） -->
<view wx:if="{{showHint}}" class="search-hint">
  <text>支持：中文 / 英文 / 拼音首字母 / 英文首字母</text>
</view>

<!-- 建议下拉（搜索时显示） -->
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

<!-- 历史 + 热门（默认显示） -->
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

### 5.2 WXSS 新增样式

```css
/* Hint */
.search-hint {
  font-size: 22rpx;
  color: var(--text-muted);
  padding: 0 8rpx 16rpx;
}

/* Suggestions */
.suggestions { display: flex; flex-direction: column; gap: 8rpx; margin-bottom: 16rpx; }
.suggestion-item { background: var(--bg-card); border-radius: 16rpx; box-shadow: var(--shadow-card); padding: 16rpx 20rpx; display: flex; align-items: center; gap: 12rpx; }
.suggestion-item:active { opacity: 0.7; }
.suggestion-color { width: 6rpx; height: 32rpx; border-radius: 3rpx; }
.suggestion-color.color-W { background: var(--color-white); border: 1rpx solid var(--border-default); }
.suggestion-color.color-U { background: var(--color-blue); }
.suggestion-color.color-B { background: var(--color-black); }
.suggestion-color.color-R { background: var(--color-red); }
.suggestion-color.color-G { background: var(--color-green); }
.suggestion-color.color-C { background: var(--text-muted); }
.suggestion-icon { font-size: 28rpx; }
.suggestion-info { flex: 1; }
.suggestion-name { font-size: 26rpx; color: var(--text-primary); display: block; }
.suggestion-en { font-size: 22rpx; color: var(--text-secondary); }

/* History + Hot */
.history-section { margin-bottom: 24rpx; }
.block-title { font-size: 26rpx; font-weight: 600; color: var(--text-secondary); display: block; margin-bottom: 16rpx; }
.history-chips { display: flex; flex-wrap: wrap; gap: 12rpx; align-items: center; }
.history-chip { padding: 8rpx 20rpx; background: var(--bg-input); border-radius: 24rpx; font-size: 24rpx; color: var(--text-primary); }
.history-chip:active { opacity: 0.7; }
.history-clear { font-size: 24rpx; color: var(--text-muted); padding: 0 8rpx; }
.history-clear:active { color: var(--accent-dark); }
.hot-list { display: flex; flex-wrap: wrap; gap: 12rpx; }
.hot-chip { display: flex; align-items: center; gap: 8rpx; padding: 8rpx 16rpx; background: var(--bg-card); border-radius: 20rpx; font-size: 24rpx; box-shadow: var(--shadow-card); }
.hot-chip:active { opacity: 0.7; }
.hot-color { width: 12rpx; height: 12rpx; border-radius: 50%; }
.hot-color.color-W { background: var(--color-white); border: 1rpx solid var(--border-default); }
.hot-color.color-U { background: var(--color-blue); }
.hot-color.color-B { background: var(--color-black); }
.hot-color.color-R { background: var(--color-red); }
.hot-color.color-G { background: var(--color-green); }
.hot-color.color-C { background: var(--text-muted); }
```

---

## 6. 错误处理

| 场景 | 处理 |
|------|------|
| localStorage 不可用 | 静默降级，搜索历史只在内存 |
| 拼音映射缺失 token | 跳过该 token 的拼音匹配 |
| 建议下拉无匹配 | `showSuggestions: false`，不显示下拉 |
| 重复搜索 | 在历史中移到最前（去重） |

---

## 7. 测试策略

**手动验证**：
- 默认页：历史 chips 正确显示 / 清空有效
- 热门 chips：点击后选中对应 token（弹详情弹窗）
- 输入 "tre"：建议下拉显示 Treasure（英文首字母）
- 输入 "sb"：建议下拉显示 士兵（拼音首字母）
- 输入 "宝"：建议下拉显示 珍宝（中文包含）
- 清空 input：回到默认页

**边界**：
- 输入空字符串 / 全空格 → 关闭建议下拉
- 输入超长字符串（>20 字符）→ 仍然匹配（只 slice 前 5）
- 存储异常 → 不影响其他功能

---

## 8. 验收清单

- [ ] 默认页显示历史（复访）+ 热门（首次也有）
- [ ] 搜索栏聚焦显示语法 hint
- [ ] 中文包含匹配
- [ ] 英文包含匹配
- [ ] 英文首字母匹配（"tr" → Treasure）
- [ ] 拼音首字母匹配（"sb" → 士兵）
- [ ] 建议下拉点击直接进入 token 详情
- [ ] 搜索成功后写入历史
- [ ] 暗色主题兼容
- [ ] iOS / Android 真机验证

---

## 9. 文件改动

- `miniprogram/pages/token/token.wxml` — 新增建议下拉 + hint + 历史+热门区
- `miniprogram/pages/token/token.wxss` — 新增样式
- `miniprogram/pages/token/token.js` — 新增方法 + data 字段
