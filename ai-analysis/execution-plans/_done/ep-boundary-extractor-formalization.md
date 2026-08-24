# EP：pyo3 boundary extractor 正式化（吸收 mosaic P1 原型進 code_reality）

> **ep_type**: implementation
> **狀態**: ✅ **已收案（2026-08-24）——驗收閉環記錄**
> **baseline**: `1c9222a206e70c287172629d23e84c8329fcdf1c`（EP 建立當下）
> **結局**: EP 對過時快照起草——段 1-3 的實作**早已由 08-22 遷移弧完成**
> （`5800806` 九工具遷入＋`0633263` 審查修正輪：mosaic P1 原型→mosaic 工具→
> ai-rules 兩手吸收）；段 4 驗收由 NT session 2026-08-24 實測閉環（見下）。
> 起草 session（sess_53cdb187）已認錯：「既有 NT scoped 簡版」描述錯誤。

## 驗收記錄（NT HEAD `9133b89` 實測，2026-08-24）

- **10,180 邊**／class **92.3%**（627/679，≥90 ✓；16 custom_data! 巨集已知殘差）／
  method **87.2%**（9,443/10,834，優於原型 84.6%；credential 欄位殘差已知構成）／
  function **孤兒 0/0**（與原型 coverage.json 一致）
- **LiveNode 3 case 全命中**：class NAME_MATCH（mod.rs:158↔pyi:230＝NT tour 錨）、
  build PYO3_NAME_RENAME（node.rs:103）、LiveNodeBuilder 雙宣告雙邊
- **F3 相容**：`code_reality.boundary LiveNode` 22 edges，命令形態不變
- **SM-6 冪等**：~~位元級~~→**內容級冪等**（boundary_edges 全表 digest 兩次一致
  `1e872d9e`；位元級差異＝meta.created_at 時間戳——provenance 本性，起草端措辭過嚴已更正）
- **原型對照自洽**：+499 邊＝method matched 增量（8,944→9,443），denominator +261
  ＝正式版規則更全——無未解釋殘差
- 七規則逐行命中（boundary_build.py :279/:227/:229/:613/:201/:385/:352）；
  match_kind 六分類齊；13 tests 含四事故 regression（SM-8，對照 gap-prototypes §1.6）

## 設計定案（NT＋ai-rules 雙方一致，2026-08-24）

1. sidecar 預設路徑**維持** `~/.mosaic/code-reality/boundary/`（commit-keyed＝自動
   歷史、對遷移 PROVENANCE 加分；跨 repo sidecar home 為遷移 EP 凍結慣例；
   mosaic M4 要 in-repo 位置走 `--out-dir` 指定）
2. 覆蓋率報告**維持** stdout＋meta JSON 常駐，不加獨立 `--report` flag（YAGNI）

## Known Concern（記錄不擋）

- sidecar commit-keyed 檔案會累積（`~/.mosaic/code-reality/boundary/`）——遲需清理
  策略（如保留最新 N 個）；已記入 boundary_build docstring
- 文件勘誤：本 EP 原文寫 `_meta`、實際表名 `meta`（歸檔版已全文更正）

## 跨軌成果

- mosaic **M4 消費端可動工**（sidecar schema 已定且 NT 實測：表結構/meta 欄位/
  --out-dir 語義）
- mosaic `.agent-tmp/research/p1/` 可清理（吸收驗證完畢）；`p2/` 已複製進
  ai-rules `.agent-tmp/research/p2/`（M3 hazard 材料保全）
- 原文（起草版）隨收案以本檔取代；規格源＝mosaic
  `ai-analysis/reports/code-reality-gap-prototypes.md` §1/§4
