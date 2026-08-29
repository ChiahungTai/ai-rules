# [tag:agents] callstack writer flash A/B 試點

## 目標
裁決「callstack 文檔寫手可否降階 flash+high」——telemetry 兩報告判決衝突（mosaic 判可降：模板固定、輸入是閱讀量；CR 判全強度：跨檔追鏈＋行號當下實讀＋防造假敘事）。

## 相關
- `rules/model-routing.md` 角色 tier 表（render 已列 lite；callstack writer 待此卡裁決）
- 基準：blueprint-bootstrap 既有「工具實測錨定率 >90%」

## 驗收標準
- flash+high 跑一條鏈（golden 對照全強度版），行號錨定率 ≥90% 且零行號幻覺 → 可轉 lite
- 任一不達標 → 維持全強度，記錄數據

## 備註
行號幻覺踩 line-anchors 三跳傳播教訓——不賭，數據裁決。
