# mtgAsk 项目文件整理 Design

**Date**: 2026-07-18
**Status**: Draft (pending user approval)
**Owner**: 梁皓铭
**Scope**: 仓库根目录、`.gitignore`、`docs/screenshots/`、`logs/`、`.playwright-mcp/`

---

## 1. 背景与目标

### 1.1 现状

`git status` 持续显示 14 个未跟踪的根目录调试截图和 `.playwright-mcp/` 目录：

```
?? .playwright-mcp/
?? ai-zoom.png           104 KB    7月 17
?? dice-coin.png          12 KB    7月 15
?? dice-final.png          9 KB    7月 15
?? homepage-test.png     578 KB    7月 15
?? homepage-v3.png        71 KB    7月 15
?? index-full.png        222 KB    7月 17
?? promo-final.png         1 KB    7月 16
?? promo-zoom.png         11 KB    7月 17
?? search-final.png        3 KB    7月 16
?? search-real.png         3 KB    7月 16
?? token-v2.png          104 KB    7月 17
?? tools-final.png        44 KB    7月 15
?? tools-mobile.png       46 KB    7月 15
?? tools-zoom.png         36 KB    7月 17
```

合计约 **1.24 MB**,全部为 Playwright/小程序调试期间在项目根目录临时拍摄的页面截图(共 6 个页面:首页、Dice、Token、Promo、Search、Tools)。

此外还有:

- `.playwright-mcp/` 目录:8 个 console log + 12 个 page YAML(共 38 KB),Playwright MCP 服务器运行时产出
- `docs/.DS_Store`、`logs/.DS_Store`:本地残留
- `logs/ai_judge_20260317.log`、`logs/ai_judge_20260330.log`:2026/03 老日志,202 KB,云函数 `log_service.py` 已将业务日志写入 MySQL,本地副本不再需要
- `scripts/`、`data/`:空目录(空目录不进 git,本身不脏,但留着无意义)

### 1.2 痛点

1. **每天开发循环**都被 `git status` 中 ~14 条噪音条目干扰,容易掩盖真正的新增/修改
2. **测试截图**沉淀到根目录,新人看到会困惑这些 PNG 是不是项目资产
3. `.playwright-mcp/` 频繁被 Playwright MCP 覆写,**无 gitignore 防线**
4. **根目录缺少"PNG 防污规则"**,任何新调试截图都会被 `git add .` 误抓

### 1.3 目标

| 序号 | 目标 | 验收标准 |
|------|------|----------|
| G1 | 根目录的 14 个截图迁移到 `docs/screenshots/<feature>/` | `git status` 不再列出根目录 *.png |
| G2 | `.playwright-mcp/` 在 .gitignore 中消失 | 后续 `git status` 也不列 |
| G3 | 根目录新增调试 PNG 不会再被误跟踪 | `.gitignore` `/docs/screenshots/` 之外的 `/*.png` 永远 tracked-only 通过归档路径 |
| G4 | 仓库视觉净化 | `docs/.DS_Store`、`logs/*.DS_Store` 删除;老 AI Judge 日志清理 |
| G5 | 6 个原子 commit,git log 清晰 | 截图归档、文档、gitignore、DS_Store、日志分别 1 commit |

### 1.4 非目标

- ❌ 不改 `functions/mtgAsk/`、`miniprogram/`、`backend/`、`docs/api/`、`deployment/`、`tests/`、`logo/`、`venv/`、`data/rules/`、`data/mtg/` 等已规范存放的目录内部结构
- ❌ 不引入 cleanup.sh 之类的可复用脚本(YAGNI:本次是一次性清理)
- ❌ 不重新组织 `docs/` 顶层结构(已经井然有序:`ARCHITECTURE.md`、`INTERACTION_DESIGN.md` 等命名规整)
- ❌ 不删 `venv/` —— 已 gitignore 不影响 status,真要清理留作以后磁盘管理

---

## 2. 设计

### 2.1 截图归档结构

```
docs/screenshots/
├── README.md
├── homepage/
│   ├── test.png             ← 原 homepage-test.png
│   ├── v3.png               ← 原 homepage-v3.png
│   └── full.png             ← 原 index-full.png (P5 主页全屏)
├── dice/
│   ├── coin.png             ← 原 dice-coin.png
│   └── final.png            ← 原 dice-final.png
├── token/
│   └── v2.png               ← 原 token-v2.png
├── promo/
│   ├── final.png            ← 原 promo-final.png
│   └── zoom.png             ← 原 promo-zoom.png
├── search/
│   ├── final.png            ← 原 search-final.png
│   └── real.png             ← 原 search-real.png
└── tools/
    ├── final.png            ← 原 tools-final.png
    ├── mobile.png           ← 原 tools-mobile.png
    └── zoom.png             ← 原 tools-zoom.png
```

**命名规则**:扁平的 `<state>.png`(test / v3 / final / mobile / zoom 等),不带日期或版本号 —— 这些文件已经是历史快照,文件名即语义。

**`index-full.png` 归类决策**:经排查文件名(`index-full.png` 而非 `homepage-full.png`)模糊,但拍摄时间(7月 17)紧跟主页 P5 视觉升级(参见 commit `7993762`),判定为 P5 期间主页完整长截图。归档到 `homepage/full.png`。

### 2.2 `.gitignore` 增量

在 `/Users/lianghaoming/cbworkplace/.gitignore` 末尾追加:

```gitignore
# 浏览器 MCP 测试产物
.playwright-mcp/

# 根目录调试截图(只允许出现在 docs/screenshots/ 下)
/*.png
```

`/*.png` 仅锚定仓库根,不影响 `docs/screenshots/**/*.png`。不需要白名单条目。

### 2.3 删除清单

| 路径 | 性质 | 操作 |
|------|------|------|
| `docs/.DS_Store` | 本地残留 | 本地 `rm`(git 未跟踪,无需 git 命令) |
| `logs/.DS_Store` | 本地残留 | 本地 `rm` |
| `logs/ai_judge_20260317.log` | 老 AI Judge 日志 | `git rm` + 本地 `rm`(需确认是否曾经 tracked) |
| `logs/ai_judge_20260330.log` | 老 AI Judge 日志 | `git rm` + 本地 `rm`(同上) |

`.DS_Store` 在 git 中已被 ignore 但仍是本地脏文件;`logs/*.log` 已在 `.gitignore` 中但历史上某次 `git add -f` 可能把日志纳入过 tracked,实施前需要 `git ls-files logs/` 验证。

### 2.4 空目录

`scripts/`、`data/`:空目录 git 不跟踪。**不动**,除非用户后续要求清理。空目录清理属于另一个独立问题,本 spec 不覆盖。

### 2.5 `docs/screenshots/README.md` 约定

```markdown
# 截图归档

## 用途

历史调试截图归档。仓库在 P4/P5 视觉升级期间通过 Playwright 拍摄页面快照,以根目录散落 PNG 形式保存。

整理后归档于此,既保留历史又避免污染根目录 `git status`。

## 目录约定

- `homepage/`:主页相关
- `dice/`:Dice 页(随机硬币/骰子)
- `token/`:Token 页(攻防指示物)
- `promo/`:Promo 入口(Tools 卡片)
- `search/`:搜索页
- `tools/`:Tools 页(主页→Tools)

## 命名约定

`<state>.png`,state 为:
- `test` — 早期测试版
- `v2` / `v3` — 版本号
- `final` — 最终视觉定稿
- `mobile` — 移动尺寸
- `zoom` — 局部放大对照
- `real` — 真实场景截图
- `full` — 全屏长截图
- `coin` — 硬币特写

## 历史贡献

- 2026-07-15(初次):
  - homepage/test.png、homepage/v3.png
  - dice/coin.png、dice/final.png
  - tools/final.png、tools/mobile.png
- 2026-07-16:
  - promo/final.png
  - search/final.png、search/real.png
- 2026-07-17:
  - homepage/ai-zoom.png (原 ai-zoom.png)
  - homepage/full.png (原 index-full.png)
  - promo/zoom.png
  - token/v2.png
  - tools/zoom.png

新截图若要归档,请在此 README 的"历史贡献"段追加一行。
```

---

## 3. 实施步骤

### 3.1 提交粒度(6 个原子 commit)

```
commit 6: chore: 删除 logs/ 中 2026/03 旧 AI Judge 日志
commit 5: chore: 清理 docs/ 和 logs/ 的 .DS_Store 残留
commit 4: chore: .gitignore 添加 .playwright-mcp/ 和根目录 *.png 规则
commit 3: docs: 添加 docs/screenshots/README.md 归档约定
commit 2: chore: 归档 dice/token/promo/search/tools 测试截图
commit 1: chore: 归档主页测试截图到 docs/screenshots/homepage/
```

按"主页最优先 → 其他子目录 → 文档 → gitignore → 清理"的顺序,git log 自下而上读出"先移物→立规→清垃圾"的故事线。提交时间顺序倒过来:commit 1 是首个动作,commit 6 是收尾。

### 3.2 详细步骤(每个 commit)

**Commit 1: 归档主页(4 个文件)**
```bash
mkdir -p docs/screenshots/homepage
git mv ai-zoom.png        docs/screenshots/homepage/ai-zoom.png
git mv homepage-test.png  docs/screenshots/homepage/test.png
git mv homepage-v3.png    docs/screenshots/homepage/v3.png
git mv index-full.png     docs/screenshots/homepage/full.png
```

| 原文件 | 归档位置 |
|--------|----------|
| ai-zoom.png       | docs/screenshots/homepage/ai-zoom.png |
| homepage-test.png | docs/screenshots/homepage/test.png |
| homepage-v3.png   | docs/screenshots/homepage/v3.png |
| index-full.png    | docs/screenshots/homepage/full.png |

> **归类决策**:`ai-zoom.png` 拍摄时间 7月 17 与主页 P5 视觉升级(commit `7993762`)同期,推测为主页 AI 入口放大对照,归档到 `homepage/ai-zoom.png`。`index-full.png` 同理归档到 `homepage/full.png`,作为 P5 主页全屏长截图。

**Commit 2: 归档 dice/token/promo/search/tools**

按 §2.1 表格,10 个文件逐个 `git mv`(dice 2 + token 1 + promo 2 + search 2 + tools 3)。

**Commit 3: README**

`Write docs/screenshots/README.md`,内容见 §2.5。

**Commit 4: .gitignore 增量**

编辑 `.gitignore`,末尾追加 §2.2 的两段规则。

**Commit 5: DS_Store 清理**

```bash
# 检查是否曾经被误跟踪
git ls-files docs/.DS_Store logs/.DS_Store
# 若未 tracked,直接本地 rm
rm -f docs/.DS_Store logs/.DS_Store
# 若已 tracked(可能性低),则 git rm --cached
```

**Commit 6: 旧日志清理**

```bash
git ls-files logs/  # 验证是否 tracked
rm logs/ai_judge_20260317.log logs/ai_judge_20260330.log
```

执行前先跑 `git log --follow logs/ai_judge_20260317.log --oneline` 确认这些日志的入库历史 — 如果曾经 tracked,就用 `git rm`;如果从未 tracked,就直接 `rm`。

---

## 4. 测试与验收

| 测试 ID | 描述 | 命令 / 操作 | 通过标准 |
|---------|------|-------------|----------|
| T1 | 根目录无 PNG 残留 | `ls *.png` | 无输出 |
| T2 | 截图全归档完毕 | `find docs/screenshots -name "*.png" \| wc -l` | 输出 14 |
| T3 | `.playwright-mcp/` 不在 git status | `git status --ignored` 中包含该目录,但 `git status` 不显示 | 通过 |
| T4 | 新增根目录调试 PNG 不被误跟踪 | `touch test.png && git status` | 无 `?? test.png` |
| T5 | DS_Store 清理完毕 | `find docs/ logs/ -name ".DS_Store"` | 无输出 |
| T6 | 旧日志清理完毕 | `ls logs/*.log` | 无输出 |
| T7 | git log 6 commit 完整 | `git log --oneline -6` | 含 §3.1 全部 6 个 commit |
| T8 | README 存在并可读 | `head docs/screenshots/README.md` | 看到"用途"段落 |
| T9 | .gitignore 增量生效 | `grep -A 2 "playwright" .gitignore` | 看到 `.playwright-mcp/` |
| T10 | 仓库其余功能不受影响 | `git status` 末尾 | 仅显示新 commit 引入的状态变化,无回归 |

---

## 5. 风险与缓解

| 风险 | 概率 | 影响 | 缓解 |
|------|------|------|------|
| `git mv` 失败(目标已存在) | 低 | 单文件迁移失败 | 先 `rm -rf docs/screenshots/`,再重新 mkdir 每个子目录 |
| 旧日志曾经 tracked 触发 `git rm` 与其他 commit 顺序冲突 | 低 | git 历史被复杂化 | 拆为两个 commit:先 `git rm --cached` 解除跟踪,再 `rm` 物理删除 |
| 未来误归档到错误子目录 | 低 | 归档混乱 | README 显式写明新截图规则,人工 review |
| 用户未来用 `git add .` 抓根目录 PNG | 低 | .gitignore 被绕过 | 显式 `*.png` 是 git 通配规则,根目录 `/` 锚定,行为可靠 |
| `index-full.png` 归类错误(非主页) | 低 | 历史归类不可逆 | 实施前可由用户人工查看 `index-full.png` 内容确认(用户已认可) |

---

## 6. 范围之外 / 后续可考虑

- **截图版本对比工具**:不做。YAGNI。
- **常规 cleanup.sh**:不做。本次是一次性清理。
- **`docs/` 顶层结构重组**:不做。当前顶层已规范(`ARCHITECTURE*.md`、`INTERACTION_DESIGN.md` 等)。
- **`.playwright-mcp/` 定期清理**:可通过系统 crontab(用户系统级配置)实现,本次 spec 不覆盖。
- **空目录 `scripts/`、`data/` 的清理**:不属于本 spec。
- **`miniprogram/images/user_avatar.png` + `user_avatar.avif` 孤儿资源清理**:发现这两个文件存在但代码零引用(`grep -rln "user_avatar" miniprogram/` 无输出)。本 spec 不处理,留作独立后续 PR(用户决定)。涉及文件:
  - `miniprogram/images/user_avatar.png`
  - `miniprogram/images/user_avatar.avif`
  注意:`mtgask_logo.png` **必须保留**(`pages/agent/agent.js` + `pages/index/index.wxml` 正使用)。

---

## 7. 待最终核实

| 事项 | 验证方法 | 阻塞? |
|------|----------|--------|
| `logs/*.log` 是否曾经 tracked? | `git ls-files logs/` | 不阻塞(若是 tracked,commit 6 改用 `git rm`) |
| `.DS_Store` 是否曾经 tracked? | `git ls-files docs/.DS_Store logs/.DS_Store` | 不阻塞(若是 tracked,commit 5 改用 `git rm --cached`) |
| 确认 `index-full.png` 是主页全屏 | 用户已通过上面方案 §2.1 决定归入 `homepage/full.png` | 已解决 |
| `ai-zoom.png` 是主页 AI 入口 | 用户已通过上面方案 §3.2 决定归入 `homepage/ai-zoom.png` | 已解决 |
