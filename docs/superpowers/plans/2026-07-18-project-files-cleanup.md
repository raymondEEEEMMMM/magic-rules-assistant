# 项目文件整理 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把 14 个根目录测试截图归档到 `docs/screenshots/<feature>/`,把 `.playwright-mcp/` 和根目录调试 PNG 加入 .gitignore,清理 .DS_Store 残留与 2026/03 老旧 AI Judge 日志,使 `git status` 整洁。

**Architecture:** 6 个原子 commit,每 commit 一个 git 历史里程碑(主页归档 → 其他子目录 → 文档 → gitignore → DS_Store → 旧日志)。每步可独立回滚。本质是 git 仓库卫生,非逻辑重构。

**Tech Stack:** git 2.x, bash, Playwright MCP(产出副作用)

**Spec:** `docs/superpowers/specs/2026-07-18-project-files-cleanup-design.md`

---

## File Map

### 新增文件(`git mv`)

| 源(untracked) | 目标(tracked) |
|---------------|---------------|
| `ai-zoom.png` | `docs/screenshots/homepage/ai-zoom.png` |
| `homepage-test.png` | `docs/screenshots/homepage/test.png` |
| `homepage-v3.png` | `docs/screenshots/homepage/v3.png` |
| `index-full.png` | `docs/screenshots/homepage/full.png` |
| `dice-coin.png` | `docs/screenshots/dice/coin.png` |
| `dice-final.png` | `docs/screenshots/dice/final.png` |
| `token-v2.png` | `docs/screenshots/token/v2.png` |
| `promo-final.png` | `docs/screenshots/promo/final.png` |
| `promo-zoom.png` | `docs/screenshots/promo/zoom.png` |
| `search-final.png` | `docs/screenshots/search/final.png` |
| `search-real.png` | `docs/screenshots/search/real.png` |
| `tools-final.png` | `docs/screenshots/tools/final.png` |
| `tools-mobile.png` | `docs/screenshots/tools/mobile.png` |
| `tools-zoom.png` | `docs/screenshots/tools/zoom.png` |

### 新增文件(Write)

- `docs/screenshots/README.md`

### 修改文件

- `.gitignore`(末尾追加)

### 删除文件

- `docs/.DS_Store`(本地)
- `logs/.DS_Store`(本地)
- `logs/ai_judge_20260317.log`(本地,可能需 `git rm`)
- `logs/ai_judge_20260330.log`(本地,可能需 `git rm`)

---

## Task 0: 前置前置状态验证

**Files:** none(只读检查)

- [ ] **Step 1: 确认当前分支**

```bash
git branch --show-current
```

预期:输出 `dev`。如果是其他分支,**立即停止**并报告给用户。

- [ ] **Step 2: 确认工作区干净(只有 untracked PNG + .playwright-mcp/)**

```bash
git status -s
```

预期输出(恰好 15 行):
```
 .playwright-mcp/
 ai-zoom.png
 dice-coin.png
 dice-final.png
 homepage-test.png
 homepage-v3.png
 index-full.png
 promo-final.png
 promo-zoom.png
 search-final.png
 search-real.png
 token-v2.png
 tools-final.png
 tools-mobile.png
 tools-zoom.png
```

**判定**:若有其他修改条目(staged/unstaged),**立即停止**并报告。用户需要先 stash 或 commit 现有改动。

- [ ] **Step 3: 验证 14 个 PNG 全部 untracked**

```bash
git ls-files | grep -E "^(ai-zoom|homepage-test|homepage-v3|index-full|dice-coin|dice-final|token-v2|promo-final|promo-zoom|search-final|search-real|tools-final|tools-mobile|tools-zoom)\.png$" || echo OK_NO_TRACKED_PNG
```

预期输出:`OK_NO_TRACKED_PNG`。如果有任何匹配,**立即停止**——这些文件不该被归档,需要查历史。

- [ ] **Step 4: 检查旧 AI Judge 日志是否曾经 tracked**

```bash
git ls-files logs/ | grep -E "ai_judge_202603(17|30)\.log" || echo NOT_TRACKED
```

预期输出:`NOT_TRACKED`(这两文件已 gitignore 但 `git ls-files` 只列 tracked,所以应该 not_tracked)。

**判定**:若意外出现文件名,**调整 Task 6 改用 `git rm`**。若输出 `NOT_TRACKED`,后续 Task 6 用 `rm`。

---

## Task 1: 归档主页 4 个测试截图

**Files:**
- Move(untracked → tracked via git): `docs/screenshots/homepage/ai-zoom.png`, `test.png`, `v3.png`, `full.png`

- [ ] **Step 1: 创建目标目录**

```bash
mkdir -p docs/screenshots/homepage
```

- [ ] **Step 2: 移动 4 个主页截图**

```bash
cd /Users/lianghaoming/cbworkplace
mv ai-zoom.png        docs/screenshots/homepage/ai-zoom.png
mv homepage-test.png  docs/screenshots/homepage/test.png
mv homepage-v3.png    docs/screenshots/homepage/v3.png
mv index-full.png     docs/screenshots/homepage/full.png
```

注意:`mv` 而非 `git mv`,因为这些文件当前 untracked(无 git 跟踪状态)。`git add` 时直接识别为新增。

- [ ] **Step 3: 验证文件已就位**

```bash
ls -la docs/screenshots/homepage/
```

预期输出 4 个文件,大小与修改时间与原根目录 14 个 PNG 对应一致。

- [ ] **Step 4: 验证根目录已无主页类 PNG**

```bash
ls ai-zoom.png homepage-test.png homepage-v3.png index-full.png 2>&1
```

预期输出(每个文件都报"没有那个文件或目录"):
```
ls: ai-zoom.png: No such file or directory
ls: homepage-test.png: No such file or directory
ls: homepage-v3.png: No such file or directory
ls: index-full.png: No such file or directory
```

- [ ] **Step 5: git add + git status 预检**

```bash
git add docs/screenshots/homepage/
git status -s
```

预期(新增 4 个文件 staged):
```
A  docs/screenshots/homepage/ai-zoom.png
A  docs/screenshots/homepage/full.png
A  docs/screenshots/homepage/test.png
A  docs/screenshots/homepage/v3.png
```

- [ ] **Step 6: Commit**

```bash
git commit -m "chore: 归档主页测试截图到 docs/screenshots/homepage/ (ai-zoom/test/v3/full)"
```

---

## Task 2: 归档 dice/token/promo/search/tools 10 个测试截图

**Files:**
- Move: 10 个文件到 `docs/screenshots/{dice,token,promo,search,tools}/`

- [ ] **Step 1: 创建所有目标子目录**

```bash
mkdir -p docs/screenshots/{dice,token,promo,search,tools}
```

- [ ] **Step 2: 移动 dice/token/promo/search 子目录**

```bash
cd /Users/lianghaoming/cbworkplace
mv dice-coin.png      docs/screenshots/dice/coin.png
mv dice-final.png     docs/screenshots/dice/final.png
mv token-v2.png       docs/screenshots/token/v2.png
mv promo-final.png    docs/screenshots/promo/final.png
mv promo-zoom.png     docs/screenshots/promo/zoom.png
mv search-final.png   docs/screenshots/search/final.png
mv search-real.png    docs/screenshots/search/real.png
```

- [ ] **Step 3: 移动 tools 子目录**

```bash
cd /Users/lianghaoming/cbworkplace
mv tools-final.png    docs/screenshots/tools/final.png
mv tools-mobile.png   docs/screenshots/tools/mobile.png
mv tools-zoom.png     docs/screenshots/tools/zoom.png
```

- [ ] **Step 4: 验证所有 10 个文件就位**

```bash
ls docs/screenshots/dice/ docs/screenshots/token/ docs/screenshots/promo/ docs/screenshots/search/ docs/screenshots/tools/
```

预期:dice 2 个、token 1 个、promo 2 个、search 2 个、tools 3 个,共 10 个。

- [ ] **Step 5: 验证根目录已无调试 PNG**

```bash
ls *.png 2>&1
```

预期输出:`ls: *.png: No such file or directory`

- [ ] **Step 6: git add + commit**

```bash
git add docs/screenshots/
git commit -m "chore: 归档 dice/token/promo/search/tools 测试截图 (10 个)"
```

---

## Task 3: 添加 docs/screenshots/README.md 归档约定

**Files:**
- Create: `docs/screenshots/README.md`

- [ ] **Step 1: 写 README.md**

`Write` `/Users/lianghaoming/cbworkplace/docs/screenshots/README.md`:

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
- `ai-zoom` — AI 入口特写

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

- [ ] **Step 2: 验证 README 内容完整**

```bash
wc -l docs/screenshots/README.md
```

预期:行数 ≥ 25。

- [ ] **Step 3: git add + commit**

```bash
git add docs/screenshots/README.md
git commit -m "docs: 添加 docs/screenshots/README.md 归档约定"
```

---

## Task 4: .gitignore 追加 .playwright-mcp/ 和根目录 *.png

**Files:**
- Modify: `/Users/lianghaoming/cbworkplace/.gitignore`

- [ ] **Step 1: 读取 .gitignore 末尾**

```bash
tail -5 .gitignore
```

预期看到 `# 头脑风暴会话产物` + `.superpowers/`(确认已有该段,且本任务追加在其后)。

- [ ] **Step 2: 追加两段规则**

```bash
cat >> .gitignore << 'EOF'

# 浏览器 MCP 测试产物
.playwright-mcp/

# 根目录调试截图(只允许出现在 docs/screenshots/ 下)
/*.png
EOF
```

- [ ] **Step 3: 验证追加成功**

```bash
tail -7 .gitignore
```

预期输出最后 7 行:
```
(s之前的几行)
# 头脑风暴会话产物
.superpowers/

# 浏览器 MCP 测试产物
.playwright-mcp/

# 根目录调试截图(只允许出现在 docs/screenshots/ 下)
/*.png
```

- [ ] **Step 4: 验证 .playwright-mcp/ 已 ignore**

```bash
git check-ignore -v .playwright-mcp/page-2026-07-17T02-56-15-186Z.yml
```

预期输出类似:
```
.gitignore:XX:.playwright-mcp/
.playwright-mcp/page-2026-07-17T02-56-15-186Z.yml
```

**判定**:若无输出,说明规则未生效 — 检查语法(`/` 前空格、`*.png` 后无注释)。

- [ ] **Step 5: 验证根目录 PNG 已 ignore(用防污模拟)**

```bash
cd /Users/lianghaoming/cbworkplace
touch /tmp/zzz-test-png.png
git check-ignore -v /tmp/zzz-test-png.png 2>&1 || echo "NOT_IGNORED: full path test only"
cd /Users/lianghaoming/cbworkplace
touch _test_root_png.png
git check-ignore -v _test_root_png.png
rm _test_root_png.png
```

预期:对 `_test_root_png.png` 输出:
```
.gitignore:XX:/*.png
_test_root_png.png
```

**注意**:`/tmp/...` 因为不在仓库内,`git check-ignore` 不处理(预期 NOT_IGNORED)。只关心仓库根目录创建的文件。

- [ ] **Step 6: 验证 docs/screenshots/ 内 PNG 不被忽略**

```bash
git check-ignore -v docs/screenshots/homepage/test.png
```

预期:非零退出码 + 无 stdout(或:`NOT_IGNORED` 字样)。

- [ ] **Step 7: git add + commit**

```bash
git add .gitignore
git commit -m "chore: .gitignore 添加 .playwright-mcp/ 和根目录 *.png 规则"
```

---

## Task 5: 清理 docs/ 和 logs/ 的 .DS_Store 残留

**Files:**
- Delete(本地): `docs/.DS_Store`, `logs/.DS_Store`

- [ ] **Step 1: 验证 .DS_Store 文件存在**

```bash
ls -la docs/.DS_Store logs/.DS_Store 2>&1
```

预期:`-rw-r--r-- ... .DS_Store`(两个文件都列出来)。若 `.DS_Store` 不存在,跳过整个任务(Task 5 已无内容,无需 commit)。

- [ ] **Step 2: 验证 .DS_Store 未 tracked(虽然 gitignore 兜底)**

```bash
git ls-files docs/.DS_Store logs/.DS_Store 2>&1
```

预期:无输出。若有输出,**立即停止**——文件被追踪,需 `git rm --cached`,可能需新增 Task。

- [ ] **Step 3: 本地删除 .DS_Store**

```bash
rm -f docs/.DS_Store logs/.DS_Store
```

- [ ] **Step 4: 验证 .DS_Store 不再存在**

```bash
ls docs/.DS_Store logs/.DS_Store 2>&1
```

预期(每个文件都报"没有那个文件或目录"):
```
ls: docs/.DS_Store: No such file or directory
ls: logs/.DS_Store: No such file or directory
```

- [ ] **Step 5: 验证 git 工作区状态干净**

```bash
git status -s
```

预期:无任何修改或新增条目。

**判定**:若有 `D docs/.DS_Store` 之类,说明前面有错误,需要回退。

- [ ] **Step 6: 不需要 commit(纯本地删除)**

跳过 git 操作。本 commit 不存在,因为没有 tracked 文件变化。

注:若 Task 5 没有 .DS_Store 文件或全为本地未跟踪,跳过整个 commit。

---

## Task 6: 删除 2026/03 旧 AI Judge 日志

**Files:**
- Delete(本地,可能需 git rm): `logs/ai_judge_20260317.log`, `logs/ai_judge_20260330.log`

- [ ] **Step 1: 验证日志文件存在**

```bash
ls -la logs/ai_judge_20260317.log logs/ai_judge_20260330.log 2>&1
```

预期:两个文件都列出来。若不存在,跳过整个任务(Task 6 无内容)。

- [ ] **Step 2: 检查跟踪状态**

```bash
git ls-files logs/ai_judge_20260317.log logs/ai_judge_20260330.log
```

预期:**无输出**(因为 `.gitignore` 含 `logs/`)。但如果意外曾被 `git add -f` 加入,这里会出现文件名。

- [ ] **Step 3: 判定删除方式**

```bash
if git ls-files logs/ai_judge_20260317.log logs/ai_judge_20260330.log | grep -q .; then
  echo "TRACKED_USE_GIT_RM"
else
  echo "UNTRACKED_USE_RM"
fi
```

- [ ] **Step 4a: 若输出 `UNTRACKED_USE_RM`(预期分支)**

```bash
rm -f logs/ai_judge_20260317.log logs/ai_judge_20260330.log
```

- [ ] **Step 4b: 若输出 `TRACKED_USE_GIT_RM`(意外情况)**

```bash
git rm logs/ai_judge_20260317.log logs/ai_judge_20260330.log
# 不需要额外 rm,git rm 会删除 working copy
```

**判定**:本情况概率极低,但若发生,继续走后续步骤(commit 信息和预期会变化)。

- [ ] **Step 5: 验证日志不存在**

```bash
ls logs/ai_judge_20260317.log logs/ai_judge_20260330.log 2>&1
```

预期:每个文件都报"没有那个文件或目录"。

- [ ] **Step 6: 若是 4a 路径,无 git 操作(纯本地删除)**

```bash
git status -s | grep -E "ai_judge_202603(17|30)" && echo "ERROR: still tracked" || echo "OK"
```

预期输出:`OK`。

- [ ] **Step 7: 若是 4b 路径,commit 删除**

```bash
git commit -m "chore: 删除 logs/ 中 2026/03 旧 AI Judge 日志 (20260317、20260330)"
```

预期 commit message 包含 commit hash。

**判定**:若 4a 路径(更可能),跳过 Step 7,无需 commit。

---

## Task 7: 全局验收

**Files:** none(只读验证)

- [ ] **Step 1: git log 显示 4-5 个新 commit**

```bash
git log --oneline -8
```

预期:看到以下 commit(顺序依提交时间):

```
(预计 commit 4-6 中部分存在,commit 1-3 必有)
docs: 添加 docs/screenshots/README.md 归档约定
chore: 归档 dice/token/promo/search/tools 测试截图 (10 个)
chore: 归档主页测试截图到 docs/screenshots/homepage/ (ai-zoom/test/v3/full)
chore: .gitignore 添加 .playwright-mcp/ 和根目录 *.png 规则
chore: 删除 logs/ 中 2026/03 旧 AI Judge 日志 (20260317、20260330)(可选)
docs: 添加项目文件整理设计 spec... (前述 spec 已 commit)
docs(spec): 修正文件计数...
docs(spec): 补 README 历史列表...
docs(spec): 补充 user_avatar 孤儿资源...
```

- [ ] **Step 2: 工作区干净**

```bash
git status
```

预期:无任何 untracked/modified/staged 条目(`.playwright-mcp/` 在 `git status --ignored` 里才出现)。

- [ ] **Step 3: 根目录无 PNG**

```bash
find . -maxdepth 1 -name "*.png" -not -path "./.git/*"
```

预期:**无输出**。

- [ ] **Step 4: docs/screenshots/ 包含 14 个 PNG**

```bash
find docs/screenshots -name "*.png" | wc -l
```

预期输出:`14`。

- [ ] **Step 5: README 存在并可读**

```bash
head -3 docs/screenshots/README.md
```

预期输出前 3 行:
```
# 截图归档

## 用途
```

- [ ] **Step 6: .gitignore 含规则**

```bash
grep -E "^\.playwright-mcp|^/\*\.png" .gitignore
```

预期两行:
```
.playwright-mcp/
/*.png
```

- [ ] **Step 7: .playwright-mcp/ 不在 git status**

```bash
git status --ignored | grep -A 1 "Ignored files" | head -20
```

预期:在"Ignored files"段下看到 `.playwright-mcp/`(确认 ignore 生效,但默认 status 不显示)。

- [ ] **Step 8: logs/ 清理验证**

```bash
ls logs/*.log 2>&1
```

预期:`ls: logs/*.log: No such file or directory` 或 `logs/*.log` 不匹配任何文件。

- [ ] **Step 9: docs/ 和 logs/ 无 .DS_Store**

```bash
find docs logs -name ".DS_Store" 2>/dev/null | wc -l
```

预期输出:`0`。

- [ ] **Step 10: miniprogram/images/ 不受影响**

```bash
ls miniprogram/images/*.png
```

预期:看到 `miniprogram/images/mtgask_logo.png` 和 `miniprogram/images/user_avatar.png`(gitignore `/*.png` 锚定仓库根,不影响子目录)。

---

## 验收总结

✅ Task 0–6 全部通过 → 项目文件整理完成。
✅ Task 7 全部 10 步验收通过 → 整体符合 spec 1.3 节 G1–G5 目标。
❌ 任何一步失败 → 回滚对应 commit(`git revert <hash>`),回到 Task 0 状态重试。

---

## 风险与回滚

| 风险 | 回滚方式 |
|------|----------|
| 单个 commit 不需要 | `git revert <hash>` 或 `git reset --soft HEAD~N; git reset HEAD .` |
| 误归档文件名/位置 | `git mv` 反向,然后 commit "fix: 撤回错误归档" |
| `.gitignore` 规则遗漏 | `git revert <commit_hash_of_task_4>` |
| Task 5/6 删错文件 | `git ls-files <path>` 检查;若曾 tracked,用 `git checkout HEAD -- <path>`;若未 tracked,从备份/Time Machine 恢复 |

---

## 范围之外(本计划不执行)

- `miniprogram/images/user_avatar.png` + `user_avatar.avif` 孤儿资源清理(独立 PR 处理,见 spec §6)
- 空目录 `scripts/`、`data/` 清理(不属于本 spec)
- `.playwright-mcp/` 内容清理(纯本地,通过系统 crontab 或手动清理)
- 定期 cleanup.sh 脚本(YAGNI)
