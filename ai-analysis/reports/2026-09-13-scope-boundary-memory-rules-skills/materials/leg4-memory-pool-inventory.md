# 腿 4：ai-rules memory 池形態盤點

> 產出者：lite-verify（glm-5.3-flash），2026-09-13。唯讀機械盤點，數字可重現（命令附各節）。

## 節 1｜規模與型態

**總量**：條目檔 **239**（`rg --files -g '*.md' -g '!_*.md' -g '!MEMORY.md' . | wc -l`）；infra 檔 5：MEMORY.md／_inventory.md（238 行投影，機械生成）／_resident-set.md（12 常駐）／_audit-state.md／_generate_index.py。

**type 分佈**（權威源＝frontmatter `metadata: type`；regex 錨定行首縮進）：

| type | 檔案數 | 漂移說明 |
|---|---|---|
| feedback | **136** | ＋7 無前綴檔（frontmatter 判定） |
| project | **36** | ＋5 無前綴檔 |
| reference | **67** | 無漂移 |

- 前綴≠frontmatter 漂移：12 檔無型態前綴、4 檔連字號命名——型態判定一律以 frontmatter 為準。
- **索引落後 1 筆**：`feedback_rules-scope-special-not-common.md`（mtime 07:54，盤點期間新寫入）在目錄但 _inventory.md（07:06）尚無——generator 待重跑。

**前 10 大條目**（ls -laS）：feedback_dual-family-review-dispatch 21.3KB、reference_external-runtime-delegation-family 17.6、reference_muse-code-cli-facts 16.6、project_memory-cc-alignment-diagnosis-0905 14.7、reference_codex-config-zai-topology 13.0、reference_zcode-platform-facts 12.0、feedback_quota-failover-policy 11.5、project_session-topology-single-writer 11.1、feedback_drift-scan-include-variants 10.6、feedback_relay-claims-verify-current-state 10.5。長尾陡（第 20 名 ~6.2KB，多數 1–4KB）。

## 節 2｜主題聚類（12 群；依檔名＋description 全量 rg，未逐條讀 body）

| # | 群 | 數 | 代表條目 |
|---|---|---|---|
| C1 | Commit/Git 收尾防護與 branch 治理 | ~11 | commit-consent-in-autonomous-mode、verify-wt-before-commit |
| C2 | 平行 session 對時／單一寫入者拓撲／relay | ~11 | session-topology-single-writer、relay-claims-verify-current-state |
| C3 | Edit/寫檔與 shell 工具機械陷阱 | ~13 | cjk-char-corruption-rg-verify、full-read-base-not-context-copy |
| C4 | Review/驗證鏈與證據紀律 | ~17 | dual-family-review-dispatch、evidence-over-claims |
| C5 | Model routing／額度／計費／bridge 委派 | ~14 | quota-failover-policy、bridge-glm-family-facts |
| C6 | Harness 平台事實（ZCode/CC/codex/muse 實測） | ~22 | zcode-platform-facts、codex-cli-exec-facts |
| C7 | Memory 治理（池自身機制與治理史） | ~15 | inflow-needs-outflow、memory-index-load-truncation |
| C8 | Backlog/kanban 卡治理與 triage | ~13 | backlog-cli-entry、blueprint-before-new-cards |
| C9 | 派發／agent 編排形態 | ~15 | conference-chair-mode、scan-breadth-over-agent-count |
| C10 | 架構/UC/載體放置設計方法論 | ~14 | uc-inventory-before-structure-proposal、absorb-patterns-not-tools |
| C11 | 人類 viewport／消費形態 | ~9 | viewport-path-click-zero-ceremony、vscode-preview-mechanics |
| C12 | Project 終態弧記錄（「勿重跑」類） | ~17 | execution-tapestry-0910、cr-role-audit-0910 |

形態觀察：project 型幾乎全落 C12＋C7＋C8（弧結算）；reference 型集中 C5/C6（外部工具實測）；feedback 型覆蓋 C1–C4/C9–C11（行為校準）。C7 的教訓條目本身就是 scope 分界一手材料。

## 節 3｜與 rules/ 主題重疊面（rules 側＝19 檔）

重點配對（全表見盤點原文）：
- outward-action-consent ↔ commit-consent 系列 4 條（user 原話裁定層）
- tool-discipline ↔ Edit/背景執行事故 6 條
- collaboration-constraints ↔ 拓撲/relay 5 條
- acceptance-evidence ↔ 證據紀律 5 條
- context-management ↔ memory 治理 5 條
- model-routing ↔ routing/bridge 6 條
- symbol-query-routing ↔ CR 工具鏈 5 條
- 19 檔全覆蓋；**must-execute-before-complete 重疊最薄、llm-output-convention 無同題條目**

**重疊形態小結**：多數配對呈「**rules＝條文、pool＝事故證據＋user 原話裁定**」的縱深關係（pool 條目常自陳「條文已落 rules/xxx」）——非重複，是規範層↔證據層互補。C7（memory 治理）與 C8（kanban）在 rules 側只有 pointer、主體在 skills/——屬「pool↔skill」重疊形態。
