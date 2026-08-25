# 觀察：.review/ 降 optional 後是否還有人用

`.review/` 降 optional 後，跨命令自動化場景（`/judge-review`、`/followup-review`）是否仍有人用。若長期不用 → 可進一步移除 status 機制。

長期觀察，下次 `/flow-review` 回顧。

**來源**：flow-feedback `review-commit-workflow-mismatch` 觀察點 1

## 收案（2026-08-26）
觀察已回答：**有人用**——post-build 鏈（code-review→judge→followup）持續實戰讀寫 `.review/main.md`（2026-08-25 delta_tour 弧全鏈＋此前 A6/M3、①⑤、② 多弧段落共生）。「移除 status 機制」分支不觸發。
