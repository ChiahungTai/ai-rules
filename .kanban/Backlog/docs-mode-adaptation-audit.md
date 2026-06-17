# docs mode 系統性適配盤點

docs mode 已落地（`execution-plan` + `build`），但下游消費端未全面適配。已知缺口：ripple 缺語義反向撈（judge-review ✅ 待落地）、`code-review` 六軸（Security/Performance 對文檔 N/A）未適配。可能還有 `audit-test`、`ep-review` 未盤點。零星修會陷入「修一個發現一個」。

**決策**（flow-review 2026-06-17 討論點 1）：選 B 系統性盤點。盤點本身用「語義反向撈」掃所有命令的 docs mode 分支。

**來源**：flow-feedback `docs-mode-ep-ripple-gaps` + `review-commit-workflow-mismatch` 觀察點 3
