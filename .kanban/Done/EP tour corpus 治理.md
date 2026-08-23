# [tag:docs] EP tour corpus 治理

## 目標
tour corpus 從一次性 bootstrap 產物升級為可維護衍生資產：derived/curated 二分、manifest provenance、tour_validate/tour_upgrade/test_tour 三工具、NT 30 條遷移、audit 接線。

## 相關
- EP：ai-analysis/execution-plans/ep-tour-corpus-governance.md
- 能力卡：tour corpus 機械驗證與遷移／test case tour 骨架

## 驗收標準
SM-1~9 全過；三工具測試綠；NT corpus apply 後 validate 綠＋用戶走讀 cross-ref 活 link。

## 備註
T6 mosaic nightly-sequence 行為可選、commit 前用戶 gate。

2026-08-23 結算：T5 test_tour 已除役（M1 D2 user 裁定——承接＝coverage 三軸，見 Backlog/coverage-triaxis-spec.md）；audience 欄廢除（D3）。卡內「三工具」為目標時點歷史描述。
