# [ep:rules] T2-2 bundle 減肥第二波（88.1KB→~79.7KB）

**目標**：always-on bundle 從 88,085 bytes（90KiB gate 95%）減至 ~79.7KB（86%）——S1 design-thinking 合併（deep-thinking rule×guide 架構段）、S2 model-routing 下沉 skill、S3 llm-output-convention 下沉＋自檢清單退場、S4 guide↔rule 單源化三處。

**相關**：EP `ai-analysis/execution-plans/ep-bundle-diet-wave2.md`；supersede `.kanban/Backlog/bundle-layered-diet.md`（繼承護欄：每項搬移須驗證 on-demand 連結存在且可被觸發）。

**驗收標準**：bundle ≤~79.7KB（dry-run 數字）；三端部署一致（shasum＋rg 抽查）；引用面零殘留（repo-wide rg 對帳）；tests 全綠；check_single_source invariants 全綠；/consistency 過。

**備註**：凍結決策五項見 EP 實作總覽（2026-08-30 side chat 定案，勿重辯）。implement 前置＝工作樹乾淨（前 session 五批已 gate commit）＋baseline 重 stamp。
