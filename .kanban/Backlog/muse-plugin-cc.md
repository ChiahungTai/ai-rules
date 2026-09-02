# [tag:plugins] muse-plugin-cc 委派 plugin（ZCode/CC 雙端）

## 目標
致敬 codex/grok-build plugin-cc（皆 Apache-2.0）開發 Muse Code 委派 plugin：headless `muse exec` 委派任務、結構化 review、runs 管理、訂閱制計費（bridge 剝除 `META_API_KEY`）。

## 相關
- EP：`00-tasks/09-02-muse-plugin-cc/ep.md`（段落 0 研究：同目錄 `research.md`）
- 新 repo `~/Github/muse-plugin-cc`（standalone，照兩上游 `-cc` 先例）
- 上游：openai/codex-plugin-cc、xai-org/grok-build-plugin-cc
- 文檔鏡像：`ref-docs/harness/meta/`（92 頁）

## 驗收標準
- S1 三項致命先驗 POC 過（muse CLI 可跑、headless 走訂閱計費、--json 可解析）
- 五 UC 落地：委派／review／runs／setup／雙端發佈（marketplace）
- 雙端（ZCode+CC）實際安裝可用（消費端驗證，缺任一端不算完成）

## 備註
已裁定：不支援 META_API_KEY（純訂閱）、--yolo 呼叫端 opt-in、--trust-workspace 獨立於 --yolo、預設模型 pin `muse-spark-1.2`（standard tier，CLI 預設不穩定）。R1/R3 已過；R2 待 user dashboard 核對（4 錨點）。EP review 雙 agent 全數寫回（2026-09-02）。
