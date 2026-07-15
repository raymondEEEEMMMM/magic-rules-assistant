# mtgAsk 小程序前端 P5 清理任务 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 清理 P1-P4 阶段遗留的死代码、未使用 data 字段、残留硬编码颜色，提升代码可维护性。

**Architecture:** 静态扫描 + 局部清理 — 不引入新功能，仅删除冗余。

**Tech Stack:** 微信原生小程序 + 已有的 P1-P4 设计系统

**前置状态：** P1-P4 全部完成（`edb0c07` on main）

---

## 文件清单

**修改**：
- `miniprogram/pages/keyword/keyword.js` — 移除 `commonKeywords` data 字段
- `miniprogram/pages/setcards/setcards.js` — 移除 viewMode/filter* data 和方法
- `miniprogram/pages/sldcards/sldcards.js` — 移除 viewMode/searchCode data 和方法
- `miniprogram/pages/odds/odds.js` — 移除 `selectedDeck` 等未使用字段
- `miniprogram/pages/index/index.wxss` — 移除 `feedback-link` 残留（保留 - 仍在用）
- `miniprogram/pages/index/index.js` — 移除 `noop` 死方法（如有）

**无需修改**：`pages/_demo/components/`（开发用，不上线）

---

## Task 1: 移除 keyword.js 的 commonKeywords

**Files:**
- Modify: `miniprogram/pages/keyword/keyword.js`

- [ ] **Step 1: 验证 commonKeywords 不在 WXML 中使用**

```bash
grep -n "commonKeywords" miniprogram/pages/keyword/keyword.wxml
# Expected: 0 matches
```

- [ ] **Step 2: 移除 commonKeywords 字段和相关方法**

用 Edit 工具，从 `miniprogram/pages/keyword/keyword.js` 的 `data` 对象中删除 `commonKeywords` 字段，并移除不再使用的 `searchKeyword` 方法（如果有）。

Find:
```javascript
    commonKeywords: [
      'Flying', 'Trample', 'Deathtouch', 'First Strike', 'Lifelink',
      'Haste', 'Vigilance', 'Reach', 'Hexproof', 'Indestructible',
      'Menace', 'Double Strike', 'Flash', 'Ward', 'Protection'
    ],
```

Replace with: (empty — remove the whole array)

- [ ] **Step 3: 移除 searchKeyword 方法（如未使用）**

```bash
grep -n "searchKeyword" miniprogram/pages/keyword/keyword.wxml
# Expected: 0
```

If 0, remove the `searchKeyword` method from keyword.js (Edit tool to remove the method block).

- [ ] **Step 4: 提交**

```bash
git add miniprogram/pages/keyword/keyword.js
git commit -m "refactor(p5): 移除 keyword.js 未使用 commonKeywords"
```

---

## Task 2: 移除 setcards.js 的 filter/viewMode 死代码

**Files:**
- Modify: `miniprogram/pages/setcards/setcards.js`

- [ ] **Step 1: 验证 WXML 中没有用到的字段**

```bash
grep -n "viewMode\|filterColor\|filterCmc\|filterType\|filterRarity\|filteredCards" miniprogram/pages/setcards/setcards.wxml
# Expected: 0 matches
```

If 0, those data fields are dead code.

- [ ] **Step 2: 移除 filter 相关 data 字段**

用 Edit 工具，从 `setcards.js` 的 `data` 对象中删除：
- `viewMode`
- `filterColor`
- `filterCmc`
- `filterType`
- `filterRarity`
- `filteredCards`

每个字段用单独 Edit 替换（或一次 Edit 删多个相邻字段）。

- [ ] **Step 3: 移除对应方法**

移除以下方法（如果存在且未在 WXML 调用）：
- `toggleViewMode()`
- `selectColorFilter()`
- `selectCmcFilter()`

验证:
```bash
grep -n "toggleViewMode\|selectColorFilter\|selectCmcFilter" miniprogram/pages/setcards/setcards.wxml
# Expected: 0
```

如果 0，从 setcards.js 删除这些方法。

- [ ] **Step 4: 提交**

```bash
git add miniprogram/pages/setcards/setcards.js
git commit -m "refactor(p5): 移除 setcards.js 未使用 filter 数据"
```

---

## Task 3: 移除 sldcards.js 的 searchCode/viewMode 死代码

**Files:**
- Modify: `miniprogram/pages/sldcards/sldcards.js`

- [ ] **Step 1: 验证 WXML 中没有用到的字段**

```bash
grep -n "viewMode\|searchCode" miniprogram/pages/sldcards/sldcards.wxml
# Expected: 0 matches
```

- [ ] **Step 2: 移除 searchCode/viewMode data 字段**

用 Edit 工具，从 `sldcards.js` 的 `data` 中删除 `searchCode` 和 `viewMode` 字段。

- [ ] **Step 3: 移除对应方法**

```bash
grep -n "onSearchCodeInput\|toggleViewMode\|onSearchSubmit" miniprogram/pages/sldcards/sldcards.wxml
# Expected: 0
```

如果 0，从 sldcards.js 删除这些方法。

- [ ] **Step 4: 提交**

```bash
git add miniprogram/pages/sldcards/sldcards.js
git commit -m "refactor(p5): 移除 sldcards.js 未使用 search 数据"
```

---

## Task 4: 移除 odds.js 死字段

**Files:**
- Modify: `miniprogram/pages/odds/odds.js`

- [ ] **Step 1: 验证 WXML 中字段使用情况**

```bash
grep -n "selectedDeck\|formatNames\|selectedFormat" miniprogram/pages/odds/odds.wxml
```

For each field that's not in WXML, it's dead code.

- [ ] **Step 2: 移除死字段（按需）**

Read `odds.js` data block. For each field not referenced in WXML, remove it.

- [ ] **Step 3: 提交**

```bash
git add miniprogram/pages/odds/odds.js
git commit -m "refactor(p5): 移除 odds.js 未使用 data 字段"
```

---

## Task 5: 清理 index.wxss 残留（feedback-link）

**Files:**
- Modify: `miniprogram/pages/index/index.wxss`

- [ ] **Step 1: 验证 feedback-link 实际使用**

```bash
grep -n "feedback-link" miniprogram/pages/index/index.wxml
```

If used (Expected: 2 matches in WXML), KEEP the CSS. If not, remove.

- [ ] **Step 2: 如果需要删除**

从 index.wxss 移除 `.feedback-link` 规则。

- [ ] **Step 3: 提交**

```bash
git add miniprogram/pages/index/index.wxss
git commit -m "refactor(p5): 清理 index.wxss 死样式"
```

---

## Task 6: 清理 index.js 死方法

**Files:**
- Modify: `miniprogram/pages/index/index.js`

- [ ] **Step 1: 查找可疑死方法**

```bash
grep -n "noop" miniprogram/pages/index/index.wxml
# Expected: 0 (or any uses)
```

Other potential dead methods (in index.js):
- `onPullDownRefresh` (if not used by WXML)
- Various `goTo*` methods that may not be in WXML

For each method, verify it's called from WXML.

- [ ] **Step 2: 删除确认死方法**

用 Edit 工具删除确认无引用的方法。

- [ ] **Step 3: 提交**

```bash
git add miniprogram/pages/index/index.js
git commit -m "refactor(p5): 清理 index.js 死方法"
```

---

## Task 7: 整体验证 + 合并

- [ ] **Step 1: 运行最终 lint 检查**

```bash
grep -rn "CODEBUDDY_DEBUG" miniprogram/ 2>/dev/null
# Expected: no output

# Verify no old color references in new code
grep -rn "rgba(102, 126, 234\|rgba(255, 255, 255, 0.[678])" miniprogram/ 2>/dev/null
# Expected: no output (or only in legacy compat)
```

- [ ] **Step 2: 切换到 main + 合并**

```bash
git checkout main
git pull origin main
git merge dev --no-ff -m "merge: P5 清理任务（死代码 + 未使用 data 字段）"
```

- [ ] **Step 3: 推送**

```bash
git push origin main
git push origin dev
```

---

## P5 验收清单

- [ ] keyword.js 无 commonKeywords
- [ ] setcards.js 无 filter/viewMode
- [ ] sldcards.js 无 searchCode/viewMode
- [ ] odds.js 无死字段
- [ ] index.wxss 无死样式
- [ ] index.js 无死方法
- [ ] 所有页面仍然正常工作（无回归）
- [ ] 暗色主题仍然正常
- [ ] 无 `CODEBUDDY_DEBUG`

---

## 项目最终状态

P1-P5 全部完成：
- 20 个页面视觉统一
- 设计系统完整
- 暗色主题支持
- 死代码清理
- 文档完整（spec × 1 + plan × 5）