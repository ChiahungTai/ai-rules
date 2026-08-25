# UC-2：caller 邊查詢（callers/call_edges/closure）

[tag:code-reality]

## 目標
DEF-enc containment 推導 caller 邊（96.9% 歸屬已證）：ref occ 行→同檔最內層 fn DEF→caller symbol。`scip_refs` 長 `--callers`/`--closure` 模式＋sqlite fn_defs 表（schema bump）。

## 相關
- EP 段 2：`ai-analysis/execution-plans/ep-code-reality-repo-mcp.md`
- 機制證據：`ai-analysis/reports/rust-precision-ecosystem-research.md` §2
- 消費者：hub_refs/hazard 可刪判斷（v1 資料源升級）、graph 層邊材料（v1 S6）

## 驗收標準
- `EventStoreLifecycle.open --callers`＝17 callers（trait impl open()＋16 test fn）＝LSP incomingCalls 同名單（三源一致）
- single-line span（3 元素 enc，巨集生成 fn）支援——≥35 顆反例不誤殺
- closure BFS 環偵測＋按檔聚合；sqlite 路徑秒級
- 既有 query/audit 輸出 byte-identical（NT 契約）

## 備註
refs＝所有 non-DEF occ、不可當呼叫數解讀；callers＝歸屬子集（item-level remainder 分離標注）

## 收案（2026-08-26）
能力已交付——載體＝code-reality repo R3（`8cacbce` feat(rust): caller edges + closure，DEF-enc attribution＋fn_defs sidecar；NT 基準經 46a9c23 EP 裁定為 16 callers）。本卡以能力交付論結；Python 版 S2 形態（17 callers 三源）由 Rust parity 測試承接。
