# Rust 語義精確層與 caller 邊——生態替代方案研究報告

> **定位**：self-contained 研究報告（deep-work 弧，2026-08-25）。調查動機鏈：
> 「CRG 同鍵去重 bug（861 顆）→ SCIP sidecar 導入 → 怕每次 code 更新的索引
> 維護成本 → 改 CRG 的難度評估（tree-sitter 語法層到不了 trait solving）→
> **那 GitHub 生態上還有誰能做到？**」。前一份評估
> [`code-reality-tools-evaluation.md`](../../../mosaic_alpha_offline_backtesting/ai-analysis/reports/code-reality-tools-evaluation.md)
> （2026-08-21）確立了「tree-sitter 家族集體失明／LSP 型別推導是邊真相源／
> 單一工具全包不存在」；本報告覆蓋它之後的精確問題：Rust 符號精度、
> caller 邊、更新經濟學。
>
> **事實錨**：ai-rules HEAD `847ebf5`；本地 NT 真索引（stamp `76213ffd`，
> 275MB＋衍生 db 239MB）；E2E 探針腳本在 ai-rules `.agent-tmp/research/`。
> 方法論限制見 §7。

---

## TL;DR

1. **沒有替代品能取代現有 facade——但發現比取代更好的東西**：caller 邊
   （圖級查詢的缺口）**可以從現有 SCIP 索引單獨推導**，本地真索引 E2E
   實證 **96.9% 歸屬覆蓋**。不需要新工具、不需要改 CRG、不需要額外索引成本。
2. 這**修正了前一天的錯誤結論**：「enclosing_range→caller 邊死路」只對了一半
   ——ref occ 的 enc 確實是 callee echo（無 caller 資訊），但 **DEF occ 的 enc
   是定義項完整 span（函式體）**，正是 containment 歸屬需要的材料。
3. 生態掃描結論：**Rust 語義精確層唯一活水源头就是 rust-analyzer**——連
   Meta Glean 的 Rust 支援都是吃 SCIP；GitHub stack-graphs（增量名稱解析的
   最後希望）2025-09 已 archive 且從未支援 Rust 精確解析；CodeQL 2025-06 起
   有 Rust public preview 但授權擋商業專案。
4. **scip-callgraph**（Beneficial-AI-Foundation＝Verus 團隊，MIT/Apache）把
   「SCIP→caller/callee 圖」產品化——與本報告實證的機制同族，可直接試用
   或當參考實作。
5. 架構含義：**facade 定案升級而非推翻**——SCIP 層從 site 級 refs 擴張到
   caller 邊；CRG 的保留層（Python 常駐查詢、transitive/communities、增量）
   不變；A5（修 CRG 鍵化）的觸發條件進一步後退，可能永遠不需要觸發。

---

## 1. 緣起：三個 UC 與已知情事

本弧對話鏈確立的需求（消費形態：solo+AI、離線、CLI 查詢、量化數據完整性 ethos）：

| UC | 內容 | 現況載體 | 缺口 |
|---|---|---|---|
| **UC-1 符號精確層** | trait 消歧的 def/refs（`impl#[Type]method()` vs `impl#[Type][Trait]method()`） | `scip_refs` sidecar（NT 驗收 byte-identical、138/861 對帳） | ✅ 已解 |
| **UC-2 caller 圖級** | 誰在呼叫→impact radius／hub／「0 prod callers 可刪」 | CRG（Python ✅；Rust 遭 861 顆同鍵去重污染）＋前日判定「SCIP 無 caller 材料」 | 🔴 本報告翻案 |
| **UC-3 更新經濟學** | code 更新後索引保鮮 | CRG 增量（秒級）vs SCIP 全量（~8 分＋手動三步） | 🟡 懶更新紀律＋可選一條龍 |

已知情事（本弧前段實證，勿重推）：CRG collapse 機制＝`qualified_name UNIQUE`
（`graph.py:46`＋`parser.py:11108-11119` trait 資訊在手但丟棄）；tree-sitter
語法層無法判定 trait vs inherent 呼叫歸屬（需要 rust-analyzer 級 trait solving）；
ref occ 的 enc＝同檔 callee 定義 span 回聲（同檔 84,562 全有 enc、同檔
enc=N 為 **0**；跨檔 154,852 全無＋**188 顆例外**＝③ bin/test duplicate
家族——「完美分離」僅同檔向成立，雙條件有 0.1% 反例）；DEF occ 的 range＝3 元素名稱行（不含體）——**此點導致前日誤判
「containment 不可行」，見下節翻案**。

## 2. 重大實證：SCIP-only caller 邊（DEF-enc containment）

### 2.1 機制

SCIP spec 對 DEF occurrence 的 `enclosing_range` 定義＝「外圍定義的範圍」。
rust-analyzer 的實作：**fn DEF occ 的 enc＝該 fn 完整 item span**（4 元素
`[start_line, start_col, end_line, end_col]`）。本地索引統計：64,164 顆 fn DEF
**100% 帶 enc**（4 元素 63,841／3 元素 323）。樣本對照源碼全吻合
（`kernel.rs` `default()` name@L126→enc L126-132、`default_backend_opener`
name@L191→enc L191-195）。

據此推導 caller 邊（**零額外工具，SCIP 單獨成立**）：

```
per-doc 建 fn DEF 清單：enc span → (start_line, end_line, symbol)
每顆 ref occ (file, line) → 同檔內含它的最內層 fn DEF
    → 該 DEF symbol = caller；ref occ symbol = callee
    → 邊 = caller → callee（編譯器級符號精度：callee 已 trait 消歧）
```

### 2.2 E2E 數據（本地真索引，NT @76213ffd）

- **歸屬覆蓋 96.9%**：239,602 顆 workspace fn ref occ 中 232,078 顆成功歸屬
  fn caller。
- **7,524 顆（3.1%）落 item 層**（use 敘述/const/屬性等）＝**絕大多數為
  非呼叫 refs**——containment 順帶就是 refs/callers 的口徑過濾器。
  **但「3.1%＝非呼叫」是過度定言**（reviewer 機械反例）：其中至少
  **35 顆是巨集生成 fn 內的真呼叫**被誤殺——肇因 e2e 只把 4 元素 enc 的
  fn DEF 納入 caller 候選，323 顆 3 元素 enc（single-line span，proto
  定義 `[startLine, startChar, endChar]`，形態＝`criterion_group!`/
  `sbe_roundtrip_test!` 等巨集生成的 fn）被排除。實作版必須支援
  single-line span；口徑過濾的精確數字以實作版為準。
- **`EventStoreLifecycle.open`（inherent）18 refs 逐筆歸屬全數合理**：
  `kernel.rs:1356`→trait impl `open()`（KernelEventStore 委派邊）；其餘 17 顆
  →`mod tests` 內對應測試 fn（名稱與行為吻合，如
  `kernel_event_store_open_seals_leftover_session_before_reopen`）。

### 2.3 對前日結論的更正

前日記錄（memory tri-track）：「enc 是 callee echo——SCIP 無 caller 材料全程
成立、enc→caller 邊原規格死路」。**錯誤的半邊**：只驗了 ref occ 的 enc，
漏驗 DEF occ 的 enc。正確表述：ref-side enc＝callee echo（對）；DEF-side
enc＝body span（漏）→ **caller 邊可推導**。memory 已更正。教訓同
[[relay-claims-verify-current-state]] 家族：半邊驗證的「完美分離」也會給出
自信的全稱否定——84,562/0 的分離只證明了「ref-side enc 無 caller 資訊」，
不證明「索引無 caller 材料」。

### 2.4 與 LSP incomingCalls 的交叉驗證（08-25 補測）

同日另一 session（`sess_0afead70`）把 `tools/lsp_mcp` 多語言化（rust-analyzer
掛入常駐 LaunchAgent `127.0.0.1:8000/mcp`、NT root 進 workspace 白名單、
ZCode user-level 註冊），其 handoff 自承 hover/findReferences/call hierarchy
**未實測**。本弧以 curl 補測 call hierarchy 對同一標的：

- `prepareCallHierarchy` @ kernel.rs:544:12（inherent `open()`）✓ 命中；
- `incomingCalls` 回 **17 callers**——trait impl `open()`（kernel.rs:1350
  委派）＋16 個測試 fn，**與 SCIP containment 推導的 18 refs→17 callers
  完全一致**（同批函式名單；LSP 列 fn item 起始行、SCIP 列呼叫點行）。

兩個機制獨立的方法（批次索引 containment vs 活 rust-analyzer call
hierarchy）對同一符號產出相同 caller 集——**evidence fusion 級交叉驗證**。
分工定案：**互動查詢走 LSP**（常駐、背景索引、免 regen、~即時——你原本
怕的「每次 code 更新」在互動側不存在此問題）、**錨定批次工件走 SCIP**
（stamp/[SRC]/audit/governance——可審計證據）。工具面為 per-session
快照：新 session 才會看到 `mcp__lsp-python__*` 工具。

## 3. 生態掃描總表

評估軸：**精度**（trait 消歧？）、**caller 邊**、**增量/更新**、**solo 契合**
（離線/免費/CLI/MCP/server 負擔）、**維護**。

| 專案 | 精度 | caller 邊 | 更新 | solo 契合 | 維護 | 判定 |
|---|---|---|---|---|---|---|
| **rust-analyzer SCIP**（現役） | ✅ 編譯器級 | △ 可推導（歸屬覆蓋 96.9%；正確率經 18 refs 抽樣＋LSP incomingCalls 交叉驗證，見 §2.4） | ❌ 全量 ~8 分 | ✅ 離線 CLI | ✅ 官方 | **留任，擴張** |
| **scip-callgraph**（Beneficial-AI-Foundation） | ✅ 吃 SCIP | ✅ caller/callee 圖＋subgraph/depth | 同 SCIP | 🟡 38 binaries、Verus 導向 | 🟡 8★ 但 CI 活躍、©2026 | **試用＋參考實作** |
| **nusy-codegraph**（crate，scip_calls 模組） | ✅ 吃 SCIP | ✅ 「high-fidelity Calls edges」 | 同 SCIP | ✅ Rust crate | 未深查 | 備選整合件 |
| **bonsai-ninja** | ❌ tree-sitter（自建 typed IR；dyn/巨集明示不解析） | ✅（同天花板內） | △ content-addressed 快取世代；無 watch | ✅ CLI-first＋agent skills；MIT | 🟡 2026-08 首發、early-stage | **watch**（誠實信號佳） |
| **CRG**（現役） | ❌ 語法級（861 顆污染） | △ | ✅ git 增量秒級 | ✅ 已部署 MCP/CLI | ✅ 自有 | **留任結構層** |
| **Glean**（Meta） | ✅（Rust 經 SCIP） | ✅（經 SCIP 轉換） | 伺服器端 | ❌ 伺服器架構、Meta 規模設計 | ✅ | **不採**（印證：Rust 精度源＝ra） |
| **stack-graphs**（GitHub） | △ 名稱解析級（非型別） | △ | ✅ 增量（核心賣點） | 🟡 | ❌ **2025-09 archived**；精確支援僅 TS/JS/Py/Java，**從未有 Rust** | 出局＋類別證據 |
| **CodeQL** | ✅ 編譯器抽取 | ✅（QL 查詢） | ❌ 全量抽取 | ❌ **授權**：免費限 OSS/研究；商業（量化交易）需 GHAS | ✅（Rust 2025-06 起 public preview） | **不採**（授權＋重量） |
| **Joern**（CPG） | ✅（有前端的語言） | ✅ | ❌ | 🟡 | ✅ | **出局**：無 Rust frontend |
| **cargo-call-stack**（japaric） | ✅ LLVM 級（單調） | △ 整程式 | ❌ nightly＋embedded 導向 | 🟡 | 🟡 embedded 場景 | 不採（場景錯位） |
| **cargo-callgraph**（robinmoussu） | —（rustc fork，釘 nightly-2020） | △ | — | — | ❌ 作者自述廢棄 PoC | 出局 |
| **Kythe** | ✅（rustc 內部實驗 indexer） | ✅ | ❌ | ❌ Bazel 生態 | 🟡 experimental 多年 | 不採（重量＋實驗性） |
| **rust-code-analysis**（Mozilla） | ❌ tree-sitter 度量 | ❌ | — | — | 🟡 crate 停更 ~2021 | 出局 |
| **rustc 內部其他**（Flowistry 等） | ✅ | △ dataflow 軸 | ❌ | 🟡 研究級 | 🟡 | 不採（軸不同＋維護風險） |
| **MCP 新波**（codegraph-rust/CodeGraphContext/Lumora/CodeSage/code-graph-mcp/CocoIndex） | ❌ tree-sitter/embedding | △ | △ | ✅ | 🟡 多為 0-數十★ 超早期 | 類別出局（前份報告結論重演：scanner-only） |
| **ra 當 library**（ra-ap-* crates） | ✅ | ✅ call hierarchy | △ 常駐 host | △ 自建工具＋ra 版本 churn | — | **自建路線**（§5 討論） |

## 4. 逐類判讀

### 4.1 編譯器前端批次輸出（SCIP 現役＋消費者生態）

**判讀：ra 是 Rust 語義的唯一活水源，且已形成消費者生態。** Meta Glean
的 Rust 支援官方文件寫明「Rust (via rust-analyzer)」走 SCIP/LSIF 攝入——
連 Meta 都不自建 Rust indexer。SCIP 格式本身（scip-code.org，已遷出
Sourcegraph 到獨立 org）有 Go CLI（convert/snapshot 等，Apache-2.0，活躍）、
Rust `scip` crate（protobuf 解析）。**scip-callgraph** 是本弧最有價值的
發現：Verus 團隊（Beneficial-AI-Foundation）用 SCIP 建 caller/callee 圖
（38 個 metrics binaries、DOT/JSON/SVG 輸出、`--include-callers/--depth`、
web viewer）——與 §2 實證機制同族（liza-mas/scip-search 文件直述該技術：
「non-definition occurrences inside the enclosing range of a target
definition occurrence」）。README 未明寫 enc 細節（需讀 scip-core 源碼確認，
本報告以本地 E2E 替代驗證）。授權（user 勘誤後修正）：README License 段
與 Cargo.toml 均宣告 MIT OR Apache-2.0——**宣告有效**；gh api `license:
null` 僅反映 GitHub 靠根目錄 LICENSE 檔偵測（無檔案即 null），非授權不明。
授權文本檔缺席屬 upstream hygiene 小事，不影響試用／參考／依賴採納。

### 4.2 增量名稱解析（stack-graphs）——死路確認

stack-graphs 是「增量＋跨 repo 名稱解析」的唯一認真嘗試（per-file partial
graph、query-time stitching）。結局：**2025-09-09 GitHub archive**，且其
精確支援清單（TS/JS/Python/Java）從未包含 Rust——方法解析需要型別資訊，
正是 scope-graph 類方法的理論邊界。社群 fork 存在但非主流。**對 UC-3 的
含義：增量語義索引這條路，生態上沒有人活著做到 Rust。**

### 4.3 平台級 indexer（Kythe/Glean/CodeQL）

共同形態：抽取器精確（編譯器/AST 級）、查詢語言強（Angle/QL）、**部署
形態是伺服器/CI 平台**——與 solo+AI 離線 CLI 形態根本錯位。CodeQL 的
Rust preview（2025-06）精度路線正確但授權對商業閉源專案是硬牆（免費限
OSS/研究用途）。Glean 若要用，Rust 資料也是先跑 rust-analyzer SCIP——
多繞一層伺服器，精度不增。

### 4.4 語法級 + 誠實信號（bonsai-ninja）——值得 watch

2026-08 首發的 local code-intelligence 引擎：tree-sitter 前端（20 語言）
→自建 typed IR/resolver/callgraph→IFDS 資料流。**精度自述誠實**：dyn
dispatch/未展開巨集/computed imports 明示不解析，回
`analysis_incomplete_reasons` 而非偽造邊（符合量化數據完整性 ethos 的
fail-loud 精神）。查詢面豐富（`slice`＝backward influence/change-impact、
`trace`、taint）。MIT、無 hosted service。30k 檔 ES 冷語義索引 7m22s。
early-stage（17★、自述 ambitious early-stage）——**watch 不採用**：其
Rust 精度天花板與 CRG 同級（tree-sitter 無 trait solving），增量模型
（content-addressed 世代快取）比 CRG 弱（無 git-driven changed-files 增量）。

### 4.5 MCP 新波——前份報告結論重演

2025-2026 出現一批 code-graph MCP servers（codegraph-rust、
CodeGraphContext、Lumora、CodeSage、code-graph-mcp、CocoIndex）。抽查
形態：tree-sitter/AST＋embedding 檢索為主——**語法級＋向量**，無一宣稱
編譯器語義。與 2026-08-21 報告的「AI-era 新波全 scanner-only」判定一致。
對已有 CRG＋LSP＋SCIP 的棧，零增量。

## 5. 架構分析（deep-thinking 格式）

**本質需求**：Rust 側三 UC（§1）在 solo+AI 離線 CLI 形態下的最便宜的
充分解。不可妥協：精度（trait 消歧——錯的 refs 比沒有更糟）、可更新
（懶更新可接受、每次全量 8 分可接受但有摩擦）、AI 點查人體工學（秒級、
stable 輸出、可 stamp）。

**基本元素拆解**：語義源（只有 rust-analyzer：SCIP 批次輸出／LSP 常駐／
ra-ap library 三種消費形態）、圖計算（transitive/hub/communities——任何
圖庫皆可，CRG 已有）、歸屬層（ref→caller：本報告證明 DEF-enc containment
即解）、新鮮度（增量：語法級可行〔CRG〕、語義級無人生存〔stack-graphs
死＋scip-differential 從未上市〕）。

**從基本原理推導**：語義精度與增量更新在 Rust 生態是**互斥的現實**（精度
源 ra 只批次輸出；增量源 tree-sitter 無語義）→ 最優結構不是找「既精確又
增量」的幻想工具，而是**分層各自取最長板**：語義層（SCIP，懶更新）＋
結構層（CRG，增量）＋歸屬薄層（DEF-enc containment，零額外成本）。這正是
既有 facade 定案的深化——**facade 的邊界移動了**：caller 邊從「CRG 保留層」
移入「SCIP 可推導層」，CRG 對 Rust 的角色縮到 transitive/communities 的
**圖計算殼**（且這塊也可以用 SCIP 邊重）。

**驗證**：§2 E2E（96.9%＋18 refs 逐筆）；生態面對照（scip-callgraph 同機制
產品化、Glean Rust=SCIP、stack-graphs 之死證明增量語義無人做成）。

**連鎖後果追蹤**：
- 第一層：scip_refs 可長 `--call-edges`（hub_refs 式消費的直接原料）→
  「0 prod callers 可刪」判斷的 Rust 側安全網閉環。
- 第二層：A5（修 CRG 鍵化）的觸發條件進一步後退——Rust 圖級 caller 查詢
  不再需要修 CRG（SCIP 邊＋自建 closure 即可）；修 CRG 只剩「NT graph
  自洽」價值。mosaic Rust 遷移側的 hazard 型流程可以直接建立在 SCIP 邊上。
- 負面情境：若 containment 歸屬在巨集生成代碼誤判（巨集展開體不在
  tree-sitter/語法樹中——但 SCIP occ 的 range 已是 ra 展開後位置，歸屬到
  巨集叫用處所在 fn，語義合理）；3.1% item-level 排除若含誤殺（如 const
  fn 初始化中的呼叫）→ 需在實作時抽驗。均可逆（薄層，隨時改）。

**決策類型**：雙向門（薄層實作＋試用，可回退；facade 邊界移動是文檔級）。

## 6. 建議（優先序）

1. **scip_refs 增 caller 邊模式**（小工程，建議下一張卡）：DEF-enc
   containment——資料已證、機制 ~50 行（per-doc span 表＋innermost 歸屬
   ＋**3 元素 single-line span 支援**〔巨集生成 fn；reviewer 反例〕）、
   餵 hub_refs/hazard 的「可刪判斷」與未來 mosaic Rust 波。可先試
   scip-callgraph 的輸出對帳（`--use-rust-analyzer`）再決定自建或整合。
   順帶固化 refs 口徑：item-level 機械分離（§2.2 修正後口徑——3.1% 中
   絕大多數非呼叫、≥35 顆巨集生成 fn 誤殺待實作修正）。
2. **lsp_mcp rust＝互動 caller 源已落地**（§2.4）：互動場景（session 內
   導航、即時 caller 查詢、「可刪」快速檢查）直接用 LSP
   `incomingCalls`——免 regen、常駐即時；scip_refs caller 邊模式服務
   錨定/批次/審計場景（governance、NT 對帳、graph 餵邊）。兩源並存
   =evidence fusion，不是二選一。
3. **試用 scip-callgraph**（零工程）：對 NT 索引跑一輪，與本報告 E2E 的
   18 refs 歸屬對帳——外部實作交叉驗證。
4. **watch bonsai-ninja**：季度回訪（誠實信號＋slice/impact 查詢面值得
   觀察是否長出語義層）。
5. **不動**：SCIP 更新紀律維持懶更新（drift WARN 驅動）；`--refresh`
   一條龍仍是可選小卡；A5 不修（觸發條件改為「NT graph 自洽需求出現」，
   實務上可能永不觸發）。
6. **明確不做**：Glean/Kythe/CodeQL（形態/授權錯位）、stack-graphs 復活
   （archived＋無 Rust）、任何 MCP 新波導入（語法級無增量）。

## 7. 方法論限制（誠實性宣告）

- **本地實證部分**（§2）：單一索引（NT @76213ffd、ra 版本隨 NT toolchain）
  ——DEF-enc＝body span 是此 ra 版本行為，其他版本需複驗；18 refs 逐筆
  人工判讀合理＋3 筆開檔核對（reviewer 加碼至 3/18）；96.9% 是歸屬成功率，
  非正確率（正確率有 18 refs 抽樣＋§2.4 LSP 交叉驗證，非全量核對）。
  e2e 歸屬為**行級粒度**（無 column）：enc 起訖行的 brace 邊界 ref、
  同 start line tie 的先見者勝，兩誤差源未量化（預期極小）。數字經
  fresh-eyes reviewer **獨立重跑 byte-level 複現**（239,602/232,078/
  7,524/18 refs 全命中），其機械反例（188 顆跨檔 enc 例外、35 顆巨集
  生成 fn 誤殺）已回修內文。
- **網路查證部分**：scip-callgraph 的內部機制未讀源碼（zread 兩次 -500；
  以本地 E2E 替代驗證同族技術）；bonsai-ninja 未本地試跑（README/docs.rs
  判讀）；Kythe Rust indexer 現況未深查（以「experimental rustc 內部依賴
  ＋Bazel 形態」判定，誤差風險低）；CodeQL 授權判定基於公開文件，未諮詢
  法務；MCP 新波僅抽查未逐一深掃。
- **單 session 弧**：結論供下個 session 以本報告為準重讀；引用的網路事實
  （archive 日期/preview 時點/星數）為 2026-08-25 快照。
- 未驗證：scip-callgraph 對 NT 規模索引的跑通性（建議 2 的待辦）。

## 附錄 A：本地可重跑指令

```bash
# DEF-enc 探針（body span 確認；64,164 顆 fn DEF 100% 帶 enc）
cd ~/Github/ai-rules && uv run python .agent-tmp/research/scip_def_enc_probe.py

# caller 邊 E2E（96.9% 歸屬＋EventStoreLifecycle.open 18 refs 逐筆）
cd ~/Github/ai-rules && uv run python .agent-tmp/research/scip_caller_e2e.py

# 前置調查腳本（enc 機制解碼鏈，保留供重驗）
#   scip_enc_residual.py / scip_enc_residual2.py / scip_enc_residual3.py
#   scip_probe_defrange.py / scip_enc_raw.py
```

## 附錄 B：網路查證清單（2026-08-25 快照）

- [github/stack-graphs](https://github.com/github/stack-graphs)（2025-09-09
  archived；[issue #420 支援語言](https://github.com/github/stack-graphs/issues/420)；
  [arXiv:2211.01224](https://arxiv.org/abs/2211.01224)）
- [facebookincubator/Glean](https://github.com/facebookincubator/Glean)
  （Rust via SCIP/LSIF via rust-analyzer；[Meta 工程blog](https://engineering.fb.com/2024/12/19/developer-tools/glean-open-source-code-indexing/)）
- [CodeQL Rust public preview（2025-06-30）](https://github.blog/changelog/2025-06-30-codeql-support-for-rust-now-in-public-preview/)；
  [支援語言表](https://codeql.github.com/docs/codeql-overview/supported-languages-and-frameworks/)
- [Beneficial-AI-Foundation/scip-callgraph](https://github.com/Beneficial-AI-Foundation/scip-callgraph)（MIT/Apache；
  Verus 生態）
- [liza-mas/scip-search](https://github.com/liza-mas/scip-search/)（enclosing
  range 歸屬技術描述）；[nusy-codegraph scip_calls](https://docs.rs/nusy-codegraph/latest/nusy_codegraph/scip_calls/index.html)
- [scip crate](https://crates.io/crates/scip)（Rust bindings）；[scip-code.org](https://scip-code.org/)；
  [sourcegraph/scip CLI](https://github.com/sourcegraph/scip)
- [japaric/cargo-call-stack](https://github.com/japaric/cargo-call-stack)；
  [robinmoussu/cargo-callgraph](https://github.com/robinmoussu/cargo-callgraph)
  （廢棄 rustc fork）
- [gromhacks/bonsai-ninja](https://github.com/gromhacks/bonsai-ninja)
  （[crates.io](https://crates.io/crates/bonsai-ninja-callgraph)，2026-08-17 首發）
- [mozilla/rust-code-analysis](https://github.com/mozilla/rust-code-analysis)
- [Joern docs](https://docs.joern.io/)（支援語言表無 Rust）
- [Kythe docs/releases](https://kythe.io/docs/)／
  [RELEASES.md](https://github.com/kythe/kythe/blob/master/RELEASES.md)
- [SCIP 發佈blog（增量為 roadmap）](https://sourcegraph.com/blog/announcing-scip)；
  [scip-clang incremental issue #183](https://github.com/sourcegraph/scip-clang/issues/183)
  （增量 SCIP 從未上市）
