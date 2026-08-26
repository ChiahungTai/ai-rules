# code-reality 新作法切換評估＋CRG/LSP 停用規劃（planning only）

> 產出於 2026-08-26。Baseline：ai-rules HEAD `f8c043b`（relay `da2f19d` 已落地）、
> code-reality HEAD `3594bba`。**2026-08-26 user 五項裁決**：P0 授權（已執行——drift
> 修復＋殘留清理＋`uv run` 回歸修復）、雙 skill 並存維持、P1 授權（已執行——語言矩陣
> 寫入）、CRG 不立替代 EP 改立 v1+ 圖引擎裁決弧、殘留清理併 P0。§3 分類表為評估時快照
> （隔離態已解除、drift 已修），現況以 git log 為準；本檔保留評估理據與裁決記錄。

## 結論摘要（TL;DR）

1. **code-reality 消費面 relay 已大致完成**——`implement`／`code-review`／`debrief`／
   `post-build`／`tour-bootstrap`／`blueprint-bootstrap` 的呼叫形態都已是
   `code-reality <tool> --repo`（Rust）。殘留是**四處 drift**（見 §4）＋**隔離態目錄**。
2. **CRG 不可停**——兩個結構性理由：① crg-query 消費的 10 個操作（impact/flows/
   communities/hub/bridge/semantic/dead-code/scoping）**全部不在 code-reality 能力面內**；
   ② **code-reality 自身依賴 CRG graph.db**（snapshot／graph_audit／chain_tour／delta_tour
   的原料是 graph.db）——退役 CRG 同時打斷 code-reality 半條工具鏈。〔2026-08-26 裁決〕
   **不立替代 EP**——改立 **v1+ 圖引擎裁決弧**（code-reality 端 `ep-v1plus-graph-engine.md`
   已 draft）；POC 實證**聯集互補模型**（SCIP 補 CRG 成立、取代不成立），「CRG 不可停」
   結論不變；引擎面 Rust 原型已驗證（closure 語義精確重現、毫秒級查詢）。
3. **LSP 不禁用**——code-reality 符號面（refs/callers/closure）吃 rust-analyzer SCIP
   index，**只覆蓋 Rust repo**；Python repo（mosaic／ai-rules）的符號真相仍只有 LSP。
   LSP 獨有面（hover／型別簽名／documentSymbol／diagnostics 即時／免建 index）全部保留。
   切換點只有一個：**Rust repo + SCIP index 在場時，符號引用查詢改 code-reality 優先**
   （provenance＋stale 守衛＋跨 session 一致，優於 LSP workspace 狀態相依）。
4. 實測驗證：plugin MCP（`plugin:code-reality:code-reality`）四工具在本 session 可用，
   NT oracle 對照通過（§2）。

## 1. 工具能力面對照（評估的事實基礎）

| 能力 | code-reality（Rust carrier） | CRG | LSP（lsp-python / Claude 原生） |
|---|---|---|---|
| 符號 refs/defs（含 trait 消歧） | ✅ `refs`（SCIP；**僅 Rust**——index 由 rust-analyzer 產） | △ graph 節點（tree-sitter，跨語言但無 trait 消歧語義） | ✅ `findReferences`/`goToDefinition`（pyright=Python；rust-analyzer=Rust） |
| callers / transitive closure | ✅ `callers`（sites）/`closure`（BFS；**僅 Rust**） | ✅ `query_graph` callers_of（跨語言，無 site 細節） | ✅ `incomingCalls`（單層；workspace 狀態相依） |
| diff→impact/risk、affected flows | ❌ | ✅ `detect_changes`/`get_affected_flows`/`get_impact_radius` | ❌ |
| communities／hub／bridge／architecture overview | ❌ | ✅ | ❌ |
| semantic search／dead code／review scoping | ❌ | ✅（`semantic_search`/`dead_code`/`minimal_context`） | ❌（name-based） |
| hover／型別簽名／documentSymbol／diagnostics 即時 | ❌ | ❌ | ✅（獨有） |
| 免建 index 即時性 | ❌（SCIP 生成 ~8 分鐘；WARN 驅動重生） | ❌（build/update） | ✅（workspace 自動索引） |
| EP 對照／transition／hub_refs hazard／tours | ✅（CLI 全工具面，獨有） | ❌ | ❌ |
| provenance／stale 守衛 | ✅ `[SRC]` 行＋index↔HEAD WARN | ✅ `head_matches_build` | △ workspace stale 只能 reindex 重試 |
| 部署形態 | ZCode plugin MCP 四工具＋CLI `code-reality <tool> --repo`；其他 harness 走 README generic MCP config | 共享 HTTP server（launchd :5555，repo_root 路由）＋Claude stdio | user-level lsp-python MCP（payload 路由）＋Claude 原生 |

**語言覆蓋矩陣**（決定「可切」範圍的關鍵）：

| 查詢需求 | Python repo（mosaic/ai-rules） | Rust repo（NT） |
|---|---|---|
| 符號 refs/defs | LSP（pyright） | **code-reality `refs`** 或 LSP |
| callers/closure | CRG `query_graph`／LSP | **code-reality `callers`/`closure`** |
| impact/flows/communities | CRG | CRG |
| hover/型別/即時 | LSP | LSP |

ai-rules 自身：無 scip index、無 `.code-reality.toml`——查自己符號走 LSP／rg（現況
即正確，不需建 index；驗證 Rust 載體一律用 NT oracle）。

## 2. 實測驗證（NT oracle，本 session plugin 工具）

- `refs EventStoreLifecycle.open --repo ~/Github/nautilus_trader` → **雙 DEF**：
  inherent impl `crates/event_store/src/kernel.rs:544`（`impl EventStoreLifecycle`〔:468，
  struct 宣告 :455〕的 `pub fn open`，18 處跨檔 refs）、trait impl `kernel.rs:1350`
  （`impl KernelEventStoreTrait for EventStoreLifecycle`〔:1339〕，0 refs）——與 handoff
  E2E 基準（inherent 18／trait 0）一致。〔勘誤 2026-08-26：初版把兩側標籤寫反並誤稱
  handoff 寫反；經 user 指正＋kernel.rs 源碼查證（:455 `pub struct`、:468/:1339 impl
  邊界）更正——EventStoreLifecycle 是 struct，無同名 trait。〕
- `callers` 同符號 → **16 callers（18 sites）**、item-level 0 處 ✓。
- `[SRC] scip index @ 76213ff（2026-08-24）` provenance 行在 ✓；stale WARN
  （index @ 76213ff vs HEAD @ fd48803）按設計觸發 ✓。
- `closure`／`audit` 未重跑（handoff 已載 E2E 驗證；refs/callers 即足以證工具鏈活）。
- **callers 計數對帳（16 vs 17）**：本報告實測 plugin `callers`＝**16 callers（18 sites）**
  ＝15 test fn＋1 trait impl 委派站；歸檔 EP（`_done/ep-code-reality-repo-mcp.md` 成功
  條件②）與 LSP 交叉（`prepareCallHierarchy`＋`incomingCalls`）基準＝**17**。兩者口徑
  未在本次對帳裁決（可能差在 closure/LSP 對委派或某 test fn 的歸屬）——差異 1 留待
  code-reality 端 `ep-v1plus-graph-engine.md` 弧首次 closure 消費時對帳，兩個數字
  皆為各自工具面實測記錄。

## 3. 三分類表（逐檔逐引用點）

> 掃描命令：`rg -l "code-review-graph|code_review_graph|crg-query|CRG"`、
> `rg -l "LSP|lsp-python|mcp__lsp"`、`rg -l "code-reality|code_reality"`（排除
> ref-docs/、.kanban/、ai-analysis/ 歸檔）。歸檔 EP/spec/report 的歷史提及不列
> （非 live 消費面）。分類：**A 可切**（symbol truth 面）／**B 保留**（CRG/LSP 獨有）
> ／**C 修復或決策**（drift／隔離態／EP 立項）。

### 3.1 code-reality 消費面

| 檔:行 | 引用語義 | 分類 |
|---|---|---|
| `skills/code-reality.disabled-by-plugin-e2e/SKILL.md`（隔離態整檔） | 工具真相源；內容已是 Rust 形態（`code-reality <tool> --repo`、`~/.cargo/bin`、scip_refs repo-keyed slot） | **C**：隔離態解除待 user 裁決；L11「工具在 `~/Github/ai-rules`」表述 drift（Rust 載體住 `~/Github/code-reality`） |
| `AGENTS.md:97` | 專案結構段：`code_reality/` 目錄＋`uv run --project ~/Github/ai-rules python -m code_reality.<tool>` | **C：drift 實錘**——目錄已 retire（git tracked 0 檔、僅剩 `__pycache__`）、消費形態是 Python 舊路 |
| `AGENTS.md:98` | `tests/`＝code_reality 工具鏈測試 | **C：drift 實錘**——tests/ tracked 0 檔（測試隨 Python copy 遷/退） |
| `skills/CLAUDE.md:143` | code-reality 索引行；內容多為 Rust 形態描述（scip_refs、graph_audit） | **C（小修）**：核對「工具住 ai-rules」表述與工具清單（plugin SKILL.md 是最新真相源）；隨隔離態解除一併改 |
| `skills/implement/SKILL.md:79` | baseline snapshot；已寫 `code-reality snapshot --repo` ✓；相對連結 `../code-reality/SKILL.md` | **A 已切**＋連結隨隔離態解除自癒 |
| `skills/code-review/SKILL.md:106` | transition 弧模式；已寫 `code-reality <tool> --repo` ✓ | **A 已切**（連結同上自癒） |
| `skills/debrief/SKILL.md:36-44` | transition／hub_refs／delta_tour 機械底稿；工具名無 `python -m` ✓ | **A 已切**（連結同上） |
| `skills/post-build/SKILL.md:37,59` | 經 code-review 模式 B 間接＋`code-reality tour_validate` ✓ | **A 已切** |
| `skills/tour-bootstrap/SKILL.md:3,13,26` | 工具層分界（chain_tour/delta_tour CLI）；形態正確 ✓ | **A 已切** |
| `skills/blueprint-bootstrap/SKILL.md:49,67` | boundary/boundary_build/chain_tour 消費；`code-reality <tool>` 形態 ✓ | **A 已切** |
| `skills/corpus-recall/SKILL.md:33` | `hub_refs` 影響域擴展（code-reality 工具） | **A 已切** |

### 3.2 CRG 消費面

| 檔:行 | 引用語義 | 分類 |
|---|---|---|
| `skills/crg-query/SKILL.md`（整檔） | CRG 查詢紀律：LSP-vs-CRG 分工表、10 操作 query map、repo_root 規則、anti-over-reliance | **B 保留（主體）**＋**A 增補（小）**：分工表可加 code-reality 第三欄——限「Rust repo＋SCIP 在場」的符號 refs/callers/closure（詳 §5 P1） |
| `skills/crg-query/SKILL.md:20,24` 依賴前提 | CRG 偵測（MCP 工具／graph.db） | **B**（前提不變） |
| `skills/code-review/SKILL.md:127` | axis 3 機械產：`get_impact_radius`/`callers_of`/`get_affected_flows`/`detect_changes`+`get_minimal_context` | **B 保留**（CRG 獨有；無 code-reality 對應面） |
| `skills/execution-plan/SKILL.md:161` | EP ripple：transitive impact／跨檔 callers | **B 保留**（同上） |
| `skills/implement/SKILL.md:166` | Agent Review wiring 驗證／段 impact／claim 反證 | **B 保留**（主消費端是 Python repo；Rust repo 場景 callers 可走 code-reality，但此檔寫的是泛用規則，不急改） |
| `skills/arch-thinking/SKILL.md:88,112,163` | CRG-first fuel：impact/flows/hub/bridge/communities | **B 保留**（CRG 獨有） |
| `skills/review-engine/SKILL.md:81` | 圖譜 facts 後備（companion） | **B 保留** |
| `skills/_common/illustrate-artifact-menu.md:41,49,56-57,65,115` | 結構 viewport fuel＋`detect_changes` SEED | **B 保留** |
| `skills/smell-detector/SKILL.md:6` | allowed-tools `mcp__code-review-graph__*` | **B 保留** |
| `skills/smell-detector/baseline.md:24-96` | baseline mode 重度消費：refresh precheck／communities／`importers_of`／`callers_of`／architecture.md | **B 保留**（communities/architecture overview 無替代） |
| `skills/smell-detector/zoom.md:28` | crg-query 委託一行 | **B**（隨 crg-query） |
| `skills/tour-bootstrap/SKILL.md:20` | `.code-review-graph/graph.db`＝chain_tour 重錯開關 | **B 保留**——**結構性依賴**：code-reality 的 snapshot/graph_audit/chain_tour/delta_tour 吃 CRG graph.db，退役 CRG＝斷 code-reality 原料 |
| `skills/CLAUDE.md:142` | crg-query 索引行 | **B**（隨 crg-query） |
| `rules/modern-cli-preference.md:22` | fd/rg 旗標陷阱案例（`.code-review-graph/` 自帶 `*` ignore） | **B 無需動**（純 fd/rg 語義，與 CRG 存續無關） |
| `hooks/require-crg-repo-root.py`＋`hooks/zcode-registration.json:17` | 共享 server repo_root 機械防護（PreToolUse） | **B 保留**（CRG server 在用） |
| `agents/AGENTS.md:21` | 歷史教訓（專案層 server 全名跨專案即炸，CRG/lsp-python 為例） | **B 無需動**（教訓記錄） |

### 3.3 LSP 消費面

> LSP 保留的兩個根據：① **Python 符號真相唯一來源**（code-reality SCIP 只蓋 Rust）；
> ② 獨有能力面（hover／型別簽名／documentSymbol／diagnostics 即時／免建 index）。
> 「可切」僅指 Rust repo＋SCIP 在場的符號 refs/callers 查詢。

| 檔:行 | 引用語義 | 分類 |
|---|---|---|
| `rules/lsp-navigation.md`（整檔） | 符號查詢 LSP 優先主 rule：Tool Discovery gate、速查表、重構前 findReferences | **B 保留為主**＋**A 增補**：加「Rust repo＋SCIP 在場→符號引用/呼叫鏈可走 code-reality（provenance/stale 守衛/免 workspace stale）」第三選項（詳 §5 P1） |
| `skills/lsp-navigation/SKILL.md`（整檔） | 反例群／agent prompt 模板／跨 harness 載體／staleness 處置 | **B 保留**；staleness 段可加一句「Rust repo 改 code-reality 可繞 workspace stale」（隨 P1） |
| `rules/tool-discipline.md:13-14,58`、`rules/modern-cli-preference.md:13` | 工具選擇原則（LSP/rg/fd 分工＋agent prompt 指定） | **B**；P1 若改分工表，此處原則句同步（single-source drift 掃描範圍） |
| `rules/acceptance-evidence.md:17,22`、`rules/collaboration-constraints.md:65` | LSP findReferences＝獨立機械證據手段（Claim→Evidence→Trust／YAGNI check） | **B 保留**（手段泛稱；Rust repo 場景 code-reality refs 是同級甚至更強證據——P1 增補級，不動規則本體） |
| `rules/instruction-writing.md:25-30`＋`skills/instruction-writing/SKILL.md:72-272`＋`skills/_common/sync-check-angles.md`＋`skills/doc-health/SKILL.md:106`＋`skills/instruction-init/SKILL.md:86,91` | 「導航-B（符號→位置）交給 LSP」寫作/驗證紀律 | **B 保留**（Python 側主力；Rust repo 的 workspaceSymbol 驗證可代 code-reality refs——低優先增補，不急） |
| `skills/review-engine/SKILL.md:71-92` | LSP 查證方法（review 家族共用真相源） | **B 保留** |
| `skills/audit-test/SKILL.md:136,165,245`、`skills/judge-review/SKILL.md:80-92`、`skills/fix-test/SKILL.md:156-168`、`skills/ep-review/SKILL.md:73,85` | LSP findReferences 查證消費點 | **B 保留** |
| `skills/execution-plan/SKILL.md:160-162,187-188`、`skills/implement/SKILL.md:83` | workspaceSymbol 盤點／依賴錨點雙端驗證／hover 型別 | **B 保留**（Python 主消費場景） |
| `skills/code-review/SKILL.md:82,126,140,150`＋`skills/code-review-and-quality/SKILL.md:91-133` | LSP 查證＋Dead Code Hygiene 全消費端列舉 | **B 保留**（hover/即時性+Python） |
| `skills/debugging-and-error-recovery/SKILL.md:90-96` | 除錯符號查詢 LSP first | **B 保留** |
| `skills/python-type-gap/SKILL.md:89-92` | LSP 型別智能（hover/goToDefinition/diagnostics） | **B 保留**（LSP 獨有面） |
| `skills/api-and-interface-design/SKILL.md:38`、`skills/acceptance-evidence/SKILL.md:82`、`skills/scan-project/SKILL.md:39-48`、`skills/_common/illustrate-structure-viewport.md`、`skills/_common/sync-output-templates.md:94`、`skills/_common/upgrade-flow.md:30`、`skills/_common/agent-review-cycle.md:65`、`skills/illustrate/SKILL.md:136,150`、`skills/rules-reminder/SKILL.md:137` | LSP 作為驗證手段/分工表消費 | **B 保留** |
| `skills/nt-query/SKILL.md:46-94`、`skills/nt-v1-query/*`、`skills/upgrade-nt/SKILL.md:34` | NT `.pyi` stubs 上的 LSP（Python contract 面） | **B 保留**；nt-query 的 Rust 真身步驟可增補 code-reality refs/callers（Rust 側符號真相）——**A 增補（隨 P1 評估）** |
| `skills/CLAUDE.md:148` | lsp-navigation 索引行 | **B**（隨 skill） |
| `agents/AGENTS.md:17,21` | lsp-python 載體/allowlist 歷史 | **B 無需動** |

## 4. 發現的 drift 清單（修復 bundle，待授權）

1. `AGENTS.md:97-98`：`code_reality/` 目錄＋`python -m code_reality` 消費形態＋`tests/`
   描述——三者都已過時（目錄與 tests 的 tracked 內容＝0 檔，僅 `__pycache__` 殘留）。
   修法：改寫為 Rust 載體事實（工具住 `~/Github/code-reality`；`~/.cargo/bin/code-reality`
   經 `cargo install --path ~/Github/code-reality/crates/code-reality`；消費形態
   `code-reality <tool> --repo`；真相源 plugin SKILL.md／repo README）＋刪 `tests/` 行。
2. `skills/code-reality.disabled-by-plugin-e2e/SKILL.md:11`「工具在 `~/Github/ai-rules`」
   與 L17「Rust 載體」自相矛盾——L11 語義應是「從任意 repo 消費、repo 事實歸 repo」，
   字面住址已過時。
3. `skills/CLAUDE.md:143` 索引行「meta 層工具住 ai-rules」同上表述問題；工具清單對照
   plugin SKILL.md 核對（`hazard`／`tour_manifest` 等單列項與 CLI 全清單的呈現）。
4. `code_reality/`／`tests/` 的 `__pycache__`＋`tests/fixtures` 殘留物（untracked）——
   順手清或留給 user（非 instruction 檔，機械清理）。

## 5. 分階段切換計畫草稿

### P0 — 隔離態解除＋drift 修復（小型 EP 或單 commit 授權；**待 user 決策 1/2**）

範圍：
1. `git mv skills/code-reality.disabled-by-plugin-e2e skills/code-reality`（還原
   `D skills/code-reality/SKILL.md` 隔離態；untracked 目錄消失）。
2. 修 §4 三處 instruction drift（AGENTS.md／SKILL.md L11／skills/CLAUDE.md:143）。
3. 重新部署：`~/.zcode/skills/code-reality` symlink 指回（四 harness symlink 機制）。
4. 清 `code_reality/__pycache__`、`code_reality/`（空殼）、`tests/` 殘留（untracked）。

**雙載入去留**（決策 2）：解除隔離後 user-level `skills/code-reality` 與 ZCode plugin
`code-reality:code-reality` 並存同名（本 session skill 清單兩者皆列）。選項：
(a) 保留 user-level skill 作為 Claude/OpenCode/Codex 三家的 symlink 載體、ZCode 端
plugin 為主（現狀即此形態，零動作）；(b) 只留 plugin（ZCode），其他 harness 走
code-reality repo README 的 generic MCP config——需拔 symlink，風險是其他 harness
失去 skill 級指引。**建議 (a)**：skill 是 harness-neutral 真相源，plugin 只是 ZCode
的 MCP 載體。

驗收：
- `rg -n "python -m code_reality" --glob '!ai-analysis/**'` → 0 hits（消費形態殘留清零）。
- 四 harness skill 載入點恢复（`ls -la ~/.zcode/skills/code-reality` 等指向 repo）。
- NT oracle 復跑：refs 雙 DEF＋callers 16（同 §2 基準）。
- `/sync-sources` 機械新鮮度檢查通過（instruction 檔改動後必跑）。

### P1 — LSP 定位增補：分工表加 code-reality 第三欄（小型；**待 user 決策 3**）

範圍（single-source drift 防護——改「LSP-vs-CRG 分工」定義源，強制 rg 掃所有引用同步）：
1. `skills/crg-query/SKILL.md` 分工表：加「Rust repo＋SCIP index 在場」的
   code-reality 列（refs/callers/closure＋provenance/stale 守衛；Python repo 不變）。
2. `rules/lsp-navigation.md` 速查表＋`skills/lsp-navigation/SKILL.md` staleness 段：
   加一句「Rust repo 符號引用查詢可改 code-reality refs（免 workspace stale、帶
   provenance）；Python repo 維持 LSP」。
3. 掃描同步範圍（引用分工表的下游）：`rules/tool-discipline.md`、
   `rules/modern-cli-preference.md`、`skills/review-engine/SKILL.md:81`、
   `skills/arch-thinking/SKILL.md:163`、`skills/_common/illustrate-artifact-menu.md`、
   `skills/code-review/SKILL.md:127`、`skills/execution-plan/SKILL.md:161`、
   `skills/implement/SKILL.md:166`——原則句不逐檔重寫，只確認「LSP-vs-CRG」複合詞
   語義仍自洽（新增的是並列選項，不是取代）。
4. `skills/nt-query/SKILL.md` Rust 真身步驟（Step 3-4 之後）：評估加 code-reality
   refs/callers 作為 Rust 側符號真相（.pyi LSP 蓋 Python contract、code-reality 蓋
   Rust 真身——兩層對照正是 boundary 工具的語義鄰居）。

驗收：
- `rg -n "code-reality" rules/ skills/` 的命中分佈與計畫一致（新增點=P1 清單，無意外擴散）。
- bundle 尺寸 gate：`rules/` 端只加一行級內容（90KiB gate 檢查）。
- NT oracle：以 code-reality refs 對照 LSP（rust-analyzer）findReferences 同符號，
  數量級一致（refs 18 為基準）。
- `/sync-sources` 通過。

### P2 — CRG 面處置：**已裁決（2026-08-26）**——不立「替代 EP」、改立 v1+ 圖引擎裁決弧

評估理據（三層，仍有效）：
1. **能力缺口**：impact/flows/communities/hub/bridge/semantic/dead-code/scoping 八類
   消費點（§3.2 十餘檔）在 code-reality 全無對應面——「替代 EP」等於重造半個 CRG。
2. **結構性依賴**：code-reality 的 snapshot/graph_audit/chain_tour/delta_tour 吃 CRG
   graph.db 為原料；先退役 CRG 得先給 code-reality 換邊源（SCIP 只有 Rust——Python
   邊源不存在），成本遠超收益。
3. **維護現實**：CRG 是 PyPI 供應（`code-review-graph@2.3.8` launchd 常駐），活躍維護。

**裁決框架（user 2026-08-26）**：不立「替代 EP」，改立 **v1+ 圖引擎裁決弧**（code-reality
端 `ai-analysis/execution-plans/ep-v1plus-graph-engine.md` 已 draft）。POC 實證採**聯集
互補模型**——SCIP 補 CRG 成立、取代不成立；「CRG 不可停」結論不變；引擎面 Rust 原型
已驗證（closure 語義精確重現、毫秒級查詢）。原本段的退役觸發條件（CRG 停止維護、或
mosaic 全面 Rust 化使 Python 邊源需求消失）併入該弧裁決範圍。

## 6. 決策清單（2026-08-26 user 已全部裁決）

| # | 決策 | 裁決結果 |
|---|---|---|
| 1 | **隔離態解除**（P0） | ✅ 授權已執行——三處 mv 回（user 先行完成；`~/.zcode/skills`、`~/.agents/skills` 實為 repo symlink，單一來源）＋drift 修復（AGENTS.md:97-98／SKILL.md 定位句／CLAUDE.md:143）＋`uv run` 回歸修復（`package = false`——f8c043b 刪顯式 packages 後 setuptools flat-layout 多包歧義）。附註：dogfood 實測 rename 隔離在 skill scanner 層無效（實體目錄仍被掃）——未來隔離要嘛移出 skills/ 要嘛刪 |
| 2 | **雙 skill 並存去留** | ✅ 維持——user-level skill＝harness-neutral 真相源、plugin＝ZCode MCP 載體；零動作 |
| 3 | **LSP 定位增補**（P1） | ✅ 授權已執行——語言矩陣寫入 rules/lsp-navigation.md＋skills/lsp-navigation（staleness 段）＋skills/crg-query（分工表兩列＋rule of thumb）＋CLAUDE.md:142 索引行；hover／簽名／documentSymbol／即時性條文保留；下游 8 檔掃描＝指針式引用自洽（真相源更新、指針不變）；bundle 80,161 bytes＝86% gate |
| 4 | **CRG 替代 EP** | **改框架定案**——不立「替代 EP」、改立 **v1+ 圖引擎裁決弧**（code-reality 端 `ep-v1plus-graph-engine.md` 已 draft）；POC 實證聯集互補模型（SCIP 補 CRG 成立、取代不成立）；「CRG 不可停」結論不變；引擎面 Rust 原型已驗證（closure 語義精確重現、毫秒級查詢） |
| 5 | untracked 殘留清理 | ✅ 併 P0 已執行（`code_reality/`、`tests/` 已刪） |

**關聯事實（user 提供 2026-08-26，免重查）**：code-reality plugin `.mcp.json` 再修正
（`bc174df`：`exec||` 死碼→`-x` 條件式），installed cache 副本仍舊版——ZCode 端重裝
plugin 才吃到（本機 rustup 路徑在，現行仍可運作）；ai-rules 端
`ep-code-reality-repo-mcp.md` 已歸檔（隨本輪 P0 收尾）。

## 7. 本次評估的證據足跡

- 掃描：三組 `rg -l`（CRG／LSP／code-reality；排除 ref-docs、.kanban、ai-analysis 歸檔）
  ——live 消費面 60+ 檔，逐檔引用行語義分類如 §3。
- drift 驗證：`git ls-files code_reality | wc -l` → 0、`git ls-files tests | wc -l` → 0
  （AGENTS.md 兩行 drift 實錘）；`git -C ~/Github/code-reality log -1` → `3594bba`。
- 能力面：plugin SKILL.md（四 MCP 工具＋CLI 全清單）× code-reality.disabled SKILL.md
  （工具表＋profile）× crg-query SKILL.md（LSP-vs-CRG 分工表＋10 操作 map）三方對照。
- 實測：plugin `refs`/`callers` NT oracle（§2）——雙 DEF 18/0、callers 16、
  `[SRC]`＋stale WARN 按設計。
