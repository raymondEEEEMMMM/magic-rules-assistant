# mtgAsk 小程序前端 P1 设计系统 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 建立可复用的设计系统（tokens、组件、utils），为 P2-P4 阶段提供视觉与代码基础。首页用新系统但视觉保持不变（兼容性验证）。

**Architecture:** 自底向上分层——
1. 静态资源层（SVG 图标）
2. 设计系统层（CSS 变量、基础样式、工具类）
3. 工具函数层（API、HTTP、错误、导航、主题、存储、图标）
4. 组件层（7 个基础组件）
5. 验证层（demo 页 + 首页兼容性检查）

**Tech Stack:** 微信原生小程序（WXML/WXSS/JS）、Feather Icons SVG 库、minitest 测试框架（已有）

**依赖 spec:** `docs/superpowers/specs/2026-07-14-miniprogram-frontend-optimization-design.md`

---

## 文件结构总览

**新建：**
- `miniprogram/styles/tokens.wxss`
- `miniprogram/styles/base.wxss`
- `miniprogram/styles/utilities.wxss`
- `miniprogram/assets/icons/feather-search.svg` 等 12 个
- `miniprogram/utils/http.js`
- `miniprogram/utils/error.js`
- `miniprogram/utils/nav.js`
- `miniprogram/utils/icon.js`
- `miniprogram/utils/theme.js`
- `miniprogram/utils/storage.js`
- `miniprogram/components/nav-header/{nav-header.js,wxml,wxss,json}`
- `miniprogram/components/card-list-item/{...}`
- `miniprogram/components/section-header/{...}`
- `miniprogram/components/empty-state/{...}`
- `miniprogram/components/skeleton-card/{...}`
- `miniprogram/components/tag-chip/{...}`
- `miniprogram/pages/_demo/components/{...}` (开发用)
- `miniprogram/minitest/utils.test.js`

**修改：**
- `miniprogram/utils/api.js`（瘦身）
- `miniprogram/components/token-card/{token-card.wxss}`（接入 tokens）
- `miniprogram/app.js`（使用 utils/theme.js）
- `miniprogram/app.wxss`（导入新 styles 文件）
- `miniprogram/pages/index/index.wxss`（用 tokens 但视觉不变）

---

## Task 1: 准备工作区

**Files:**
- Modify: `miniprogram/utils/.gitkeep`（如不存在则创建）

- [ ] **Step 1: 创建 styles 目录**

```bash
mkdir -p miniprogram/styles miniprogram/assets/icons
```

- [ ] **Step 2: 创建 components 子目录**

```bash
for name in nav-header card-list-item section-header empty-state skeleton-card tag-chip; do
  mkdir -p miniprogram/components/$name
done
```

- [ ] **Step 3: 创建 demo 页面目录**

```bash
mkdir -p miniprogram/pages/_demo/components
```

- [ ] **Step 4: 提交**

```bash
git add miniprogram/styles miniprogram/assets miniprogram/components miniprogram/pages/_demo
git commit -m "chore(p1): 创建 styles/components/assets 目录结构"
```

---

## Task 2: 写 styles/tokens.wxss（设计变量）

**Files:**
- Create: `miniprogram/styles/tokens.wxss`

- [ ] **Step 1: 写入完整 tokens 文件**

```css
/**
 * mtgAsk 设计 tokens
 *
 * 所有页面统一引用此处的 CSS 变量。
 * 亮色主题默认；暗色主题由 .theme-dark 类覆盖（详见 section 1.4 spec）。
 */

page {
  /* 背景层级 */
  --bg-page: #faf8f3;
  --bg-card: #ffffff;
  --bg-input: #f5f5f5;
  --bg-overlay: rgba(0, 0, 0, 0.4);

  /* 文字层级 */
  --text-primary: #1a1a1a;
  --text-secondary: #666666;
  --text-muted: #999999;
  --text-inverse: #ffffff;

  /* 边框 */
  --border-subtle: #f0f0f0;
  --border-default: #e0e0e0;

  /* 强调色 */
  --accent-gold: #ffd700;
  --accent-dark: #1a1a2e;

  /* MTG 五色（功能分类用） */
  --color-white: #f5f5f5;
  --color-blue: #3a7bc8;
  --color-black: #1a1a2e;
  --color-red: #c83a3a;
  --color-green: #3a9b5c;

  /* 字号 */
  --font-size-xs: 20rpx;
  --font-size-sm: 24rpx;
  --font-size-base: 28rpx;
  --font-size-md: 30rpx;
  --font-size-lg: 32rpx;
  --font-size-xl: 40rpx;
  --font-size-2xl: 44rpx;

  /* 字重 */
  --font-weight-regular: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;

  /* 间距（rpx，750rpx = 屏幕宽） */
  --space-1: 8rpx;
  --space-2: 16rpx;
  --space-3: 24rpx;
  --space-4: 32rpx;
  --space-5: 40rpx;
  --space-6: 48rpx;

  /* 圆角 */
  --radius-sm: 8rpx;
  --radius-md: 12rpx;
  --radius-lg: 16rpx;
  --radius-xl: 24rpx;
  --radius-full: 9999rpx;

  /* 阴影 */
  --shadow-card: 0 2rpx 12rpx rgba(0, 0, 0, 0.04);
  --shadow-hover: 0 4rpx 20rpx rgba(0, 0, 0, 0.08);

  /* 字体栈 */
  --font-family: Inter, -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", sans-serif;

  /* 过渡时长 */
  --duration-fast: 150ms;
  --duration-base: 200ms;
  --duration-slow: 300ms;
}

/* 暗色主题覆盖（P3 阶段启用，定义先准备好） */
.theme-dark {
  --bg-page: #16213e;
  --bg-card: #1a1a2e;
  --bg-input: rgba(255, 255, 255, 0.1);
  --text-primary: #ffffff;
  --text-secondary: rgba(255, 255, 255, 0.7);
  --text-muted: rgba(255, 255, 255, 0.4);
  --border-subtle: rgba(255, 255, 255, 0.1);
  --shadow-card: 0 2rpx 12rpx rgba(0, 0, 0, 0.3);
}
```

- [ ] **Step 2: 提交**

```bash
git add miniprogram/styles/tokens.wxss
git commit -m "feat(p1): 添加设计 tokens（颜色/字号/间距/阴影）"
```

---

## Task 3: 写 styles/base.wxss（全局基础）

**Files:**
- Create: `miniprogram/styles/base.wxss`

- [ ] **Step 1: 写入基础样式**

```css
/**
 * 全局基础样式
 * reset + 字体 + 动效
 */

/* 页面基础 */
page {
  background-color: var(--bg-page);
  color: var(--text-primary);
  font-family: var(--font-family);
  font-size: var(--font-size-base);
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
}

/* 重置列表默认样式 */
.list-reset {
  list-style: none;
  margin: 0;
  padding: 0;
}

/* 通用动效 */
.fade-in {
  animation: fadeIn var(--duration-base) ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8rpx); }
  to { opacity: 1; transform: translateY(0); }
}

/* tap 反馈 */
.tappable {
  transition: opacity var(--duration-fast);
}

.tappable:active {
  opacity: 0.7;
}

/* 文字省略 */
.text-ellipsis {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.text-ellipsis-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
```

- [ ] **Step 2: 提交**

```bash
git add miniprogram/styles/base.wxss
git commit -m "feat(p1): 添加基础样式（reset/字体/动效）"
```

---

## Task 4: 写 styles/utilities.wxss（工具类）

**Files:**
- Create: `miniprogram/styles/utilities.wxss`

- [ ] **Step 1: 写入工具类**

```css
/**
 * 工具类
 * 使用 Tailwind 风格的简短命名
 */

/* Flex 布局 */
.flex { display: flex; }
.flex-col { display: flex; flex-direction: column; }
.flex-1 { flex: 1; }
.items-center { align-items: center; }
.justify-center { justify-content: center; }
.justify-between { justify-content: space-between; }
.gap-1 { gap: var(--space-1); }
.gap-2 { gap: var(--space-2); }
.gap-3 { gap: var(--space-3); }

/* 文字 */
.text-xs { font-size: var(--font-size-xs); }
.text-sm { font-size: var(--font-size-sm); }
.text-base { font-size: var(--font-size-base); }
.text-lg { font-size: var(--font-size-lg); }
.text-xl { font-size: var(--font-size-xl); }
.text-primary { color: var(--text-primary); }
.text-secondary { color: var(--text-secondary); }
.text-muted { color: var(--text-muted); }
.text-inverse { color: var(--text-inverse); }
.font-medium { font-weight: var(--font-weight-medium); }
.font-semibold { font-weight: var(--font-weight-semibold); }
.font-bold { font-weight: var(--font-weight-bold); }
.text-center { text-align: center; }

/* 间距 */
.p-2 { padding: var(--space-2); }
.p-3 { padding: var(--space-3); }
.p-4 { padding: var(--space-4); }
.px-2 { padding-left: var(--space-2); padding-right: var(--space-2); }
.px-3 { padding-left: var(--space-3); padding-right: var(--space-3); }
.py-2 { padding-top: var(--space-2); padding-bottom: var(--space-2); }
.py-3 { padding-top: var(--space-3); padding-bottom: var(--space-3); }
.m-2 { margin: var(--space-2); }
.mt-2 { margin-top: var(--space-2); }
.mt-3 { margin-top: var(--space-3); }
.mb-2 { margin-bottom: var(--space-2); }
.mb-3 { margin-bottom: var(--space-3); }

/* 圆角 */
.rounded-sm { border-radius: var(--radius-sm); }
.rounded-md { border-radius: var(--radius-md); }
.rounded-lg { border-radius: var(--radius-lg); }
.rounded-full { border-radius: var(--radius-full); }

/* 阴影 */
.shadow-card { box-shadow: var(--shadow-card); }
.shadow-hover { box-shadow: var(--shadow-hover); }

/* 卡片容器 */
.card {
  background-color: var(--bg-card);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
  padding: var(--space-3);
}
```

- [ ] **Step 2: 提交**

```bash
git add miniprogram/styles/utilities.wxss
git commit -m "feat(p1): 添加工具类样式"
```

---

## Task 5: 创建 SVG 图标库（12 个）

**Files:**
- Create: `miniprogram/assets/icons/feather-search.svg` 等 12 个

- [ ] **Step 1: 创建 search 图标**

创建 `miniprogram/assets/icons/feather-search.svg`:

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
```

- [ ] **Step 2: 创建 moon / sun 图标**

`feather-moon.svg`:
```xml
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
```

`feather-sun.svg`:
```xml
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>
```

- [ ] **Step 3: 创建箭头图标**

`feather-chevron-right.svg`:
```xml
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>
```

`feather-arrow-left.svg`:
```xml
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>
```

- [ ] **Step 4: 创建工具图标（book/heart/dice/card）**

`feather-book.svg`:
```xml
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>
```

`feather-heart.svg`:
```xml
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>
```

`feather-dice.svg`（自定义：用 grid 表示骰子点）:
```xml
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8" cy="8" r="1.2" fill="currentColor"/><circle cx="16" cy="8" r="1.2" fill="currentColor"/><circle cx="8" cy="16" r="1.2" fill="currentColor"/><circle cx="16" cy="16" r="1.2" fill="currentColor"/><circle cx="12" cy="12" r="1.2" fill="currentColor"/></svg>
```

`feather-card.svg`（类似 card 形状）:
```xml
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M9 9h6v6H9z"/></svg>
```

- [ ] **Step 5: 创建 plus / close / sparkle / filter / share**

`feather-plus.svg`:
```xml
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
```

`feather-close.svg` (x):
```xml
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
```

`feather-sparkle.svg`:
```xml
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>
```

`feather-filter.svg`:
```xml
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/></svg>
```

`feather-share.svg`:
```xml
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>
```

- [ ] **Step 6: 验证所有 12 个图标**

```bash
ls miniprogram/assets/icons/ | wc -l
# Expected: 12
```

- [ ] **Step 7: 提交**

```bash
git add miniprogram/assets/icons
git commit -m "feat(p1): 添加 12 个 Feather 风格 SVG 图标"
```

---

## Task 6: 写 utils/storage.js（存储封装）

**Files:**
- Create: `miniprogram/utils/storage.js`
- Test: `miniprogram/minitest/utils.test.js`

- [ ] **Step 1: 写测试**

创建 `miniprogram/minitest/utils.test.js`:

```javascript
/**
 * utils 单元测试
 * 运行: 在 minitest 页面点击"运行测试"
 */

const storage = require('../utils/storage.js')

// ============= storage =============
function test_storage_set_and_get() {
  storage.set('test:key', { foo: 'bar' })
  const got = storage.get('test:key')
  if (JSON.stringify(got) !== JSON.stringify({ foo: 'bar' })) {
    throw new Error(`expected {foo:'bar'}, got ${JSON.stringify(got)}`)
  }
}

function test_storage_get_with_default() {
  const got = storage.get('test:nonexistent', 'default-value')
  if (got !== 'default-value') {
    throw new Error(`expected 'default-value', got ${got}`)
  }
}

function test_storage_remove() {
  storage.set('test:to-remove', 'value')
  storage.remove('test:to-remove')
  const got = storage.get('test:to-remove')
  if (got !== undefined) {
    throw new Error(`expected undefined, got ${got}`)
  }
}

function test_storage_namespacing() {
  // 不同 namespace 不互相影响
  storage.set('a:key', 1, 'ns1')
  storage.set('a:key', 2, 'ns2')
  if (storage.get('a:key', null, 'ns1') !== 1) throw new Error('ns1 wrong')
  if (storage.get('a:key', null, 'ns2') !== 2) throw new Error('ns2 wrong')
}

module.exports = {
  'storage.set+get': test_storage_set_and_get,
  'storage.get default': test_storage_get_with_default,
  'storage.remove': test_storage_remove,
  'storage namespace': test_storage_namespacing
}
```

- [ ] **Step 2: 运行测试确认失败**

打开 `miniprogram/pages/loading/loading` 或 `miniprogram/minitest/` 页面运行测试。
Expected: `storage.js not found` 错误（因为还没实现）

- [ ] **Step 3: 实现 storage.js**

创建 `miniprogram/utils/storage.js`:

```javascript
/**
 * 存储封装
 *
 * 统一命名空间（默认 'app'），避免 key 冲突。
 * 用法:
 *   storage.set('theme', 'dark')
 *   storage.get('theme', 'light')  // 带默认值
 *   storage.remove('theme')
 *   storage.set('list', [], 'search')  // 自定义 namespace
 */

const DEFAULT_NS = 'app'

function namespacedKey(key, namespace) {
  return `${namespace || DEFAULT_NS}:${key}`
}

module.exports = {
  /**
   * 设置值（自动 JSON 序列化）
   */
  set(key, value, namespace) {
    try {
      wx.setStorageSync(namespacedKey(key, namespace), JSON.stringify(value))
    } catch (e) {
      console.warn('[storage.set] failed', e)
    }
  },

  /**
   * 获取值（自动反序列化）
   * @returns {*} 值或默认值
   */
  get(key, defaultValue, namespace) {
    try {
      const raw = wx.getStorageSync(namespacedKey(key, namespace))
      if (raw === '' || raw === undefined || raw === null) {
        return defaultValue
      }
      return JSON.parse(raw)
    } catch (e) {
      console.warn('[storage.get] failed', e)
      return defaultValue
    }
  },

  /**
   * 删除值
   */
  remove(key, namespace) {
    try {
      wx.removeStorageSync(namespacedKey(key, namespace))
    } catch (e) {
      console.warn('[storage.remove] failed', e)
    }
  },

  /**
   * 清空某个 namespace 下的所有 key
   */
  clearNamespace(namespace) {
    // 微信没有按 namespace 清空的 API，跳过实现
    // 调用方需要自己管理 key
    console.warn('[storage.clearNamespace] not implemented for wx')
  }
}
```

- [ ] **Step 4: 运行测试验证通过**

在测试页面运行 `storage.*` 4 个测试。
Expected: 全部 PASS

- [ ] **Step 5: 提交**

```bash
git add miniprogram/utils/storage.js miniprogram/minitest/utils.test.js
git commit -m "feat(p1): 添加 storage 封装（含测试）"
```

---

## Task 7: 写 utils/theme.js（主题逻辑）

**Files:**
- Create: `miniprogram/utils/theme.js`
- Test: `miniprogram/minitest/utils.test.js`（追加）

- [ ] **Step 1: 追加测试用例**

在 `miniprogram/minitest/utils.test.js` 的 `module.exports` 之前添加：

```javascript
const theme = require('../utils/theme.js')

function test_theme_default_is_light() {
  // 确保 wx.getStorageSync 返回空（测试环境）
  const result = theme.getCurrent()
  if (result !== 'light') {
    throw new Error(`expected 'light', got ${result}`)
  }
}

function test_theme_isLight() {
  theme.set('dark')
  if (theme.isLight() !== false) throw new Error('isLight should be false when dark')
  theme.set('light')
  if (theme.isLight() !== true) throw new Error('isLight should be true when light')
}

function test_theme_toggle() {
  theme.set('light')
  const after1 = theme.toggle()
  if (after1 !== 'dark') throw new Error('toggle from light should give dark')
  const after2 = theme.toggle()
  if (after2 !== 'light') throw new Error('toggle from dark should give light')
}
```

更新 `module.exports`:

```javascript
module.exports = {
  'storage.set+get': test_storage_set_and_get,
  'storage.get default': test_storage_get_with_default,
  'storage.remove': test_storage_remove,
  'storage namespace': test_storage_namespacing,
  'theme default light': test_theme_default_is_light,
  'theme isLight': test_theme_isLight,
  'theme toggle': test_theme_toggle
}
```

- [ ] **Step 2: 实现 theme.js**

创建 `miniprogram/utils/theme.js`:

```javascript
/**
 * 主题管理
 *
 * 用法:
 *   const theme = require('./utils/theme.js')
 *   theme.getCurrent()  // 'light' | 'dark'
 *   theme.isLight()
 *   theme.set('dark')
 *   theme.toggle()
 *   theme.applyToPage(page)  // 给当前页加 theme-light / theme-dark class
 */

const storage = require('./storage.js')

const KEY = 'theme'

module.exports = {
  /**
   * 获取当前主题
   * @returns {'light' | 'dark'}
   */
  getCurrent() {
    return storage.get(KEY, 'light')
  },

  /**
   * 是否亮色主题
   */
  isLight() {
    return this.getCurrent() === 'light'
  },

  /**
   * 设置主题
   * @param {'light' | 'dark'} themeName
   */
  set(themeName) {
    storage.set(KEY, themeName)
    this._applyToAllPages()
  },

  /**
   * 切换主题
   * @returns {string} 切换后的主题
   */
  toggle() {
    const next = this.isLight() ? 'dark' : 'light'
    this.set(next)
    return next
  },

  /**
   * 切换主题（保持原 app.toggleTheme 签名）
   */
  toggleTheme() {
    return this.toggle()
  },

  /**
   * 把主题应用到指定 page 实例
   */
  applyToPage(page) {
    if (!page || !page.setData) return
    page.setData({ isLightTheme: this.isLight() })
  },

  /**
   * 广播主题变更给所有当前页
   */
  _applyToAllPages() {
    const pages = getCurrentPages()
    pages.forEach(page => {
      if (page.updateTheme) {
        page.updateTheme(this.isLight())
      }
    })
  }
}
```

- [ ] **Step 3: 运行测试**

Expected: 3 个 theme 测试 PASS

- [ ] **Step 4: 提交**

```bash
git add miniprogram/utils/theme.js miniprogram/minitest/utils.test.js
git commit -m "feat(p1): 添加 theme 主题管理（含测试）"
```

---

## Task 8: 写 utils/error.js（错误处理）

**Files:**
- Create: `miniprogram/utils/error.js`
- Test: `miniprogram/minitest/utils.test.js`（追加）

- [ ] **Step 1: 追加测试**

在 `miniprogram/minitest/utils.test.js` 添加：

```javascript
const errorUtil = require('../utils/error.js')

function test_error_classify_network() {
  const err = { errMsg: 'request:fail' }
  const type = errorUtil.classify(err)
  if (type !== 'network') throw new Error(`expected 'network', got ${type}`)
}

function test_error_classify_timeout() {
  const err = { errMsg: 'request:fail timeout' }
  const type = errorUtil.classify(err)
  if (type !== 'timeout') throw new Error(`expected 'timeout', got ${type}`)
}

function test_error_classify_business() {
  const err = '业务错误：参数无效'
  const type = errorUtil.classify(err)
  if (type !== 'business') throw new Error(`expected 'business', got ${type}`)
}

function test_error_friendlyMessage_network() {
  const msg = errorUtil.friendlyMessage({ errMsg: 'request:fail' })
  if (!msg.includes('网络')) throw new Error(`expected 网络提示, got: ${msg}`)
}

function test_error_handle_with_toast() {
  // 模拟 wx.showToast
  let toastCalled = null
  const origToast = wx.showToast
  wx.showToast = (opts) => { toastCalled = opts }
  errorUtil.handle({ errMsg: 'request:fail' }, { silent: false, context: '测试场景' })
  wx.showToast = origToast
  if (!toastCalled || !toastCalled.title.includes('网络')) {
    throw new Error('Toast should be called with network message')
  }
}

function test_error_handle_silent() {
  let toastCalled = false
  const origToast = wx.showToast
  wx.showToast = () => { toastCalled = true }
  errorUtil.handle({ errMsg: 'request:fail' }, { silent: true })
  wx.showToast = origToast
  if (toastCalled) throw new Error('Toast should not be called in silent mode')
}
```

更新 `module.exports`:

```javascript
module.exports = {
  'storage.set+get': test_storage_set_and_get,
  'storage.get default': test_storage_get_with_default,
  'storage.remove': test_storage_remove,
  'storage namespace': test_storage_namespacing,
  'theme default light': test_theme_default_is_light,
  'theme isLight': test_theme_isLight,
  'theme toggle': test_theme_toggle,
  'error classify network': test_error_classify_network,
  'error classify timeout': test_error_classify_timeout,
  'error classify business': test_error_classify_business,
  'error friendlyMessage network': test_error_friendlyMessage_network,
  'error handle toast': test_error_handle_with_toast,
  'error handle silent': test_error_handle_silent
}
```

- [ ] **Step 2: 实现 error.js**

创建 `miniprogram/utils/error.js`:

```javascript
/**
 * 错误处理
 *
 * 用法:
 *   const errorUtil = require('./utils/error.js')
 *   errorUtil.handle(err, { context: '搜索失败' })
 */

const TYPE_NETWORK = 'network'
const TYPE_TIMEOUT = 'timeout'
const TYPE_BUSINESS = 'business'
const TYPE_AUTH = 'auth'
const TYPE_SERVER = 'server'
const TYPE_UNKNOWN = 'unknown'

const FRIENDLY_MESSAGES = {
  [TYPE_NETWORK]: '网络连接失败，请检查网络',
  [TYPE_TIMEOUT]: '请求超时，请稍后再试',
  [TYPE_BUSINESS]: null, // 用 err.message
  [TYPE_AUTH]: '请登录后重试',
  [TYPE_SERVER]: '服务暂不可用，请稍后再试',
  [TYPE_UNKNOWN]: '操作失败，请稍后重试'
}

function classify(err) {
  if (!err) return TYPE_UNKNOWN

  const msg = (err.errMsg || err.message || String(err)).toLowerCase()

  if (msg.includes('timeout') || msg.includes('timed out') || msg.includes('time_limit')) {
    return TYPE_TIMEOUT
  }
  if (msg.includes('fail') && !msg.includes('timeout')) {
    return TYPE_NETWORK
  }
  if (err.statusCode === 401 || err.statusCode === 403) {
    return TYPE_AUTH
  }
  if (err.statusCode >= 500) {
    return TYPE_SERVER
  }
  return TYPE_BUSINESS
}

function friendlyMessage(err) {
  const type = classify(err)
  if (type === TYPE_BUSINESS) {
    return err.message || err.errMsg || FRIENDLY_MESSAGES[TYPE_UNKNOWN]
  }
  return FRIENDLY_MESSAGES[type] || FRIENDLY_MESSAGES[TYPE_UNKNOWN]
}

/**
 * 统一处理错误
 * @param {Error|string|object} err
 * @param {object} opts
 * @param {string} opts.context - 操作场景（如 "搜索"），用于日志
 * @param {boolean} opts.silent - true 则不显示 Toast
 */
function handle(err, opts = {}) {
  const { context = '', silent = false } = opts
  const message = friendlyMessage(err)

  if (!silent) {
    wx.showToast({ title: message, icon: 'none', duration: 2000 })
  }

  if (context) {
    console.warn(`[error] ${context}:`, err)
  }

  return { type: classify(err), message }
}

module.exports = {
  classify,
  friendlyMessage,
  handle,
  TYPES: {
    NETWORK: TYPE_NETWORK,
    TIMEOUT: TYPE_TIMEOUT,
    BUSINESS: TYPE_BUSINESS,
    AUTH: TYPE_AUTH,
    SERVER: TYPE_SERVER,
    UNKNOWN: TYPE_UNKNOWN
  }
}
```

- [ ] **Step 3: 运行测试**

Expected: 6 个 error 测试 PASS

- [ ] **Step 4: 提交**

```bash
git add miniprogram/utils/error.js miniprogram/minitest/utils.test.js
git commit -m "feat(p1): 添加 error 错误处理（含测试）"
```

---

## Task 9: 写 utils/http.js（HTTP 封装）

**Files:**
- Create: `miniprogram/utils/http.js`
- Test: `miniprogram/minitest/utils.test.js`（追加）

- [ ] **Step 1: 追加测试**

```javascript
const http = require('../utils/http.js')

function test_http_buildQueryString() {
  const qs = http.buildQueryString({ q: '黑莲花', page: 1, undef: undefined })
  if (qs !== 'q=%E9%BB%91%E8%8E%B2%E8%8A%B1&page=1') {
    throw new Error(`unexpected: ${qs}`)
  }
}

function test_http_buildCloudCallData_GET() {
  const data = http.buildCloudCallData('/api/search', { q: '飞行' }, 'GET')
  if (data.path !== '/api/search') throw new Error('path wrong')
  if (!data.queryString.includes('q=')) throw new Error('queryString missing')
  if (data.body !== undefined) throw new Error('GET should not have body')
}

function test_http_buildCloudCallData_POST() {
  const data = http.buildCloudCallData('/api/foo', { foo: 'bar' }, 'POST')
  if (data.path !== '/api/foo') throw new Error('path wrong')
  if (data.body !== JSON.stringify({ foo: 'bar' })) throw new Error('body wrong')
  if (data.queryString !== undefined) throw new Error('POST should not have queryString')
}

function test_http_parseResponse_body_string() {
  const res = { result: { body: JSON.stringify({ ok: true }) } }
  const parsed = http.parseResponse(res)
  if (!parsed.ok) throw new Error('parse failed')
}

function test_http_parseResponse_direct() {
  const res = { result: { ok: true } }
  const parsed = http.parseResponse(res)
  if (!parsed.ok) throw new Error('parse failed')
}
```

更新 `module.exports`:

```javascript
module.exports = {
  // ... 已有测试
  'http buildQueryString': test_http_buildQueryString,
  'http buildCloudCallData GET': test_http_buildCloudCallData_GET,
  'http buildCloudCallData POST': test_http_buildCloudCallData_POST,
  'http parseResponse body string': test_http_parseResponse_body_string,
  'http parseResponse direct': test_http_parseResponse_direct
}
```

- [ ] **Step 2: 实现 http.js**

创建 `miniprogram/utils/http.js`:

```javascript
/**
 * HTTP 封装（云函数调用）
 *
 * 用法:
 *   const http = require('./utils/http.js')
 *   const data = await http.requestCloud('/api/search', { q: '飞行' })
 *
 * 特性:
 * - 统一 wx.cloud.callFunction 包装
 * - GET/POST 参数构造
 * - 智能 loading（默认关闭，按需开启）
 * - 响应自动解析 body
 * - 错误统一抛出（由 error.js 消费）
 */

const FUNCTION_NAME = 'mtgAsk' // 可被 api.js 覆盖
const errorUtil = require('./error.js')

/**
 * URL-encode 对象为 query string（跳过 undefined/null）
 */
function buildQueryString(params) {
  const parts = []
  for (const key in params) {
    if (params[key] !== undefined && params[key] !== null) {
      parts.push(`${encodeURIComponent(key)}=${encodeURIComponent(params[key])}`)
    }
  }
  return parts.join('&')
}

/**
 * 构建云函数调用参数
 */
function buildCloudCallData(path, params, method) {
  const normalizedPath = path.startsWith('/') ? path : '/' + path
  if (method === 'GET') {
    return {
      httpMethod: 'GET',
      path: normalizedPath,
      queryString: buildQueryString(params || {})
    }
  }
  return {
    httpMethod: method,
    path: normalizedPath,
    body: JSON.stringify(params || {})
  }
}

/**
 * 解析云函数响应
 */
function parseResponse(res) {
  let result = res.result
  if (!result) return null

  if (result.body) {
    try {
      result = typeof result.body === 'string' ? JSON.parse(result.body) : result.body
    } catch (e) {
      console.warn('[http.parseResponse] body parse failed', e)
    }
  }
  if (typeof result === 'string') {
    try {
      result = JSON.parse(result)
    } catch (e) {
      // 保持字符串
    }
  }
  return result
}

/**
 * 调用云函数
 * @param {string} path
 * @param {object} params
 * @param {object} opts
 * @param {string} opts.method - 'GET' | 'POST'
 * @param {boolean} opts.showLoading - 是否显示 loading toast（默认 false）
 * @returns {Promise<*>}
 */
function requestCloud(path, params = {}, opts = {}) {
  const { method = 'GET', showLoading = false } = opts

  return new Promise((resolve, reject) => {
    if (showLoading) {
      wx.showLoading({ title: '加载中...' })
    }

    const callData = buildCloudCallData(path, params, method)

    wx.cloud.callFunction({
      name: FUNCTION_NAME,
      data: callData,
      success: (res) => {
        if (showLoading) wx.hideLoading()
        if (res.errMsg && res.errMsg.includes('fail')) {
          reject(new Error(res.errMsg))
          return
        }
        const result = parseResponse(res)
        if (result && result.error) {
          reject(new Error(result.error))
          return
        }
        resolve(result)
      },
      fail: (err) => {
        if (showLoading) wx.hideLoading()
        reject(err)
      }
    })
  })
}

/**
 * GET 请求便捷方法
 */
function get(path, params, opts) {
  return requestCloud(path, params, { ...opts, method: 'GET' })
}

/**
 * POST 请求便捷方法
 */
function post(path, params, opts) {
  return requestCloud(path, params, { ...opts, method: 'POST' })
}

module.exports = {
  requestCloud,
  get,
  post,
  buildQueryString,
  buildCloudCallData,
  parseResponse
}
```

- [ ] **Step 3: 运行测试**

Expected: 5 个 http 测试 PASS

- [ ] **Step 4: 提交**

```bash
git add miniprogram/utils/http.js miniprogram/minitest/utils.test.js
git commit -m "feat(p1): 添加 http 云函数调用封装（含测试）"
```

---

## Task 10: 写 utils/nav.js（导航封装）

**Files:**
- Create: `miniprogram/utils/nav.js`
- Test: `miniprogram/minitest/utils.test.js`（追加）

- [ ] **Step 1: 追加测试**

```javascript
const nav = require('../utils/nav.js')

function test_nav_buildUrl_with_query() {
  const url = nav.buildUrl('/pages/card/card', { id: 'abc 123' })
  if (url !== '/pages/card/card?id=abc%20123') {
    throw new Error(`unexpected: ${url}`)
  }
}

function test_nav_buildUrl_no_query() {
  const url = nav.buildUrl('/pages/index/index')
  if (url !== '/pages/index/index') throw new Error('unexpected')
}
```

- [ ] **Step 2: 实现 nav.js**

创建 `miniprogram/utils/nav.js`:

```javascript
/**
 * 导航封装
 *
 * 用法:
 *   const nav = require('./utils/nav.js')
 *   nav.navigateTo('/pages/card/card', { id: 'xxx' })
 *   nav.redirectTo('/pages/login/login')
 *   nav.switchTab('/pages/index/index')
 *   nav.goBack()
 */

/**
 * 构建带 query 的 URL
 */
function buildUrl(path, query) {
  if (!query || Object.keys(query).length === 0) return path
  const parts = []
  for (const key in query) {
    if (query[key] !== undefined && query[key] !== null) {
      parts.push(`${encodeURIComponent(key)}=${encodeURIComponent(query[key])}`)
    }
  }
  return `${path}?${parts.join('&')}`
}

function navigateTo(path, query) {
  return new Promise((resolve, reject) => {
    wx.navigateTo({
      url: buildUrl(path, query),
      success: resolve,
      fail: reject
    })
  })
}

function redirectTo(path, query) {
  return new Promise((resolve, reject) => {
    wx.redirectTo({
      url: buildUrl(path, query),
      success: resolve,
      fail: reject
    })
  })
}

function switchTab(path) {
  return new Promise((resolve, reject) => {
    wx.switchTab({
      url: path,
      success: resolve,
      fail: reject
    })
  })
}

function goBack(delta = 1) {
  return new Promise((resolve) => {
    wx.navigateBack({ delta, success: resolve, fail: resolve })
  })
}

module.exports = {
  buildUrl,
  navigateTo,
  redirectTo,
  switchTab,
  goBack
}
```

- [ ] **Step 3: 追加测试到 module.exports**

```javascript
  'nav buildUrl with query': test_nav_buildUrl_with_query,
  'nav buildUrl no query': test_nav_buildUrl_no_query
```

- [ ] **Step 4: 运行测试**

Expected: 2 个 nav 测试 PASS

- [ ] **Step 5: 提交**

```bash
git add miniprogram/utils/nav.js miniprogram/minitest/utils.test.js
git commit -m "feat(p1): 添加 nav 导航封装（含测试）"
```

---

## Task 11: 写 utils/icon.js（SVG 图标 helper）

**Files:**
- Create: `miniprogram/utils/icon.js`
- Test: `miniprogram/minitest/utils.test.js`（追加）

- [ ] **Step 1: 追加测试**

```javascript
const iconUtil = require('../utils/icon.js')

function test_icon_getDataUrl() {
  const url = iconUtil.getDataUrl('search')
  if (!url.startsWith('data:image/svg+xml;base64,')) {
    throw new Error(`unexpected: ${url.slice(0, 50)}`)
  }
}

function test_icon_getDataUrl_with_size_and_color() {
  const url = iconUtil.getDataUrl('search', { size: 32, color: '#ff0000' })
  // 解码 base64 验证包含 width="32" 和 color
  const decoded = atob(url.replace('data:image/svg+xml;base64,', ''))
  if (!decoded.includes('width="32"')) throw new Error('size not applied')
  if (!decoded.includes('#ff0000') && !decoded.includes('stroke="#ff0000"')) {
    throw new Error('color not applied')
  }
}

function test_icon_getDataUrl_unknown() {
  const url = iconUtil.getDataUrl('nonexistent-icon-name')
  if (url !== '') throw new Error(`expected '', got ${url}`)
}
```

- [ ] **Step 2: 实现 icon.js**

创建 `miniprogram/utils/icon.js`:

```javascript
/**
 * SVG 图标 helper
 *
 * 把 assets/icons/feather-<name>.svg 转成 base64 dataURL，
 * 可直接用于 <image src> 或 CSS background。
 *
 * 用法:
 *   const iconUtil = require('./utils/icon.js')
 *   iconUtil.getDataUrl('search')
 *   iconUtil.getDataUrl('search', { size: 32, color: '#ff0000' })
 */

// 内置图标库（直接内嵌 SVG，避免 require 静态资源）
const ICONS = {
  'search': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>',
  'moon': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>',
  'sun': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>',
  'chevron-right': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>',
  'arrow-left': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>',
  'book': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>',
  'heart': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>',
  'dice': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8" cy="8" r="1.2" fill="currentColor"/><circle cx="16" cy="8" r="1.2" fill="currentColor"/><circle cx="8" cy="16" r="1.2" fill="currentColor"/><circle cx="16" cy="16" r="1.2" fill="currentColor"/><circle cx="12" cy="12" r="1.2" fill="currentColor"/></svg>',
  'card': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M9 9h6v6H9z"/></svg>',
  'plus': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>',
  'close': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>',
  'sparkle': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>',
  'filter': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/></svg>',
  'share': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>'
}

// base64-encode（兼容小程序无 btoa）
function base64Encode(str) {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
  let result = ''
  let i = 0
  while (i < str.length) {
    const c1 = str.charCodeAt(i++) & 0xff
    const c2 = i < str.length ? str.charCodeAt(i++) & 0xff : NaN
    const c3 = i < str.length ? str.charCodeAt(i++) & 0xff : NaN
    const e1 = c1 >> 2
    const e2 = ((c1 & 3) << 4) | (c2 >> 2)
    const e3 = isNaN(c2) ? 64 : (((c2 & 15) << 2) | (c3 >> 4))
    const e4 = isNaN(c3) ? 64 : (c3 & 63)
    result += chars.charAt(e1) + chars.charAt(e2) + chars.charAt(e3) + chars.charAt(e4)
  }
  return result
}

function applyAttrs(svg, size, color) {
  let result = svg
  if (size) {
    result = result.replace(/width="\d+"/, 'width="' + size + '"').replace(/height="\d+"/, 'height="' + size + '"')
  }
  if (color) {
    result = result.replace(/stroke="currentColor"/g, 'stroke="' + color + '"')
  }
  return result
}

function getDataUrl(name, opts) {
  opts = opts || {}
  const svg = ICONS[name]
  if (!svg) {
    console.warn('[icon] unknown icon: ' + name)
    return ''
  }
  const final = applyAttrs(svg, opts.size, opts.color)
  return 'data:image/svg+xml;base64,' + base64Encode(final)
}

function listNames() {
  return Object.keys(ICONS)
}

module.exports = { getDataUrl: getDataUrl, listNames: listNames }
```

- [ ] **Step 3: 追加 icon 测试到 module.exports**

```javascript
  'icon getDataUrl': test_icon_getDataUrl,
  'icon getDataUrl with size/color': test_icon_getDataUrl_with_size_and_color,
  'icon getDataUrl unknown': test_icon_getDataUrl_unknown
```

- [ ] **Step 4: 运行测试**

Expected: 3 个 icon 测试 PASS

- [ ] **Step 5: 提交**

```bash
git add miniprogram/utils/icon.js miniprogram/minitest/utils.test.js
git commit -m "feat(p1): 添加 icon SVG helper（含 12 图标 + 测试）"
```

---

## Task 12: 瘦身 utils/api.js

**Files:**
- Modify: `miniprogram/utils/api.js`

- [ ] **Step 1: 替换 request 实现为 http.js 调用**

```javascript
const http = require('./http.js')
const errorUtil = require('./error.js')

const api = {
  searchRules(keyword) {
    if (!keyword || !keyword.trim()) return Promise.reject('请输入搜索关键词')
    return http.get('/api/search', { q: keyword })
  },
  getKeyword(keyword) {
    if (!keyword || !keyword.trim()) return Promise.reject('请输入关键词')
    return http.get('/api/keyword', { k: keyword })
  },
  getRule(ruleNumber) {
    if (!ruleNumber || !ruleNumber.trim()) return Promise.reject('请输入规则编号')
    return http.get('/api/rule', { n: ruleNumber })
  },
  searchCard(cardName, page, pageSize) {
    page = page || 1; pageSize = pageSize || 5
    if (!cardName || !cardName.trim()) return Promise.reject('请输入卡牌名称')
    return http.get('/api/card', { q: cardName, page: page, page_size: pageSize })
  },
  getStatus() { return http.get('/', {}) },
  getCardById(cardId) {
    if (!cardId) return Promise.reject('请输入卡牌ID')
    return http.get('/api/mtgch/card', { id: cardId })
  },
  getCardBySetAndNumber(setCode, number) {
    if (!setCode || !number) return Promise.reject('请输入系列代码和编号')
    return http.get('/api/mtgch/card', { set: setCode, number: number })
  },
  autocomplete(query, size) {
    size = size || 10
    if (!query || !query.trim()) return Promise.reject('请输入搜索内容')
    return http.get('/api/mtgch/autocomplete', { q: query, size: size })
  },
  getSetCards(setCode, page, pageSize) {
    page = page || 1; pageSize = pageSize || 20
    if (!setCode || !setCode.trim()) return Promise.reject('请输入系列代码')
    return http.get('/api/scryfall/set/' + setCode.toLowerCase() + '/cards/', { page: page })
  },
  getSecretLairCards(months) {
    months = months || 12
    return http.get('/api/secret-lair/cards', { months: months })
  },
  searchSecretLair(code) { return http.get('/api/secret-lair/search', { code: code }) },
  aiJudgeInit(openid) {
    if (!openid) return Promise.reject('openid 参数必填')
    return http.post('/api/ai-judge/init', { openid: openid })
  },
  aiJudgeChat(message, sessionId, openid) {
    sessionId = sessionId || 'miniprogram'
    if (!message || !message.trim()) return Promise.reject('请输入问题')
    const data = { message: message, session_id: sessionId }
    if (openid) data.openid = openid
    return http.post('/api/ai-judge/chat', data)
  },
  aiJudgeClear(sessionId, openid) {
    sessionId = sessionId || 'miniprogram'
    return http.post('/api/ai-judge/clear', { session_id: sessionId, openid: openid })
  },
  aiJudgeHistory(openid, sessionId, limit, offset) {
    limit = limit || 10; offset = offset || 0
    if (!openid) return Promise.reject('openid 参数必填')
    const data = { openid: openid, limit: limit, offset: offset }
    if (sessionId) data.session_id = sessionId
    return http.post('/api/ai-judge/history', data)
  },
  cleanupSessions() { return http.post('/api/admin/cleanup-sessions', {}) },
  submitFeedback(content, type, openid) {
    type = type || 'suggestion'; openid = openid || ''
    return http.post('/api/feedback', { content: content, type: type, openid: openid })
  },
  getAgentPoolStats() { return http.post('/api/admin/agent-pool/stats', {}) }
}

api.KEYWORDS = {
  FLYING: 'Flying', REACH: 'Reach', FIRST_STRIKE: 'First Strike',
  DOUBLE_STRIKE: 'Double Strike', TRAMPLE: 'Trample', MENACE: 'Menace',
  DEATHTOUCH: 'Deathtouch', DEFENDER: 'Defender', INDESTRUCTIBLE: 'Indestructible',
  WARD: 'Ward', HASTE: 'Haste', VIGILANCE: 'Vigilance', RUSH: 'Rush',
  FLASH: 'Flash', TAP: 'Tap', UNTAP: 'Untap', HEXPROOF: 'Hexproof',
  SHROUD: 'Shroud', PROTECTION: 'Protection', EVOKE: 'Evoke', EXPLOIT: 'Exploit'
}

api.CN_KEYWORDS = {
  '飞行': 'Flying', '死触': 'Deathtouch', '先攻': 'First Strike',
  '警戒': 'Vigilance', '闪现': 'Flash', '威慑': 'Menace',
  '呼魂': 'Evoke', '践踏': 'Trample', '连击': 'Double Strike',
  '辟邪': 'Hexproof', '不灭': 'Indestructible', '守护': 'Ward',
  '敏捷': 'Haste', '延势': 'Reach'
}

api.getCnKeyword = function(cn) { return this.CN_KEYWORDS[cn] || cn }
api.searchRulesCn = function(keyword) { return this.searchRules(keyword) }
api.getKeywordCn = function(keyword) {
  return this.getKeyword(this.getCnKeyword(keyword))
}

module.exports = api
```

- [ ] **Step 2: 验证首页搜索仍可用**

在微信开发者工具运行首页，搜索"飞行"，确认返回关键词结果。
Expected: 与改造前一致

- [ ] **Step 3: 提交**

```bash
git add miniprogram/utils/api.js
git commit -m "refactor(p1): api.js 迁移到 http.js（去除重复 request 实现）"
```

---

## Task 13: 创建 components/nav-header

**Files:**
- Create: `miniprogram/components/nav-header/{nav-header.js,wxml,wxss,json}`

- [ ] **Step 1: nav-header.js**

```javascript
const iconUtil = require('../../utils/icon.js')

Component({
  properties: {
    title: { type: String, value: '' },
    subtitle: { type: String, value: '' },
    showBack: { type: Boolean, value: false },
    showTheme: { type: Boolean, value: false }
  },
  data: { backIcon: '', themeIcon: '', isLightTheme: true },
  lifetimes: {
    attached() {
      const themeUtil = require('../../utils/theme.js')
      this.setData({
        backIcon: iconUtil.getDataUrl('arrow-left'),
        themeIcon: iconUtil.getDataUrl(themeUtil.isLight() ? 'moon' : 'sun'),
        isLightTheme: themeUtil.isLight()
      })
    }
  },
  methods: {
    onBack() { this.triggerEvent('back') },
    onToggleTheme() { this.triggerEvent('toggletheme') }
  }
})
```

- [ ] **Step 2: nav-header.wxml**

```xml
<view class="nav-header">
  <view wx:if="{{showBack}}" class="nav-btn" bindtap="onBack">
    <image class="icon" src="{{backIcon}}" mode="aspectFit"></image>
  </view>
  <view class="title-block">
    <view class="title">{{title}}</view>
    <view wx:if="{{subtitle}}" class="subtitle">{{subtitle}}</view>
  </view>
  <view wx:if="{{showTheme}}" class="nav-btn" bindtap="onToggleTheme">
    <image class="icon" src="{{themeIcon}}" mode="aspectFit"></image>
  </view>
</view>
```

- [ ] **Step 3: nav-header.wxss**

```css
.nav-header {
  display: flex;
  align-items: center;
  padding: var(--space-3) var(--space-2);
  background-color: var(--bg-card);
}
.nav-btn {
  width: 64rpx;
  height: 64rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-full);
}
.nav-btn:active { opacity: 0.7; }
.icon { width: 36rpx; height: 36rpx; }
.title-block { flex: 1; padding: 0 var(--space-2); }
.title {
  font-size: var(--font-size-md);
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
}
.subtitle {
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
  margin-top: 2rpx;
}
```

- [ ] **Step 4: nav-header.json**

```json
{ "component": true, "usingComponents": {} }
```

- [ ] **Step 5: 提交**

```bash
git add miniprogram/components/nav-header
git commit -m "feat(p1): 添加 nav-header 顶部导航组件"
```

---

## Task 14: 创建 components/card-list-item

**Files:**
- Create: `miniprogram/components/card-list-item/{card-list-item.js,wxml,wxss,json}`

- [ ] **Step 1: card-list-item.js**

```javascript
const iconUtil = require('../../utils/icon.js')

Component({
  properties: {
    icon: { type: String, value: '' },
    iconColor: { type: String, value: '' },
    title: { type: String, value: '' },
    desc: { type: String, value: '' },
    arrow: { type: Boolean, value: true },
    withDivider: { type: Boolean, value: false }
  },
  data: { chevronDataUrl: '', iconDataUrl: '' },
  lifetimes: {
    attached() {
      const data = { chevronDataUrl: iconUtil.getDataUrl('chevron-right') }
      if (this.properties.icon) {
        data.iconDataUrl = iconUtil.getDataUrl(this.properties.icon, { color: '#ffffff' })
      }
      this.setData(data)
    }
  },
  methods: { onTap() { this.triggerEvent('tap') } }
})
```

- [ ] **Step 2: card-list-item.wxml**

```xml
<view class="list-item {{withDivider ? 'with-divider' : ''}}" bindtap="onTap">
  <view wx:if="{{icon}}" class="icon-block" style="background-color: {{iconColor}};">
    <image class="icon-img" src="{{iconDataUrl}}" mode="aspectFit"></image>
  </view>
  <view class="content">
    <view class="title">{{title}}</view>
    <view wx:if="{{desc}}" class="desc">{{desc}}</view>
  </view>
  <image wx:if="{{arrow}}" class="chevron" src="{{chevronDataUrl}}"></image>
</view>
```

- [ ] **Step 3: card-list-item.wxss**

```css
.list-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3);
  background-color: var(--bg-card);
}
.list-item:active { opacity: 0.7; }
.list-item.with-divider { border-bottom: 1rpx solid var(--border-subtle); }
.icon-block {
  width: 68rpx; height: 68rpx; border-radius: var(--radius-sm);
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.icon-img { width: 36rpx; height: 36rpx; }
.content { flex: 1; min-width: 0; }
.title {
  font-size: var(--font-size-md);
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
}
.desc {
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
  margin-top: 4rpx;
}
.chevron { width: 32rpx; height: 32rpx; opacity: 0.3; flex-shrink: 0; }
```

- [ ] **Step 4: card-list-item.json**

```json
{ "component": true, "usingComponents": {} }
```

- [ ] **Step 5: 提交**

```bash
git add miniprogram/components/card-list-item
git commit -m "feat(p1): 添加 card-list-item 列表项组件"
```

---

## Task 15: 创建 components/section-header

**Files:**
- Create: `miniprogram/components/section-header/{section-header.js,wxml,wxss,json}`

- [ ] **Step 1-4: 完整文件**

`section-header.js`:
```javascript
Component({
  properties: {
    title: { type: String, value: '' },
    count: { type: Number, value: null },
    moreText: { type: String, value: '' }
  },
  methods: { onMore() { this.triggerEvent('more') } }
})
```

`section-header.wxml`:
```xml
<view class="section-header">
  <view class="left">
    <text class="title">{{title}}</text>
    <text wx:if="{{count !== null}}" class="count">{{count}}</text>
  </view>
  <view wx:if="{{moreText}}" class="more" bindtap="onMore">
    <text>{{moreText}}</text>
  </view>
</view>
```

`section-header.wxss`:
```css
.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-3) 0;
}
.left { display: flex; align-items: center; gap: var(--space-1); }
.title {
  font-size: var(--font-size-md);
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
}
.count {
  font-size: var(--font-size-xs);
  color: var(--text-muted);
  background-color: var(--bg-input);
  padding: 2rpx 12rpx;
  border-radius: var(--radius-full);
}
.more {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}
```

`section-header.json`:
```json
{ "component": true, "usingComponents": {} }
```

- [ ] **Step 5: 提交**

```bash
git add miniprogram/components/section-header
git commit -m "feat(p1): 添加 section-header 区块标题组件"
```

---

## Task 16: 创建 components/empty-state

**Files:**
- Create: `miniprogram/components/empty-state/{empty-state.js,wxml,wxss,json}`

- [ ] **Step 1: empty-state.js**

```javascript
const iconUtil = require('../../utils/icon.js')

Component({
  properties: {
    icon: { type: String, value: 'search' },
    title: { type: String, value: '' },
    desc: { type: String, value: '' },
    actionText: { type: String, value: '' }
  },
  data: { iconDataUrl: '' },
  lifetimes: {
    attached() {
      this.setData({ iconDataUrl: iconUtil.getDataUrl(this.properties.icon, { size: 56 }) })
    }
  },
  methods: { onAction() { this.triggerEvent('action') } }
})
```

- [ ] **Step 2: empty-state.wxml**

```xml
<view class="empty-state">
  <view class="icon-circle">
    <image class="icon" src="{{iconDataUrl}}" mode="aspectFit"></image>
  </view>
  <view wx:if="{{title}}" class="title">{{title}}</view>
  <view wx:if="{{desc}}" class="desc">{{desc}}</view>
  <view wx:if="{{actionText}}" class="action" bindtap="onAction">
    <text>{{actionText}}</text>
  </view>
</view>
```

- [ ] **Step 3: empty-state.wxss**

```css
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--space-6) var(--space-3);
}
.icon-circle {
  width: 120rpx; height: 120rpx;
  background-color: var(--bg-input);
  border-radius: var(--radius-full);
  display: flex; align-items: center; justify-content: center;
  margin-bottom: var(--space-3);
}
.icon { width: 56rpx; height: 56rpx; opacity: 0.5; }
.title {
  font-size: var(--font-size-md);
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
}
.desc {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  margin-top: var(--space-1);
  text-align: center;
}
.action {
  margin-top: var(--space-4);
  padding: var(--space-2) var(--space-5);
  background-color: var(--accent-dark);
  color: var(--text-inverse);
  border-radius: var(--radius-full);
  font-size: var(--font-size-sm);
}
.action:active { opacity: 0.7; }
```

- [ ] **Step 4: empty-state.json**

```json
{ "component": true, "usingComponents": {} }
```

- [ ] **Step 5: 提交**

```bash
git add miniprogram/components/empty-state
git commit -m "feat(p1): 添加 empty-state 空状态组件"
```

---

## Task 17: 创建 components/skeleton-card

**Files:**
- Create: `miniprogram/components/skeleton-card/{skeleton-card.js,wxml,wxss,json}`

- [ ] **Step 1: skeleton-card.js**

```javascript
Component({
  properties: {
    lines: { type: Number, value: 3 },
    avatar: { type: Boolean, value: false }
  }
})
```

- [ ] **Step 2: skeleton-card.wxml**

```xml
<view class="skeleton">
  <view wx:if="{{avatar}}" class="skeleton-avatar"></view>
  <view class="skeleton-body">
    <view wx:for="{{lines}}" wx:key="*this" class="skeleton-line" style="width: {{item === 1 ? '60%' : (item === lines ? '40%' : '90%')}};"></view>
  </view>
</view>
```

- [ ] **Step 3: skeleton-card.wxss**

```css
.skeleton {
  display: flex;
  gap: var(--space-3);
  padding: var(--space-3);
  background-color: var(--bg-card);
  border-radius: var(--radius-lg);
}
.skeleton-avatar {
  width: 80rpx; height: 80rpx;
  border-radius: var(--radius-full);
  background-color: var(--bg-input);
  flex-shrink: 0;
}
.skeleton-body { flex: 1; display: flex; flex-direction: column; gap: var(--space-2); }
.skeleton-line {
  height: 24rpx;
  border-radius: var(--radius-sm);
  background: linear-gradient(90deg, var(--bg-input) 0%, #ececec 50%, var(--bg-input) 100%);
  background-size: 200% 100%;
  animation: shimmer 1.4s infinite;
}
@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
```

- [ ] **Step 4: skeleton-card.json**

```json
{ "component": true, "usingComponents": {} }
```

- [ ] **Step 5: 提交**

```bash
git add miniprogram/components/skeleton-card
git commit -m "feat(p1): 添加 skeleton-card 骨架屏组件"
```

---

## Task 18: 创建 components/tag-chip

**Files:**
- Create: `miniprogram/components/tag-chip/{tag-chip.js,wxml,wxss,json}`

- [ ] **Step 1: tag-chip.js**

```javascript
Component({
  properties: {
    text: { type: String, value: '' },
    active: { type: Boolean, value: false },
    color: { type: String, value: '' }
  },
  methods: { onTap() { this.triggerEvent('tap', { text: this.properties.text }) } }
})
```

- [ ] **Step 2: tag-chip.wxml**

```xml
<view
  class="chip {{active ? 'active' : ''}}"
  style="{{color && active ? 'background-color:' + color + ';' : ''}}"
  bindtap="onTap"
>
  <text>{{text}}</text>
</view>
```

- [ ] **Step 3: tag-chip.wxss**

```css
.chip {
  display: inline-flex;
  align-items: center;
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-full);
  background-color: var(--bg-input);
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}
.chip:active { opacity: 0.7; }
.chip.active {
  background-color: var(--accent-dark);
  color: var(--text-inverse);
  font-weight: var(--font-weight-semibold);
}
```

- [ ] **Step 4: tag-chip.json**

```json
{ "component": true, "usingComponents": {} }
```

- [ ] **Step 5: 提交**

```bash
git add miniprogram/components/tag-chip
git commit -m "feat(p1): 添加 tag-chip 标签芯片组件"
```

---

## Task 19: 增强 components/token-card

**Files:**
- Modify: `miniprogram/components/token-card/token-card.wxss`

- [ ] **Step 1: 替换为 tokens 变量**

完整替换 `miniprogram/components/token-card/token-card.wxss`：

```css
.token-card {
  display: flex;
  flex-direction: column;
  background-color: var(--bg-card);
  border-radius: var(--radius-md);
  padding: var(--space-3);
  box-shadow: var(--shadow-card);
}
.token-card:active { opacity: 0.7; }
.token-name {
  font-size: var(--font-size-md);
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
}
.token-type {
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
  margin-top: var(--space-1);
}
```

- [ ] **Step 2: 提交**

```bash
git add miniprogram/components/token-card
git commit -m "refactor(p1): token-card 接入设计 tokens"
```

---

## Task 20: 创建 demo 演示页

**Files:**
- Create: `miniprogram/pages/_demo/components/{components.js,wxml,wxss,json}`

> **重要**：本页面**不注册到 app.json**。在 IDE 中临时通过 `wx.navigateTo({ url: '/pages/_demo/components' })` 调用预览。

- [ ] **Step 1: components.js**

```javascript
const iconUtil = require('../../utils/icon.js')

Page({
  data: {
    icons: iconUtil.listNames(),
    iconDataUrls: {}
  },
  onLoad() {
    const urls = {}
    this.data.icons.forEach(name => {
      urls[name] = iconUtil.getDataUrl(name, { size: 32 })
    })
    this.setData({ iconDataUrls: urls })
  }
})
```

- [ ] **Step 2: components.wxml**

```xml
<view class="demo-page">
  <view class="section">
    <view class="section-title">nav-header</view>
    <nav-header title="演示页" subtitle="副标题示例" showBack="{{true}}" showTheme="{{true}}" />
  </view>

  <view class="section">
    <view class="section-title">card-list-item</view>
    <card-list-item icon="book" iconColor="#1a1a2e" title="我的套牌" desc="导入导出" />
    <card-list-item icon="heart" iconColor="#c83a3a" title="生命值" desc="多人对战" withDivider="{{true}}" />
    <card-list-item icon="dice" iconColor="#3a9b5c" title="骰子" desc="随机抽卡" withDivider="{{true}}" />
  </view>

  <view class="section">
    <view class="section-title">section-header</view>
    <section-header title="最新系列" count="9" moreText="查看全部 ›" />
  </view>

  <view class="section">
    <view class="section-title">tag-chip</view>
    <view class="chips-row">
      <tag-chip text="全部" active="{{true}}" />
      <tag-chip text="卡牌" />
      <tag-chip text="规则" />
      <tag-chip text="关键词" />
    </view>
  </view>

  <view class="section">
    <view class="section-title">skeleton-card</view>
    <skeleton-card lines="3" avatar="{{true}}" />
  </view>

  <view class="section">
    <view class="section-title">empty-state</view>
    <empty-state icon="search" title="未找到结果" desc="试试其他关键词" actionText="清空搜索" />
  </view>

  <view class="section">
    <view class="section-title">图标库（12 个）</view>
    <view class="icons-grid">
      <view wx:for="{{icons}}" wx:key="*this" class="icon-cell">
        <image class="icon-img" src="{{iconDataUrls[item]}}" mode="aspectFit"></image>
        <text class="icon-name">{{item}}</text>
      </view>
    </view>
  </view>
</view>
```

- [ ] **Step 3: components.wxss**

```css
.demo-page {
  min-height: 100vh;
  padding: var(--space-3);
  background-color: var(--bg-page);
}
.section {
  margin-bottom: var(--space-5);
  background-color: var(--bg-card);
  border-radius: var(--radius-lg);
  padding: var(--space-3);
}
.section-title {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  margin-bottom: var(--space-2);
}
.chips-row { display: flex; gap: var(--space-2); flex-wrap: wrap; }
.icons-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: var(--space-3); }
.icon-cell { display: flex; flex-direction: column; align-items: center; gap: var(--space-1); }
.icon-img { width: 48rpx; height: 48rpx; }
.icon-name { font-size: var(--font-size-xs); color: var(--text-muted); }
```

- [ ] **Step 4: components.json**

```json
{
  "navigationBarTitleText": "组件演示",
  "usingComponents": {
    "nav-header": "/components/nav-header/nav-header",
    "card-list-item": "/components/card-list-item/card-list-item",
    "section-header": "/components/section-header/section-header",
    "empty-state": "/components/empty-state/empty-state",
    "skeleton-card": "/components/skeleton-card/skeleton-card",
    "tag-chip": "/components/tag-chip/tag-chip"
  }
}
```

- [ ] **Step 5: 提交**

```bash
git add miniprogram/pages/_demo/components
git commit -m "feat(p1): 添加组件演示页（开发用，不注册 app.json）"
```

---

## Task 21: 更新 app.js

**Files:**
- Modify: `miniprogram/app.js`

- [ ] **Step 1: 重写 app.js**

```javascript
/**
 * mtgAsk - 小程序入口
 */

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
    isLightTheme: themeUtil.isLight(),
    showAIJudgeCard: false,
    db: db
  },

  version: '1.0.0',

  onLaunch() {
    this.globalData.isLightTheme = themeUtil.isLight()
  },

  onShow() {},

  toggleTheme() { return themeUtil.toggle() },

  updateTheme(isLight) {
    const pages = getCurrentPages()
    pages.forEach(page => {
      if (page.updateTheme) page.updateTheme(isLight)
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

- [ ] **Step 2: 提交**

```bash
git add miniprogram/app.js
git commit -m "refactor(p1): app.js 使用新 theme util，去掉调试日志"
```

---

## Task 22: 更新 app.wxss 导入 styles

**Files:**
- Modify: `miniprogram/app.wxss`

- [ ] **Step 1: 重写 app.wxss**

```css
/* 全局样式入口 */
@import './styles/tokens.wxss';
@import './styles/base.wxss';
@import './styles/utilities.wxss';

/* 旧的 .theme-light 选择器（保留兼容，P3 阶段用 tokens 替换） */
page.theme-light {
  --bg-page: #f5f5f5;
  --bg-card: #ffffff;
  --text-primary: #333333;
  --text-secondary: #666666;
  --text-muted: #999999;
  --border-subtle: #e0e0e0;
  --accent-color: #667eea;
  --card-bg: rgba(0, 0, 0, 0.05);
  --input-bg: #f0f0f0;
}
```

- [ ] **Step 2: 提交**

```bash
git add miniprogram/app.wxss
git commit -m "refactor(p1): app.wxss 导入新 styles 文件"
```

---

## Task 23: 首页兼容性验证（视觉不变）

**Files:**
- Modify: `miniprogram/styles/tokens.wxss`
- Modify: `miniprogram/pages/index/index.wxss`
- Modify: `miniprogram/pages/index/index.js`

- [ ] **Step 1: 在 tokens.wxss 顶部加 legacy 变量**

修改 `miniprogram/styles/tokens.wxss`，在 `page { ... }` 块开头加入：

```css
page {
  /* Legacy 兼容变量（P1 阶段保留旧视觉） */
  --legacy-bg: #16213e;
  --legacy-accent-start: #667eea;
  --legacy-accent-end: #764ba2;
  --legacy-text: #ffffff;
  --legacy-text-secondary: rgba(255, 255, 255, 0.6);
  --legacy-text-muted: rgba(255, 255, 255, 0.4);
  --legacy-border: rgba(255, 255, 255, 0.1);
  --legacy-card-bg: rgba(255, 255, 255, 0.08);
  --legacy-input-bg: rgba(255, 255, 255, 0.1);

  /* 新设计 tokens（亮色默认） */
  --bg-page: #faf8f3;
  /* ... 其余不变 */
}
```

- [ ] **Step 2: 替换首页 wxss 中的硬编码颜色**

```bash
cd miniprogram/pages/index
sed -i '' 's/#16213e/var(--legacy-bg)/g' index.wxss
sed -i '' 's/#667eea/var(--legacy-accent-start)/g' index.wxss
sed -i '' 's/#764ba2/var(--legacy-accent-end)/g' index.wxss
```

- [ ] **Step 3: 删除首页 JS 中所有 CODEBUDDY_DEBUG 日志**

```bash
sed -i '' '/console\.log.*CODEBUDDY_DEBUG/d' miniprogram/pages/index/index.js
sed -i '' '/console\.log.*CODEBUDDY_DEBUG/d' miniprogram/pages/index/index.wxml 2>/dev/null || true
```

- [ ] **Step 4: 视觉对比**

1. **修改前**（先截基线）：在开发者工具截一张首页图
2. 运行替换后的代码
3. 截屏对比新首页
4. 两张图必须**像素级一致**

Expected: 视觉与 P1 改造前完全一致（无变化）

- [ ] **Step 5: 验证控制台无 CODEBUDDY_DEBUG**

```bash
grep -r "CODEBUDDY_DEBUG" miniprogram/pages/index/ || echo "CLEAN"
# Expected: CLEAN
```

- [ ] **Step 6: 提交**

```bash
git add miniprogram/styles/tokens.wxss miniprogram/pages/index
git commit -m "refactor(p1): 首页用 legacy tokens 替换硬编码颜色 + 清理调试日志"
```

---

## P1 验收清单

完成所有 task 后逐项验证：

- [ ] 所有 utils 单测通过（~20 个测试：storage/theme/error/http/nav/icon）
- [ ] 6 个新组件在 `_demo/components` 页正确渲染
- [ ] `app.wxss` 导入新 styles 无报错
- [ ] 首页截屏与 P1 开始前像素级一致（视觉兼容）
- [ ] `app.js` 不再使用 `console.log("CODEBUDDY_DEBUG")`
- [ ] iOS / Android 真机各编译运行一次
- [ ] 没有 `wx.showLoading` 直接调用（都走 http.js）
- [ ] 控制台无 error/warning
- [ ] `grep -r CODEBUDDY_DEBUG miniprogram/` 输出为空

---

## 下一步

P1 完成后，按相同 TDD 模式继续生成 P2-P4 plan。生成入口：

- P2 plan: `docs/superpowers/plans/2026-07-14-miniprogram-p2-homepage-tools.md`
- P3 plan: `docs/superpowers/plans/2026-07-14-miniprogram-p3-core-pages.md`
- P4 plan: `docs/superpowers/plans/2026-07-14-miniprogram-p4-remaining-pages.md`

每个 plan 遵循本文件的 TDD + 完整代码 + 提交规范。
