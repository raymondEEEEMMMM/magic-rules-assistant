# MTG 错题本功能设计

## Overview

MTG 错题本是一个帮助用户记录、复习实战中遇到的问题的工具。支持记录操作失误、规则问答、miss trigger 三种类型，后续扩展语音输入和 AI 分析功能。

## 数据模型

存储在微信小程序本地 Storage，key 为 `mistake_records`，数据类型为 JSON 数组。

```typescript
interface MistakeRecord {
  id: string;                    // UUID
  type: 'operation' | 'rule' | 'miss_trigger';
  cards: string[];               // 涉及的牌名列表
  title: string;                 // 一句话描述
  content: string;               // 详细记录
  created_at: number;            // 时间戳
  reviewed_at: number | null;    // 最近复习时间
  review_count: number;          // 复习次数
}
```

## 页面结构

| 页面 | 路径 | 功能 |
|------|------|------|
| 列表页 | `/pages/mistake/index` | 展示所有记录，按类型筛选，删除 |
| 新增页 | `/pages/mistake/add` | 选择类型、选牌、输入文字 |
| 详情页 | `/pages/mistake/detail` | 查看记录，复习，AI 分析（预留） |

## 页面交互

### 列表页 `/pages/mistake/index`

- 顶部 Tab 筛选：全部 / 操作失误 / 规则 / Miss Trigger
- 列表项显示：标题、类型标签、创建时间
- 支持左滑删除
- 底部悬浮按钮 `+` 跳转新增页

### 新增页 `/pages/mistake/add`

- Step 1：选择类型（三个按钮）
- Step 2：输入涉及的牌名（可选，支持模糊搜索）
- Step 3：文字描述（textarea）
- 保存后返回列表页

### 详情页 `/pages/mistake/detail`

- 显示完整记录内容
- "标记已复习" 按钮 — 更新 `reviewed_at` 和 `review_count`
- "AI 分析" 按钮（预留）— 跳转 AI Judge 携带内容
- "删除" 按钮

## 类型枚举

| 值 | 显示名 | 标签颜色 |
|----|--------|----------|
| operation | 操作失误 | #FF6B6B |
| rule | 规则 Q&A | #4ECDC4 |
| miss_trigger | Miss Trigger | #FFE66D |

## 后续扩展

1. **语音输入** — 调用 `wx.startRecord` API，语音转文字填入 textarea
2. **首页推送** — 定期在首页显示历史记录提醒复习
3. **AI 分析** — 详情页"AI 分析"按钮，跳转 AI Judge 对话

## 文件结构

```
miniprogram/pages/mistake/
├── index/
│   ├── index.js
│   ├── index.wxml
│   └── index.wxss
├── add/
│   ├── add.js
│   ├── add.wxml
│   └── add.wxss
└── detail/
    ├── detail.js
    ├── detail.wxml
    └── detail.wxss
```

## 依赖

- 无需新的云端依赖
- 使用微信小程序原生 API
- 复用手写字典搜索组件（参考 `miniprogram/pages/token/` 的搜索实现）
