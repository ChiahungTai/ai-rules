# CR 完全取代 LSP——跨 repo 協調路線（umbrella）

> 產出於 2026-08-28（pyrefly＋occurrence＋CALLS 三弧收斂後；ai-rules 端 arch-thinking 全取代討論＋CR 端 `cr-as-unified-language-intelligence.md` 結晶的統整）。
> **性質**：跨 repo 協調路線——技術真相源在 code-reality repo `ai-analysis/reports/cr-as-unified-language-intelligence.md`（use cases × 情境矩陣 U1-U10＋路線圖），本檔只加**排序、歸屬、gate、relay 檢查點**，不重複其內容。
> **北極星**：「取代」是手段不是目標——價值主張＝一個 plugin 給全部語言＋LSP 給不了的 graph 智慧（U3/U4/U7/U8/U10 獨有、U2 超越）。驗收＝U1-U10 全綠＋鮮度 gate＝stale WARN 不觸發（2026-08-28 裁決：沿用既有機制不新增數值；U6 自帶詞法 vs 語義但書、不分級——findings #8 已裁），非功能清單打勾。

## EP Review Findings

> 2026-08-28 /ep-review（獨立 agent F1-F5 五維度＋主 session 錨點查證；load-bearing findings 已抽驗複核）。狀態：implemented＝修正已回寫本檔；needs-confirmation＝待 user 裁決。

| ID | 嚴重度 | EP 段落 | 問題 | 建議 | 狀態 |
|----|--------|---------|------|------|------|
| 1 | 🟡 | P0／P1 gate | 分工用語 4 位點殘留 `Python=LSP-harvest`（rules/lsp-navigation.md:26＋skills/crg-query/SKILL.md:3/44/55）；部署 bundle 新舊並存（~/.zcode/AGENTS.md:749 vs :800）——aef3f49「zero-residue」宣稱不實 | 4 位點列入 P1 翻轉清單（或先行小修＋redeploy） | implemented |
| 2 | 🟡 | P3 | 退役面低估＋狀態矛盾：mosaic `tools/lsp_mcp/` 8 檔＋Makefile lsp-http/lsp-stop targets＋pyproject mcp 依賴仍在場（git-tracked）；:8000 現況無 listener（client 條目指死 server）；CR STATE.md「lsp_mcp 已全刪」與現場不符 | P3 退役清單補齊（已改 P3 行）；STATE.md 矛盾經 relay 交 CR session 修正 | implemented |
| 3 | 🟡 | Role 表／P2 | NT 消費端無任何 phase 步驟（NT 無 .mcp.json、單 worktree，消費形態≠mosaic） | Role 表 NT 行已補註；P2 gate 補 NT 掛接檢查點（已改） | implemented |
| 4 | 🟡 | 決策 1／分發軸 | Codex/OpenCode 型別面載體無承接——bridge 若不上共享面（:8200），P3 後這兩家型別面歸零，與北極星矛盾 | 載體待裁決：8200 共享面 vs 明示排除（已標分發軸行 ⚠️） | adjudicated（2026-08-28 user：**Codex 納入**——plugin 承載；**OpenCode 明示排除**，未來需要再議 :8200） |
| 5 | 🟡 | P1 gate | 等值電池本體無歸宿：三 repo 僅 CR 結構面 _done EP 提及（golden_corpus＋sidecar 先例）；「凍結在 mosaic relay」是機制非位置，mosaic 端零 artifact | P1 EP 開時明寫歸宿——照結構面先例：CR repo 測試＋sidecar baseline（已註 P1 行） | implemented |
| 6 | 🟡 | 分發軸 | gate「發版→cache 免手動」被現場反證：marketplace.json=0.1.1（08-28 bump）vs ZCode cache=0.1.0（08-26）；決策 2 自記手動修；「ai-rules 端 cache」地點錯置（實為 ZCode user-level） | gate 改機械比對（已改分發軸行） | implemented |
| 7 | 🟡 | P2 | gate「對拍過」規格空洞＋oracle 不對稱：incumbent LSP＝rust-analyzer＝bridge backend，跨引擎等值失去獨立對象 | P2 gate 補 bridge 內外往返一致性＋延遲預算（已改） | implemented |
| 8 | 🟡 | 北極星 | 「U1-U10 全綠＋鮮度可接受」非機械判定：U6 自帶詞法 vs 語義但書；鮮度無門檻數值 | 定義鮮度門檻數值；U6 綠分級或加註排除條款 | adjudicated（2026-08-28 user：沿用 stale WARN 為 gate、U6 不分級） |
| 9 | 🟡 | P1/P3 gate | 電池不過的處置未寫（fallback 缺）；「單向門」修辭與回滾實況錯配——config 全 git-tracked、回滾＝revert，真單向性僅 session 習慣 | 處置＝維持並列（已補決策 6）；單向門 reframing 已標 P3 行 ⚠️ | adjudicated（2026-08-28 user：改「可逆但收緊」） |
| 10 | ℹ️ | P3 | 三 worktree `.mcp.json` 均有未提交修改（code-review-graph→code-reality），lsp-python 移除疊在其上易生混雜 commit | P3 執行前先落盤既有修改再獨立 commit（已註 P3 行） | implemented |
| 11 | ℹ️ | 決策／P1 | 橋 pyright-langserver（已在場、與 harvest 引擎同源）的替代取捨未記錄；裁決 B 在 CR 真相源僅一句 | 裁決 B 取捨理由隨 P1 spike 回填（防再議） | implemented |

## EP Validate Findings

| ID | 嚴重度 | EP 段落 | 問題（POC 結果） | 建議 | 狀態 |
|----|--------|---------|------------------|------|------|
| 1 | — | P1 | POC#1 ✅ `pyrefly lsp` 官方子命令存在——pinned crate rev `1d64c4b` 原始碼：`pyrefly/lib/commands/lsp.rs`＋`lib/commands.rs:22`（pub mod lsp）＋`bin/main.rs:15`。**致命假設成立** | — | verified |
| 2 | 🟡 | P1 | POC#2 ⚠️ 本機無 pyrefly 執行檔（PATH／~/.local/bin／~/.cargo/bin 僅 pyrefly-index；producer 採 crate in-process 連結）——spawn 前提待安裝；PyPI wheel 版本（1.3.x）vs pinned rev 對齊是實作風險 | 安裝形態＋版本對齊納入 P1 spike 前置（已註 P1 行） | implemented |
| 3 | 🟡 | 分發軸 | POC#3 ❌ 「發版→cache 免手動同步」假設與現場矛盾（repo 0.1.1 vs cache 0.1.0） | gate 改機械比對（＝Review #6，已改分發軸行） | implemented |

> 深度 POC（spawn `pyrefly lsp`→didOpen→hover 往返）依單一寫入者拓撲歸屬 CR P1 session——STATE.md 起手點 0 已排薄 spike，本 repo 不重複跑。

## 角色分工（bounded context——單一寫入者拓撲）

| Repo/session | 職責 | 載體 |
|---|---|---|
| **code-reality** | 實作主場：bridge EPs、plugin manifests、發版紀律 | 各 EP 住 `~/Github/code-reality/ai-analysis/execution-plans/` |
| **ai-rules**（本 repo） | relay hub＋instruction 真相源隨 milestone 翻轉（分工條文）＋本路線 | rules/skills＋本檔 |
| **mosaic / NT sessions** | 消費端遷移：lsp_mcp 退役、`.mcp.json`、等值電池現場。NT＝P2 型別面掛接對象（無 .mcp.json、單 worktree；P3 免除——findings #3） | 各 repo handoff／小 EP |

## Phases（依賴序）

| Phase | 內容 | Owner | Gate／milestone |
|---|---|---|---|
| **P0 ✅** | 結構面已取代（Python＝pyrefly producer 78s 全量；Rust＝SCIP；CALLS 拆分 CR `2c44534`→ai-rules `aef3f49`）；分工用語 4 位點殘留 LSP-harvest 隨 P1 清（findings #1） | CR＋ai-rules | 分工條文現況＝「符號→CR、型別→LSP」（`b2c480f`） |
| **P1 ✅** | **DONE 2026-08-28**（CR commit `e524866`）：bridge crate `code-reality-lsp-bridge`（stdio MCP，tools `lsp_status`/`hover`/`check_file`/`edit_file`）＋backend bin `pyrefly-lsp`（producer crate 同 pinned rev）＋plugin entry（inert until bump）。等值電池：hover parity 三型逐字（variable/function/attribute，共用五步正規化）＋class 單側斷言（兩家顯示深度本質不同，記錄排除）；diagnostics .py 過濾＋串流（edit→recheck version 雙條件）；18/18 tests＋dual-context review 25 findings 全修。取捨理由（橋 pyrefly vs pyright）已回填 EP。**分工條文已翻**：型別面 Python→CR bridge（lsp-navigation 3 位點＋crg-query 3 位點＋modern-cli-preference＋tool-discipline，2026-08-28 同批） | CR＋ai-rules | 電池過＋條文翻轉完成＋**MCP 面實證**（2026-08-28 mosaic session 四項：lsp_status alive（lazy spawn）、hover 完整簽名＋docstring＋go-to、check_file `.py` 過濾、edit_file 否證探針——注入型別錯誤 recheck 抓到、還原歸零、磁碟未動） |
| **P2 ✅** | **DONE 2026-08-28**（CR commit `decdb75`）：同 bridge crate 副檔路由（.py→pyrefly、.rs→rust-analyzer 無參數 spawn）——per-language LangSpec＋雙獨立 lazy session；probe 實證 backend 現實（range 省略形被 ra 無視→range 形舊內容 span；didChange 靜默丟棄→停滯重發恢復；-32801 暫態重試）。**Gate 過**：ra_equivalence_battery 內外往返逐字一致（版本釘＋BRIDGE_STRICT_BATTERY strict mode）＋延遲預算（init 0.02s／冷 hover 749ms-9.5s／熱 25ms）＋SM-7 並發獨立性釘；23/23 tests＋post-build review 9 findings 處置（8 採納 1 回滾取捨記錄）。**NT 消費端實證 ✅**（2026-08-28 NT session：路由正確〔status 雙 backend〕、熱 hover 完整簽名（kernel.rs `EventStoreLifecycleOptions` 含 private fields＋doc）、check_file 穩定 count=0；**已知行為**：大 repo 首次冷 hover 可能吃掉內部 timeout 逾時一次——逾時後 status 確認 spawn、重試即熱，非故障——冷 spawn 費用在 NT 量級超過 CR 實測上界〔9.5s〕，改善候選＝首單 pre-warm/retry，隨下次 CR relay）。**mosaic Python 回歸 ✅**（2026-08-28 mosaic session 四項：路由正確落 pyrefly 未誤路由、hover 同 P1 基準品質（簽名＋docstring＋go-to bundled typeshed）、check_file 乾淨、edit 注入→recheck 抓 4 診斷→還原歸零、git status 驗磁碟不動——**P2 重構無回歸**）。**分工條文全面翻轉完成**（型別面雙語言→bridge，8 位點，2026-08-28 同批） | CR＋ai-rules | 條文翻轉完成——U1-U10 全綠＋雙語言型別面，完全取代路線收斂（餘 P3 退役與發版） |
| **P3** | lsp-python :8000 退役：mosaic 三 worktree `.mcp.json` 條目移除＋ZCode user-level config entry＋server 本體歸屬裁定（**offline_backtesting 已退役 in-repo lsp_mcp**——2026-08-28 30 檔批次、gates 全綠、已 commit `d0345603`＋`0914dedd`；main `mosaic_alpha` 仍持 8 檔本體＋Makefile targets；:8000 現況無 listener——findings #2）；CC 內建 LSP 自然共存不強制；執行前先落盤 `.mcp.json` 既有未提交修改（findings #10） | mosaic sessions＋user（STATE.md 矛盾經 relay 交 CR session 修正） | **可逆但收緊**（回滾＝git revert 成本已知；收緊＝U1-U10 電池＋鮮度 gate 齊才走——findings #9 已裁） |
| **分發軸（貫穿）** | plugin＝純 MCP carrier：`.claude-plugin` manifest 補（CC 端一條安裝）＋**Codex 納入**（plugin 承載——機制存在性由 CR 發版時驗證）＋**OpenCode 明示排除**（暫不建，未來需要再議 :8200 共享面）；version bump 紀律、skill 不入 bundle（findings #4 已裁） | CR | 發版後機械比對 marketplace.json vs ZCode user-level cache 版本（`~/.zcode/cli/plugins/cache/code-reality-market/`），不一致即 finding——「免手動同步」現況未實證（repo 0.1.1 vs cache 0.1.0；findings #6／Validate #3） |

## 資料面自理軸（與型別面並行——import_legacy 退場鏈）

> 規格真相源：code-reality `ai-analysis/reports/s5-ceiling-analysis.md`（agent 全量分類 5,805 missing pairs、非抽樣；2026-08-28）。
> 與型別面**無互相依賴**；排序（user 2026-08-28 二次裁決）：**P1→P2→本軸（W2）**——P2 趁 bridge 基建最新做塌縮成本弧、補 Rust hover 真空；W2 規格凍結不衰變。

| # | 內容 | Owner | Gate |
|---|---|---|---|
| W1 | S5 結算修訂：套用 R2-3 凍結條款（constructor 剔分母——94.7% 達標記錄）＋B7a 度量收割（2,642 grain 錯位邊收割）——**併入 W2 EP 開段**（同一度量面，不單開 session） | CR | 結算數字更新＋度量測試 |
| W2 ✅ | **DONE 2026-08-28**（CR `ef58b61`）：B7b 偽建構子 mint 完整落地（pseudo refs/defs 3,033/377；class-callee missing 4,957→~110、轉換率 ~97.8%）；B8 **非 bug 結案**（130 檔＝97 語義空 document＋33 個 class/variable-only 檔被 R2-3 fn-tail gate 設計性濾除——probe 推翻「get_ast None」歸因）；W1 度量腳本 `scripts/s5_coverage.py`（gate 層＝全分母＋B7a 正規化；腳本自身 keying bug 被審出修正）。**gate 實測 95.42%**（凍結語料 `24ced017`，預測 95.7% 的 Δ0.28pp 全歸因：derived-base ~110＋B5 fixture/builtin ~236＋B4/B6/B1b 固有類；HEAD 語料 93.86%／剔 345 條 stale 端點後 95.43%——兩語料收斂）。EP 雙軸審查 12＋post-build 8 findings 全採納 | CR | B7b 落地＋B8 列冊＋凍結第二條成立——**user 已裁（2026-08-28）：接受 95.42% 全歸因真匹配版為 W3 gate 達成**（嚴格 95.7% 為預測值；實測全歸因，精神滿足） |
| W3 ✅ | **DONE 2026-08-28**（CR `3980fe1`）：import_legacy 退役為恢復面（CLI 保留帶 WARN＋`"retired": true`；刷鏈引導全移除——純 producer graph＝常態）；**mosaic 驗收 PASS**——producer 面退場前後逐位相同、chain_tour 重錨逐位相同（same 42/moved 6/not-in-graph 2）；差異全歸因 legacy universe 退役（hub 重整化、impact_radius 7,905→275〔TESTED_BY 33,117 測試衝擊邊隨 legacy 退場〕、communities 排除 legacy-only 成員）；恢復路徑實測可用。結算＝CR `ep-w3-import-legacy-retirement.md` | CR＋mosaic | gate 已裁定達成（user：95.42% 全歸因版——W2 `ef58b61`）；ai-rules 刷鏈文檔已翻轉（同批） |
| W4 | 退場後 mosaic 清 `.code-review-graph/`（oracle／回滾角色卸除） | mosaic（relay 屆時發） | W3 驗收過 |
| W5 | `import_legacy` 完全拔除（subcommand＋importer code＋tests＋雙端文檔殘句；user 2026-08-28 裁定方向） | CR 小弧 | W4 全清＋批次二（NT/code-reality repo/ai-rules 舊庫）完成——gate 表在 CR W3 EP |
| W6 | **tree-sitter 互補面（19.8%＝Rust macro／多行／動態派發——POC 聯集互補實證）**。**前置＝RA 榨乾 spike**（升級 rust-analyzer＋查 SCIP emitter 對 macro expansion call sites 覆蓋——殘餘缺口先量化，可能蒸發大半）；有殘餘才建 producer，**首選 syn-based**（與 Python 側 ruff-parse／py_calls 對稱模式，非 tree-sitter grammar）；cargo expand 路線否決（行號契議全毀）、pyrefly 不適用（Python semantic；Python 語法層已由 ruff-parse 承接）。設計約束：provenance 標記＋查詢面分離、producer-native 鍵避 double-key collision；TESTED_BY 為獨立衍生功能項 | CR（新弧） | 觸發：RA spike 殘餘量化後 user 決定建不建；序位建議 P3/分發軸之後 |

## 決策記錄（2026-08-28 arch-thinking 定案，防再議）

1. **ai-rules 不 plugin 化**——更新流錯配：ai-rules 幾乎天天 commit，symlink＝live 直達四 harness 零刷新；plugin＝install-time copy，整包語料的 staleness 爆炸半徑。OpenCode 無 plugin 系統（Codex 有——分發軸已納入），OpenCode 端 symlink/config 路仍需維持；核心理由（更新流）不變。
2. **plugin 不綁 bundled skill**——dual-source 稅已實證（2026-08-28 ZCode cache 過時副本手動修）；skill 通道由 symlink 層承載。
3. **lsp-python 退役＝可逆但收緊**（2026-08-28 裁決 reframing——回滾＝git revert 成本已知）——等值電池（hover 對照 pyright／diagnostics .py 過濾／串流）齊才走；CC 內建 LSP 不必關（MCP 與內建共存無害，取代由消費端自然發生）。
4. **鮮度是取代的真摩擦**——78s 全量＋stale WARN 已壓到可接受；watch 增量屬「真痛才做」（YAGNI）。
5. **resident state 不進 code-reality-mcp**——型別面走獨立 bridge 進程（bounded context 物理化；CR 端裁決）。
6. **電池不過＝維持並列**——決策 3 共存原則的處置化：等值電池未過前 lsp-python 不退役，P1 成果以並列形態上線（fallback 即現狀；findings #9）。
7. **pyright 僅存非生產角色**——新生產路線全 pyrefly（producer＋型別面橋對象皆 `pyrefly lsp`）；pyright 只剩 ①golden oracle（`lsp_harvest` 產 baseline）②驗收對照組（「hover 對照 pyright」的量尺）。橋 pyrefly 而非橋 pyright 的取捨理由隨 P1 spike 回填（findings #11）。

## Relay 機制（本路線的運轉模式——今日全天已實跑）

每 Phase 完成 → CR 回執（commit＋等值電池證據）→ 貼 ai-rules session → ai-rules 做：①分工條文翻轉（docs mode 小改＋deploy）②下游 handoff 產生（mosaic/NT 消費步驟）③本檔 milestone 打勾。跨 session 不代授權——各 repo commit gate 留在各 session。

## 下一步（immediate，2026-08-28 P2 完成後更新）

1. ~~deploy~~ ✅；**bridge 驗證 ✅**（mosaic offline_backtesting 四項全過）
   ；該 worktree **收案**（`d0345603` lsp_mcp 退役批次＋`0914dedd`
   `.code-reality/` ignore——.gitignore 拆獨立 commit 倖存；`.mcp.json`
   依 user 裁決丟棄，CC 端形態分發軸定案後再設定）。mosaic_alpha／
   trading_lab 隨相互 rebase 收斂（繼承兩個 commit；各自未 commit 的
   `.mcp.json` 修改同批丟棄）
2. **P2 ✅**（CR `decdb75`；副檔路由＋probe 實證 backend 現實＋往返
   一致性 gate 過——見 P2 行）；條文已翻（8 位點）；**deploy 待跑**
   （P2 批次）。NT 掛接實證屬消費端（hover `kernel.rs` 回填 EP）
3. **W2/資料面自理軸**（下一弧；kickoff prompt user 已持有）：規格真相源
   code-reality `ai-analysis/reports/s5-ceiling-analysis.md`（W1 結算
   修訂併入 W2 EP 開段）；CR 新 session 起手
4. **P3**（lsp-python 退役）：W3 退場鏈 gate＝B7b 落地（95.7% 真匹配）
   ＋P2 補齊 Rust 型別面（:8000 曾雙語言服務）；offline_backtesting 的
   lsp_mcp 退役已預先落地（見 P3 行）
5. **分發軸**：下次發版 bump 讓 bridge plugin entry 生效（ZCode cache
   版本鎖；bump 後移除 user-level 手動 entry 避免雙掛）；候選議題——CRG 式 `install` 子命令 vs plugin entry
   （user 標記之後研究，CR STATE.md item 4）
