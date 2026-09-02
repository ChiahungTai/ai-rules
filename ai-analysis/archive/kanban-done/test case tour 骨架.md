# [tag:docs] test case tour 骨架

## 目標
tests 作為 tour source：AST 枚舉 → 每 test 檔一條 tour、每 test 一步（pattern 錨 def test_*＋>> pytest 可執行步）——斷點③拆小的機械替代。

## 相關
- EP：ep-tour-corpus-governance（T5）

## 驗驗標準
對 mosaic tests/ 子目錄實跑：步數＝test 數、validate 綠、>> 行符合 SHELL_SCRIPT_PATTERN。
