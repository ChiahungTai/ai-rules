[tag:common]

# EP ai-rules 自家三池對齊（full domain）

## 目標

ai-rules 自家分析側採 `ai-analysis/_tasks/` 任務家（與 mosaic 一致，user 2026-09-02 裁定 full domain）＋退役清債（execution-plans/specs 實體歸 archive）＋放置規則 README 單一源。

## 相關

- EP：`00-tasks/09-02-ai-rules-three-pool/ep.md`（simple 清單；🔴 前置 gate＝muse-plugin-cc session 收尾、00-tasks/ 樹清才動）
- 設計脈絡：mosaic 三池重構（S9 任務家探測已寫進 skills——本任務是 ai-rules 自家 dogfood）

## 驗收標準

- [ ] `fd '00-tasks' . -d 2` 零命中；`ai-analysis/` 含 `_tasks/`＋`archive/`、不含 `execution-plans/`＋`specs/`
- [ ] 新 session `/spec --write` 落 `_tasks/`（探測解析正確）
- [ ] 引用 sweep 白名單外零命中
