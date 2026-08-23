# [tag:feat] coverage 三軸規格對齊

## 目標
test_tour 承接方向的規格化（user 裁決 M1 D2）：覆蓋＝資產間可度量對帳（缺口報告生成器），非 tour 生成。

## 三軸
| 軸 | 問題 | 現況 |
|----|------|------|
| test→source | 程式碼被測試覆蓋嗎 | 已有（pytest --cov、audit-test 覆蓋對稱性） |
| tour→source | call path 被 corpus 覆蓋嗎 | 雛形＝mosaic callstack-v1/coverage-audit.md（手工檔案級） |
| test→tour | tour 聲明的重要路徑有 test cover 嗎 | 無（user 原始意圖） |

## 硬約束（user 裁決語義——不可被 rationalize）
- 產出＝缺口報告（backlog 生成器）＋健康度號碼；**永遠不是 gate**（Goodhart：為覆蓋率灌 tour 稀釋敘事品質）
- 新模組名（非 test_tour 改造——語義已不同）
- 共用引擎構想：call path 索引（chain_tour steps 錨＋CRG call graph 全集）× 覆蓋源比對（tests：pytest --cov 行覆蓋或 CRG transitive；tours：corpus steps 現成）

## 已知需求實證（M2 2026-08-23）
跨鏈雙源型 findings（tolerance 常數雙源定義／`broker_breakdown_as_of` 零 production caller（僅測試消費）／benchmark_scanner inline `Equity()` 繞工廠）在 fresh 生成未重現——**單鏈深挖視角天然難抓跨鏈對照**，tour→source／test→tour 對帳工具的具體需求來源。

## 對齊清單
- 規格 session（獨立）：軸定義、產出格式、健康度號碼語義
- mosaic 舊卡「EP 候選 test-derived tours 與 tour coverage 雙軸」需同步更新（仍描述舊 generator 方向＋優先序排著它——relay）

## 相關
- 源頭：M1 handoff（2026-08-23）＋ `ai-analysis/execution-plans/_done/ep-tour-corpus-governance.md` 結算段
