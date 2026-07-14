# mtgAsk 小程序前端 UI/UX 优化设计

**Date**: 2026-07-14
**Status**: Draft (pending user approval)
**Owner**: 梁皓铭
**Scope**: `miniprogram/`（19 个页面 + utils + components）

---

## 1. 背景与目标

### 1.1 现状

- 20 个页面目录（19 个在 `app.json` 中注册，`pages/loading/` 仅作开发用）
- ~15,800 行前端代码
- 原生 WXML + WXSS + JS，无 TypeScript、无框架
- 视觉风格：深蓝紫渐变 + emoji 图标，3-4 年前的移动端风格
- 大量重复样板：调试日志、导航跳转、主题切换
- 散落的空/加载/错误态（多为 `wx.showToast` 一笔带过）
- 用户痛点：视觉旧、信息层级不清、无交互动画、空状态不友好

### 1.2 目标

通过 4 阶段重做，建立清晰的视觉语言和组件库：

- **现代感**：明亮日间轻量风 + Feather 风格 SVG 图标 + MTG 五色色块
- **信息层级**：清晰的主从关系、视觉锚点、留白节奏
- **交互动画**：页面过渡、骨架屏、动作反馈
- **友好状态**：空/加载/错误态统一化、可操作
- **可维护**：设计 tokens 化、组件化、消除重复

### 1.3 非目标（YAGNI）

- 不引入 TypeScript / 框架（Taro/uni-app）
- 不改后端 API、不动云函数
- 不引入新的状态管理库（继续用 Page.data）

### 1.4 暗色主题处理策略

- **P1 设计系统阶段**：保留 `tokens.wxss` 中暗色变量定义（兼容现有 `app.wxss` 的 `.theme-light` 写法），但不主动切换演示。
- **P2 首页 + 工具页阶段**：**暂时隐藏暗色主题切换入口**（`app.js` 主题切换按钮不渲染，或自动锁定为亮色），避免新视觉与旧暗色对比造成混乱。
- **P3 核心交互页阶段**：在新设计 token 上**重新实现暗色主题**（基于 P2 验证过的浅色 token 反向定义），届时再放开切换入口。
- **P4 剩余页阶段**：暗色主题全量覆盖。

---

## 2. 视觉风格

### 2.1 色彩系统

| Token | 值 | 用途 |
|---|---|---|
| `--bg-page` | `#faf8f3` | 页面背景（米白） |
| `--bg-card` | `#ffffff` | 卡片背景 |
| `--bg-input` | `#f5f5f5` | 输入框背景 |
| `--text-primary` | `#1a1a1a` | 主文字 |
| `--text-secondary` | `#666666` | 次文字 |
| `--text-muted` | `#999999` | 弱文字 |
| `--border-subtle` | `#f0f0f0` | 细分割线 |
| `--accent-gold` | `#ffd700` | 强调色（AI 裁判、CTA） |
| `--accent-dark` | `#1a1a2e` | 强对比（AI 横幅背景） |

**MTG 五色**（功能分类用）：
| Token | 值 | 用途 |
|---|---|---|
| `--color-white` | `#f5f5f5` | 白（中立） |
| `--color-blue` | `#3a7bc8` | 蓝（Token 生成） |
| `--color-black` | `#1a1a2e` | 黑（套牌） |
| `--color-red` | `#c83a3a` | 红（生命值） |
| `--color-green` | `#3a9b5c` | 绿（骰子） |

### 2.2 排版

- **标题**: 22px, font-weight 700, letter-spacing -0.5px
- **区块标题**: 14px, font-weight 600
- **正文**: 14px, regular
- **辅助文字**: 11-12px, color secondary
- **图标文字**: 10px, color muted
- 字体栈: `Inter, -apple-system, "PingFang SC", sans-serif`

### 2.3 间距与圆角

- 页面内边距: 16px
- 卡片间距: 8-14px
- 卡片圆角: 12-16px
- 小元素圆角: 8-10px
- 图标色块圆角: 8px

### 2.4 阴影

- 卡片轻阴影: `0 2px 12px rgba(0, 0, 0, 0.04)`
- 悬浮态: `0 4px 20px rgba(0, 0, 0, 0.08)`
- AI 强调: 深底 + 金色图标

### 2.5 动效

- 页面切换: 默认 wx 自带，无额外定制
- 元素出现: 淡入 200ms
- 按钮反馈: tap 透明度 0.7
- 加载旋转: 自定义星标旋转（AI 裁判场景）

---

## 3. 目录结构

新增以下目录/文件：

```
miniprogram/
├── assets/
│   └── icons/              # SVG 图标库（Feather 风格，按名称索引）
├── components/
│   ├── token-card/         # 现有（增强）
│   ├── nav-header/         # 🆕 通用顶部导航
│   ├── card-list-item/     # 🆕 列表项
│   ├── section-header/     # 🆕 区块标题
│   ├── empty-state/        # 🆕 空状态
│   ├── skeleton-card/      # 🆕 骨架屏
│   └── tag-chip/           # 🆕 标签芯片
├── styles/                 # 🆕 设计系统
│   ├── tokens.wxss         # 设计变量
│   ├── base.wxss           # 全局基础
│   └── utilities.wxss      # 工具类
├── utils/
│   ├── api.js              # 现有（瘦身后）
│   ├── http.js             # 🆕 通用 HTTP/Cloud 调用
│   ├── error.js            # 🆕 错误处理
│   ├── nav.js              # 🆕 统一跳转
│   ├── icon.js             # 🆕 SVG 图标 helper
│   ├── theme.js            # 🆕 主题逻辑（从 app.js 抽出）
│   └── storage.js          # 🆕 存储封装
└── pages/                  # 19 个页面，按 4 阶段逐步迁移
```

### 3.1 `styles/tokens.wxss`

集中所有 CSS 变量（亮色主题默认；暗色主题通过 `.theme-dark` 覆盖）。

```css
page {
  --bg-page: #faf8f3;
  --bg-card: #ffffff;
  /* ... */
  --color-white: #f5f5f5;
  --color-blue: #3a7bc8;
  --color-black: #1a1a2e;
  --color-red: #c83a3a;
  --color-green: #3a9b5c;
}
```

### 3.2 `components/` 7 个组件

| 组件 | Props | 用途 |
|---|---|---|
| `nav-header` | title, subtitle, showBack, showTheme, transparent | 顶部导航（替代各页面 banner） |
| `card-list-item` | icon, iconColor, title, desc, arrow, withDivider, withImage, bindtap | 列表项（工具/套牌/Token） |
| `section-header` | title, count, moreText, bindmore | 区块标题（首页/SLD/资讯） |
| `empty-state` | icon, title, desc, actionText, bindaction | 空状态（4-5 套 SVG 插画） |
| `skeleton-card` | lines, avatar | 加载骨架屏 |
| `tag-chip` | text, active, color, bindtap | 标签芯片（tabs/筛选） |
| `token-card` | 现有 props | 接入新 tokens，加 hover/press |

组件规则：
- 接口简单，无内部状态（除非必要）
- 视觉通过 tokens 驱动
- 默认 `rpx` 单位、`flex` 布局

### 3.3 `utils/` 拆分

| 文件 | 内容 |
|---|---|
| `http.js` | `requestCloud(path, params, opts)`、智能 loading、retry(GET 1 次) |
| `error.js` | 错误类型、友好提示映射 |
| `nav.js` | `goBack()`、`navigateTo(path)`、`redirectTo(path)` 统一封装 |
| `icon.js` | `getSvg(name)`: 通过图标 name（对应 `assets/icons/feather-<name>.svg`）返回 base64 dataURL，可直接用于 `<image src>` 或 CSS background |
| `theme.js` | `getTheme()`、`setTheme()`、`toggleTheme()`（从 app.js 抽出） |
| `storage.js` | 统一 key 命名（如 `app:theme`、`app:search-history`），加版本前缀 |

`utils/api.js` 瘦身：只保留具体 API 方法（如 `searchRules`、`searchCard`），请求逻辑全部走 `http.js`。

---

## 4. 错误处理

| 错误类型 | 用户提示 | 日志级别 |
|---|---|---|
| 网络失败 | Toast "网络连接失败，请检查网络" | warn |
| 超时 | Toast "请求超时" | warn |
| 业务错误 | Toast 后端 message | warn |
| AI 流式超时 | 静默 + 提示刷新 | info |
| 401/403 | 跳转登录（如有）或 Toast | error |
| 500 | Toast "服务暂不可用，请稍后再试" | error |

- 不再 `console.error` 散落各处，错误统一收口
- Toast 是默认，但空状态场景用 `<empty-state>` 组件更友好
- 关键错误写入 `log_service`（云函数侧已有 `log_service`）

---

## 5. 测试策略

| 层 | 工具 | 覆盖 |
|---|---|---|
| 工具函数 | `minitest/*.test.js`（现有 minitest 框架） | http/error/storage/nav/icon 单元测试 |
| 组件 | 渲染快照（自写） | 7 个组件各 1-2 用例 |
| 页面逻辑 | 微信开发者工具 + 截图 | 19 页关键路径 |
| API 契约 | 已有 `tests/integration/` | 云函数返回结构 |

**质量门禁**（每个 PR）：
- 新增/修改的 `utils/*.js` 必须有测试
- 真机/模拟器截图关键页面对比
- 控制台无 error/warning（清理 `CODEBUDDY_DEBUG` 调试日志）

**手动验收清单**（每阶段）：
- [ ] 首页加载 < 1s
- [ ] 搜索响应 < 3s
- [ ] 主题切换无闪烁
- [ ] 空/加载/错误态在 4G 弱网下正常
- [ ] iOS / Android 真机各验证一次

---

## 6. 4 阶段路线图

### P1 · 设计系统（约 1 周）

**目标**：建立底层，首页用新系统但视觉不变（兼容性验证）

**交付物**：
- `styles/tokens.wxss`、`styles/base.wxss`、`styles/utilities.wxss`
- `assets/icons/` SVG 图标（至少 12 个：search、moon、sun、back、chevron、book、heart、dice、card、plus、close、empty）
- 7 个基础组件（`nav-header`、`card-list-item`、`section-header`、`empty-state`、`skeleton-card`、`tag-chip`、`token-card` 增强）
- `utils/http.js`、`utils/error.js`、`utils/nav.js`、`utils/icon.js`、`utils/theme.js`、`utils/storage.js`
- `utils/api.js` 瘦身
- demo 页面 `pages/_demo/components`（**仅开发用**：不注册到 `app.json`，本地通过 `wx.navigateTo({url: '/pages/_demo/components'})` 测试用；最终 PR 中可通过环境变量或注释临时注册）

**验收**：
- 所有 token 覆盖现有 19 页的所有变量
- 7 组件 demo 渲染正确
- 主题切换所有组件同步响应
- 首页用新组件搭建但保持原视觉（验证兼容性）

### P2 · 首页 + 工具页（约 1-2 周）

**目标**：用户动线主路径视觉升级

**页面**：
- `pages/index/index` — 顶部品牌区 + 搜索 + AI 横幅 + 工具纵向列表 + 系列/资讯
- `pages/token/token` — Token 列表（按颜色分组）
- `pages/token-generate/token-generate` — Token 生成器
- `pages/decks/decks` — 我的套牌
- `pages/deck-detail/deck-detail` — 套牌详情
- `pages/counter/counter` — 生命值计数器
- `pages/dice/dice` — 骰子 & 随机

**视觉升级**：
- 白底 + 微阴影卡片
- 工具列表用 `card-list-item`，图标色块对应 MTG 五色
- AI 裁判入口用深底横幅 + 金色图标强调
- 空/加载/错误态统一（4 套空插画、skeleton-card）

**验收**：
- 7 页全部用新设计语言
- 空/加载/错误态在三场景下都正常
- 暗色主题切换入口**暂时隐藏**（不渲染主题按钮），锁定为亮色主题
- iOS / Android 真机验证

### P3 · 核心交互页（约 1-2 周）

**页面**：
- `pages/search/search` — 搜索结果页
- `pages/card/card` — 卡牌详情
- `pages/rule/rule` — 规则详情
- `pages/keyword/keyword` — 关键词异能
- `pages/agent/agent` — AI 裁判（聊天界面）

**视觉升级**：
- 搜索 tabs 用 `tag-chip`
- 详情页统一布局：顶图 + 标题区 + 标签 + 正文 + 操作
- AI 裁判：聊天气泡 + 流式动画 + 消息状态

**暗色主题回归**：
- 在新设计 tokens 上重新定义暗色变量（反向覆盖亮色 token）
- 重新启用主题切换按钮
- 验收：5 个页面在亮/暗主题下均视觉一致

### P4 · 剩余页（约 1 周）

**页面**：
- `pages/setcards/setcards`
- `pages/sldcards/sldcards`
- `pages/promos/promos`
- `pages/feedback/feedback`
- `pages/devlog/devlog`
- `pages/apitest/apitest`
- `pages/loading/loading`
- `pages/odds/odds`

**视觉升级**：全量迁移，新组件覆盖，旧暗色风格退役。

---

## 7. 风险与缓解

| 风险 | 影响 | 缓解 |
|---|---|---|
| 设计 token 不全 | 视觉不一致 | P1 阶段先扫描现有所有颜色/字号，再定 tokens |
| 组件 API 设计不周 | 后期返工 | P1 demo 页面跑通 19 页所有调用模式 |
| 微信小程序 SVG 限制 | 图标实现方案不确定 | 测试 base64 嵌入 vs CSS background |
| 真机兼容问题 | 部署阻塞 | 每个 P 阶段结束 iOS+Android 真机验证 |
| 用户对视觉改动的负面反馈 | 回滚成本 | P1 保持原视觉验证，P2 灰度或快速迭代 |

---

## 8. 度量与成功标准

- **代码量**: utils/components 复用率提升（减少重复代码 ≥ 30%）
- **首屏**: 首页 FCP < 1s（4G 弱网）
- **维护性**: 新增工具/页面通过组件拼装而非从头写（定性）
- **用户反馈**: 小程序评分/反馈中"界面相关"投诉下降

---

## 9. 附录

### 9.1 SVG 图标库（assets/icons/）

命名规则：`feather-<name>.svg`
| 名称 | 用途 |
|---|---|
| search | 搜索 |
| moon / sun | 主题切换 |
| chevron-right | 列表箭头 |
| arrow-left | 返回 |
| book | 套牌 |
| heart | 生命值 |
| dice | 骰子 |
| card | Token / 卡牌 |
| plus / close | 加号 / 关闭 |
| sparkle | AI 强调 |
| filter | 筛选 |
| share | 分享 |

### 9.2 参考资源

- Feather Icons: https://feathericons.com/
- MTG 五色卡：白蓝黑红绿
- 设计参考：Pinterest 卡片风格、Notion 文档页