# AIR-86 批二 candidate ledger（frozen by 5.3 writer，2026-09-13）

> 對照：卡面已決策＋materials/codex-out.txt §C band。裁定欄 A=delete candidate（純教學/模型已知/工具速查細節）、C=keep（user calibration/bootstrap）、S=sink to paired skill。
> 管線：本 ledger 凍結→flash C1（skill 承接）＋C2（rule slim）→機械 gate→真 deploy→雙審（本 ledger 逐列 verdict DELETE-OK/RESTORE/NEEDS-JUDGE）→verify-close→post-build。

## 檔案 1：rules/edit-discipline.md（1,265B → 預估 ~1,180B；band 0.75–0.95KB）

| id | 條文 | 裁定 | 理由 |
|---|---|---|---|
| ED-1 | SOLID 教科書展開（SRP/OCP/LSP/ISP/DIP 括號展開＋冒號後逐原則翻譯） | **A（壓一行）** | 卡面已決策「SOLID 壓一行」；展開是純教學（模型已知），壓縮保留 user 常用語彙錨 |
| ED-2 | 核心原則（編輯現有優先/測試保護重構/預設不保向後相容） | C | 反主流 user ruling |
| ED-3 | scripts/library 入口層級 | C | user ruling（勿讓 scripts 成第二 library） |
| ED-4 | validation/logging/config 禁投機 | C | AI 行為校準 |
| ED-5 | 衝突寫法禁混合 | C | 真實事故裁定 |
| ED-6 | 向後相容確認機制 | C | user ruling |
| ED-7 | 變更範圍紀律（只改必要行/dead code 只標不刪/不留 tombstone） | C | 反主流裁定群 |

**ED-1 定稿文本**（old→new）：
- old：`- 遵循 SOLID（SRP/OCP/LSP/ISP/DIP——子型可替換、介面隔離、對擴展開放對修改封閉）：單一改變理由、多責任拆分；高層透過內層 interface 反轉依賴；公開介面不暴露內部資料/型別。`
- new：`- 遵循 SOLID：依賴向內、介面隔離、單一改變理由；公開介面不暴露內部資料/型別。`

**Band 披露**：其餘全 C-core，終值預估超 band ~200B——比照批一 C7 前例（C-core 承重 band 上修），交雙審裁決。

## 檔案 2：rules/symbol-query-routing.md（1,549B → 預估 ~1,000B；band 0.75–0.95KB）

| id | 條文 | 裁定 | 理由 |
|---|---|---|---|
| SQ-1 | 「ZCode 無原生 LSP 由 bridge 承接；pyright-langserver 是 harvest golden oracle，禁解除安裝」 | **S→skill 載體對照段** | 載體事實＋操作禁令屬 on-demand 查詢面；rule 首後果決策只需 route |
| SQ-2 | 「（.py→pyrefly、.rs→rust-analyzer）」映射 | **S→隨 SQ-1 一句入 skill** | 工具速查細節 |
| SQ-3 | 「即時 documentSymbol/working-tree 回饋亦用 LSP」 | A（壓縮留 working-tree） | documentSymbol 可推導；skill L115 已有「documentSymbol 即時形」 |
| SQ-4 | code-reality 分工三 bullets 的機制細節 | C（併入核心原則一句） | SCIP/pyrefly/[SRC] 承重 route 語義，保留但收斂行數 |
| SQ-5 | 任務啟動 gate 全段 | C（逐字保留） | 卡面已決策保留核心 |
| SQ-6 | fallback 階梯＋降級標記＋工單優先＋zero-hit 禁斷言 | C（保留＋與 L21 tail 合併去重） | 「勿直接宣稱零消費者」與「禁把未查到斷言為不存在」同義——單源化 |
| SQ-7 | L21 rg 陷阱列舉（truncation/masking/命名差異/toplevel） | A（壓縮列舉） | 反例群已在 skill；rule 留詞彙錨＋pointer |

**定稿全文**（frontmatter 不變，body 全文替換）：

```markdown
# 符號／型別查詢路由（code-reality 優先）

## 核心原則（cr-first 路由）

搜尋前分清符號/引用/呼叫鏈與字串/config：符號優先 code-reality（refs/callers/closure，核對 [SRC] provenance/stale），型別走 code-reality-lsp-bridge hover/check_file（缺場退 LSP），文字 rg、檔案 fd；即時 working-tree 回饋用 LSP——index 是 build-time，編輯後須重 harvest。載體對照、staleness 處置、rg 反例群見 symbol-query-routing skill。

## 任務啟動 gate（符號查詢任務強制）

涉及依賴/引用/fan-in/消費者/呼叫鏈/跨域/context/_private/邊界/循環/反向耦合/簽名/型別/定義/實作查詢，**第一步確認 cr 在場**（MCP 或 `.code-reality/graph.db`；detect 見 cr-query skill）；禁用 which/timeout shell proxy 探測。純 Read 理解、demo、log 不觸發。

## fallback 與 zero-hit 紀律

index 缺/過期且不可重建→LSP；LSP 亦缺才 rg；工單工具/唯讀限制優先。降級須標「未 index 驗證」，**禁把未查到斷言為不存在**——rg 會漏符號/local import（truncation、display masking、命名差異，反例見 skill），引用可疑少先查 index/workspace 新鮮度。
```

## 檔案 3：rules/quality-constraints.md（2,341B → 預估 ~1,900B；band 1.3–1.7KB）

| id | 條文 | 裁定 | 理由 |
|---|---|---|---|
| QC-1 | 狀態外部化/等冪/無狀態 mechanics＋TemporaryDirectory 禁令＋ReplayHost 誤用案例 | **S→validation-strategy skill 新段** | §C「方法 body 沉 validation skill」；guide 鐵律已有一級 違規字「狀態外部化」錨，rule 留 pointer 不丟語義 |
| QC-2 | crash-only 核心句＋適用範圍 | C（壓縮合併為一段＋pointer） | 適用範圍是 guide「Crash-Only 適用範圍見 quality-constraints」的 pointer 標的——必須在場 |
| QC-3 | 消費端驗證 pointer 段的 skill 小節名全列 | A（壓縮） | 三個小節名是導航細節；skill desc 觸發詞已涵蓋路由 |
| QC-4 | 完整交付標準／fail loud／漸進驗證 gate／多步驟檢查點 | C（逐字保留） | user calibration 核心 |

**QC-1+2 定稿**（取代整個「數據完整性優先」段含誤用警告小節）：

```markdown
## 數據完整性優先（Crash-Only Design）

損壞數據比缺失更危險。無效輸入、溢出、轉型/解析失敗立即崩潰，禁吞錯續行或修補損壞輸入；驗非空、必要欄位、NaN、inf。適用量化交易、高頻、實時風控、批次；不適用長會話、複雜 UI 狀態、UX 優先互動。設計方法（狀態外部化/等冪/持久化路徑）與誤用邊界見 validation-strategy skill「crash-only 邊界」。
```

**QC-3 定稿**（old→new）：
- old：`先定位主要消費者並跑完整流程；測試集範圍不可憑目錄直覺，須機械反查。工具命令、symbol 命中≠接線被驅動、整合器型兩層測試等細則見 **validation-strategy skill**「整合器型變更判定」「接線覆蓋與漸進驗證」「消費端驗證模式」段（證據分層見 [acceptance-evidence](acceptance-evidence.md)）。`
- new：`先定位主要消費者並跑完整流程；測試集範圍不可憑目錄直覺，須機械反查；symbol 命中≠接線被驅動。細則見 **validation-strategy skill**（證據分層見 [acceptance-evidence](acceptance-evidence.md)）。`

**Band 披露**：C-core 佔比高，預估 ~1.9KB 超 band 上緣 ~160B——比照批一 C7 前例交雙審裁決。

## 檔案 4：rules/must-execute-before-complete.md（1,155B → 預估 ~1,000B；band 0.65–0.85KB）

| id | 條文 | 裁定 | 理由 |
|---|---|---|---|
| ME-1 | 「為什麼」段（四案例列舉） | A（壓縮併入核心原則） | 案例是論證證據；留三個詞彙錨＋ast.parse 反證句即可 |
| ME-2 | POC lifecycle（含「commit 2.7」EP 內部引用） | A（壓縮） | EP 段號是內部細節；「任一固化即可刪」裁定保留 |
| ME-3 | 核心原則／強制規則／例外段 | C（逐字保留） | 反「只讀碼就報完成」的核心 user ruling |

**ME-1 定稿**（兩處）：
- 核心原則 old：`語法正確不代表邏輯正確；建立/修改每個可執行 Python/script/demo/POC/example 後，必須 uv run python <file> 實跑，不能只讀碼、ast.parse 或說理論可行就報完成。`
- 核心原則 new：`語法正確不代表邏輯正確；建立/修改每個可執行 Python/script/demo/POC/example 後，必須 uv run python <file> 實跑，不能只讀碼、ast.parse 或說理論可行就報完成——psycopg COPY、轉型/FK、循環 import 這類錯誤都需實跑揭露。`
- 刪除整段：`## 為什麼`＋其下真實案例段落。

**ME-2 定稿**：
- old：`POC 是暫時產物，到所屬 EP 段落 build＋commit 為止；build 將驗證行為提煉正式測試，commit 2.7 確認承接後清除。test docstring/EP 結論/量測文件任一完整固化即可刪；量測外部世界者不強迫轉 test。`
- new：`POC 到所屬 EP 段落 build＋commit 承接後清除；驗證行為以正式 test、docstring 或 EP 結論任一完整固化即可刪，量測外部世界者不強迫轉 test。`

## C1 承接（兩支 skill）

**skills/validation-strategy/SKILL.md**——「四紀律」段之後、「整合器型變更判定」段之前插入：

```markdown
## crash-only 邊界（自 quality-constraints rule 承接 2026-09-13）

- **設計方法**：狀態外部化（DB/隊列），操作等冪、服務無狀態；停止即崩潰、恢復即初始化。持久化輸出/備份禁 `tempfile.TemporaryDirectory`（scope 結束即毀），須放專案外持久路徑。
- **誤用警告**：crash-only 只保證意外失敗後可恢復，不豁免可預期的整合 bug、配置或合約錯誤。真實案例：ReplayHost SIGTERM 失敗曾被以 crash-only 跳過 graceful 處置；正解是 TDD red（xfail strict）釘 graceful 目標再修。

rule 端留核心句＋適用範圍＋pointer（[quality-constraints](../../rules/quality-constraints.md)）。
```

frontmatter desc 追加觸發詞：`、crash-only 邊界（設計方法與誤用）`（插在「消費端驗證模式（完整流程＋測試集機械反查）」之後）。

**skills/symbol-query-routing/SKILL.md**——「跨 harness LSP 載體對照」段表格後段落（L100 段落之後）追加一句：

```markdown
ZCode 無原生 LSP：型別面由 code-reality-lsp-bridge 承接（.py→pyrefly、.rs→rust-analyzer）；pyright-langserver 是 harvest golden oracle，禁解除安裝。
```

desc 已涵蓋（「跨 harness LSP 載體對照」）不需改。

**consumer 同步（impl 停手回報後修訂，2026-09-13）**——改定義源必同步引用端（drift 防護）：

- skills/test-driven-development/SKILL.md L176：
  - old：`（用 crash-only 等設計哲學合理化不修，見 [quality-constraints](../../rules/quality-constraints.md) 誤用警告）`
  - new：`（用 crash-only 等設計哲學合理化不修，見 [validation-strategy](../validation-strategy/SKILL.md)「crash-only 邊界」）`
- skills/symbol-query-routing/SKILL.md L115：
  - old：`（2026-08-28 P1；bridge 缺場退 LSP，詳 rule「code-reality 分工」段）`
  - new：`（2026-08-28 P1；bridge 缺場退 LSP，詳 rule「核心原則（cr-first 路由）」段）`
- skills/symbol-query-routing/SKILL.md desc L3＋L8 列舉同步：
  - old（預期恰好 2 處）：`cr-first 四路路由、任務啟動 gate、code-reality 分工`
  - new：`cr-first 路由、任務啟動 gate、fallback/zero-hit 紀律`
  - 執行前先 `rg -c` 確認計數＝2，不符即停手回報

**機械 gate 補充**（隨上修訂）：
- 負詞彙掃追加：skills/symbol-query-routing/SKILL.md 內 `code-reality 分工` → 0 hits
- 正向追加：skills/test-driven-development/SKILL.md 含 `crash-only 邊界`

## 機械 gate（flash 執行後自跑）

1. `wc -c` 四 rule＋兩 skill 前後量測（雙量測 source 側）
2. 負詞彙掃（rules/ 內 0 hits）：`SRP/OCP/LSP/ISP/DIP`、`pyright-langserver`（僅 skill 1 hit）、`ReplayHost`（rule 0/skill 1）、`TemporaryDirectory`（rule 0/skill 1）、`commit 2.7`、`零消費者`
3. 正向詞彙（必須存活）：`第一步確認 cr 在場`、`禁把未查到斷言為不存在`、`DEPTH-MIN→SAMPLE→FULL`、`uv run python`、`禁默默混合`、`預設不保留向後相容`、`適用量化交易`
4. `uv run pytest`（基線 364 passed）
5. `uv run python scripts/deploy_agents.py --dry-run` 綠（真 deploy 由主 session 於雙審前執行）
6. 跨檔引用存活：guide「適用範圍見 [quality-constraints.md]」標的在；acceptance-evidence 指向 quality-constraints 的語義仍成立；tool-discipline「詳 [symbol-query-routing.md]」仍通

## 偏差回報義務

文本套用與 ledger 不一致、gate 紅、或發現 ledger 未涵蓋的語義依賴→停手回報，禁自行擴權修。
