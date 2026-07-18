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
