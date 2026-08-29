---
name: code-reality
description: "code_reality 工具鏈——repos 之上的 meta 層工具（Rust carrier，住 ~/Github/code-reality），跨 repo 消費單一入口。何時跑：新 repo 數據面一鍵準備（build）／implement 階段 1 baseline snapshot／post-build·code-review 弧模式 delta_tour 對照／debrief 機械底稿／cold-start boundary 掃描／「0 callers 可刪」判斷前 hub_refs hazard。含 repo profile（.code-reality.toml）生態示例與 claims 口徑生態語義。"
when_to_use: "Running code_reality tools (build/snapshot/hub_refs+hazard/runtime_edges/boundary/boundary_build/delta_tour/chain_tour/graph_audit/scip_refs), authoring .code-reality.toml, or interpreting delta_tour claims output. Tool availability check: .code-reality.toml in repo root OR code-reality snapshot --help exits 0."
argument-hint: "（程序 skill——不直接觸發；查閱用）"
allowed-tools: ["Read", "Bash"]
---

# code-reality 工具鏈（meta 層，Rust carrier）

> **受眾邊界（雙源分治，2026-08-29 拆遷 EP）**：CR plugin skill（`~/Github/code-reality/plugin/skills/code-reality/SKILL.md`，隨發版、plugin ≥0.1.6）＝**工具事實與坑的 standalone 真相源**（刷鏈時序、refs 密度語義、fallback 坑、profile schema＋authoring、口徑限制、boundary 假設）；本檔＝**生態操作真相源**（何時跑、接線、紀律、生態教訓收編）。同名 skill 並存時：操作依據本檔，工具細節以 plugin 版為準。

工具住獨立 repo `~/Github/code-reality`（Rust carrier；repos 之上的 meta 層——**repo 事實歸 repo**，工具層不內建任何 repo 特例；binary 安裝見存在性偵測）。**呼叫形態**（從任意 repo cwd）：

```
code-reality <tool> --repo <repo-root> [args]
```

**存在性偵測（單一真相源——implement／code-review／debrief 三檔存在性述語直接引用；post-build 經 code-review 模式 B 間接）**：repo root 有 `.code-reality.toml`，或 `code-reality snapshot --help` exit 0。**安裝單層＝uv（PyPI wheels；npm embedded face 已退役——registry 凍結 0.3.1 僅 deprecation grace，非候選）**：手動主面 `uv tool install code-reality`＋`pyrefly-producer`＋`code-reality-lsp-bridge`（免 Rust toolchain、落 `~/.local/bin`；rust-analyzer 仍系統依賴 `rustup component add rust-analyzer`；一次性用 `uvx code-reality <tool>`）；**plugin wrapper 首 session 自動 bootstrap**——`.mcp.json` wrapper 對 `--version` 做 plugin pin 前綴比對，missing/stale 即 `uv tool install --force code-reality==<pin>` 三 dist exact pin（MCP／CLI 同步釘 plugin 版）、無 uv loud 127＋指引、`CODE_REALITY_BOOTSTRAP=off`＝dev cargo-HEAD 機逃逸；**cargo＝developer face**（checkout 開發機 `cargo install --path ~/Github/code-reality/crates/code-reality`）。**dev 機＝cargo 權威（構造保證，2026-08-29 三殼實證）**——`~/.zshenv` 一行 cargo-first：terminal＝live rc；CC＝per-session 快照（新 session 自癒）；ZCode＝per-app 快照（重啟自癒）——一般呼叫即 cargo HEAD 面，無需 workaround。wrapper bootstrap 落的 uv-pinned 五顆續存 `~/.local/bin`（GUI 啟動 wrapper 場景與消費者預設面）——**需 pinned release 行為時全路徑呼 `~/.local/bin/code-reality`**（或 `uvx`）。權威面分歧窗口＝快照齡，stale WARN 橋接其間（uv-pinned 版同樣自報）。binary 查證在當下殼 `command -v`＋`--version` 直讀、勿跨殼假定。安裝/wrapper 細節真相源＝CR `plugin/README.md`。**新舊自報**：`--version` 帶嵌入 rev（`<pkg>+<rev>`）；CR checkout HEAD 前移過嵌入 rev 或帶 uncommitted `crates/` edits 時，WARN-wired bins 每進程一行 stderr stale WARN——binary 查證標準程序＝`--version` 直讀 rev。未裝 → 消費端跳過不阻擋（既有降級語義）。

**MCP 面（ZCode plugin）**：`refs`／`callers`／`closure`／`audit` 四工具對應 CLI `scip_refs` 家族——**CLI 無 `refs`/`callers` 子命令**，符號查詢 CLI 形態＝`code-reality scip_refs <symbol> --repo <repo>`（`--callers`／`--closure [--depth N]` 旗標）。instruction 引用工具名時標注面別（MCP `refs` vs CLI `scip_refs`）。

## 何時跑（程序接線）

| 時點 | 工具 | 消費者 |
|------|------|--------|
| 新 repo／缺 graph.db（數據面準備） | `build --repo <repo>`（一鍵傘形：偵測→producer→graph_db build；mixed repo 兩腿 cat-merge 雙語言合一） | 任何 graph 面消費的前置 |
| implement 階段 1（build 起點） | `snapshot --label <ep>` | delta_tour 的 before 基準 |
| 弧模式（code 已 commit、HEAD 越過 EP baseline） | `delta_tour <a> <b> --ep <ep.md> --repo <repo>` | code-review 模式 B primed／post-build／implement 階段 6／debrief |
| hub symbol 波及盤點 | `hub_refs <symbol>`（內建 hazard 安全網；「可刪」判斷前必跑） | debrief 第 5 段 |
| graph_audit 缺差對照 refs（Rust） | `scip_refs <Type.method> --repo <repo>`（repo-keyed，`--index` 顯式覆蓋）；`--audit --repo <repo>` 對帳 graph_audit 缺差 | graph_audit 發現缺差後的 callers 真相源 |
| runtime 逐函式耗時 | `runtime_edges`（viztracer trace） | 效能分析 |
| NT python↔Rust 邊 | `boundary_build --repo <nt>`（掃描建 sidecar）＋`boundary <symbol> --repo <nt>`（查詢） | v2 遷移地圖／縫分析 |
| 弧敘事載體 | `delta_tour`（snapshot 對 diff→tour）／`chain_tour`（callstack md→tours） | 人類 viewport |

**時點條件（delta_tour 消費 gate——細節真相源 code-review 模式 B）**：HEAD == EP baseline（uncommitted）→ **不跑**（同 sha 零差異假陰性＋baseline sidecar 覆寫風險），退 LLM 對照＋`[WARN]`；snapshot 報 stale → 視同缺報告。退化 pair／跨面 files pair 時 delta_tour 自動前置對應警示。

## 工具表（＋共用設施）

| 工具 | 職責 |
|------|------|
| `build` | **數據面一鍵傘形**（v0.4.0 起）：偵測語言面→spawn producer（`pyrefly-index`／`rust-analyzer scip <repo 目錄>`）→in-process `graph_db build`＋`ensure_indexes`；`--producer rust／python` 顯式覆蓋；mixed repo 兩腿 cat-merge＝單一雙語言 graph；陷阱已守衛——scip 需傳**目錄**非 Cargo.toml（後者 exit 0 空輸出）、<128B 空索引擋 |
| `snapshot` | graph module-edge 導出（讀自有 `.code-reality/graph.db`）＋commit 錨定 sidecar（冪等；`_meta` 慣例） |
| `hub_refs` | hub symbol 廣度（callers/callees 按目錄、test/prod 切分）＋hazard 分層安全網（常駐 AST 級＋static_prod ≤ 2 觸發 rg 級 dynamic dispatch 偵測，規則在 `hazard` 模組——防「0 refs 可刪」誤判；`--hazard` 強制全掃、`--json` 含 `hazard_findings` 欄）；⚠️ CLI 面無 stale guard——過期 index 上照跑，判讀前先看 `[SRC]` 行 |
| `runtime_edges` | viztracer trace → 逐函式 runtime 邊 |
| `boundary_build`／`boundary` | pyo3 宣告↔`.pyi` 合約 sidecar build／查詢 |
| `delta_tour`／`chain_tour` | delta_tour＝snapshot 對 diff→tour＋**EP 宣稱對照**（三態＋實際變動模組＋退化/跨面 pair 自動警示）；`--out-dir` 為 **cwd-relative 非 repo-relative**（落點在執行 cwd 的 `.tours/delta/`）；chain_tour＝callstack md→tours（upsert `.tours/manifest.toml`）；`.tour` 契約——渲染消費者 CodeTour |
| `tour_validate`／`tour_upgrade`／`tour_manifest` | corpus 治理：機械驗證（link 鍵／錨三態／manifest source）／舊格式遷移（pattern 補全＋cross-ref 活化，dry-run 預設）／manifest 讀寫 |
| `graph_audit` | 自有 graph.db **Rust 完整度稽核**——D1 同型別多 impl 風險掃描（per-block ≥2，非交集）＋D2 rust-analyzer symbols 對帳（kind 含 Test）；graph rebuild／rebase 大跳後跑 |
| `sidecar_migrate` | 舊 home slot → in-repo 搬遷（`~/.mosaic` 退役過渡橋；缺索引錯誤自動提示） |
| `scip_refs` | SCIP 索引查詢——graph_audit 缺差對照（雙鍵歸屬）的 def/refs 真相源 sidecar；查詢首行 `[SRC] scip index @ <sha>`＋與 repo HEAD 不一致 WARN＝漂移守衛；**重生索引直呼 repo-pin binary**（rustup proxy 依 cwd 解析 toolchain——從 any cwd outside the repo 呼叫會靜默降 toolchain；事故實案＝CR plugin skill）；索引生成 ~8 分鐘、輸出寫 cwd；衍生 sqlite `--build-cache` 過期雙訊號自動重建（本檔持有——未吸收項）；DEF 只收**函式/方法**——struct/trait 名不可作查詢鍵（用其方法符號，如 `EventStore::high_watermark`） |
| `common`／`exclusions`／`profile`／`hazard` | 共用設施：`_meta`/`connect_ro`（WAL fallback）／排除前綴／profile 引擎／hub_refs hazard 判定層（六規則純函數——registry 表由 profile `[[hazard_registry]]` 注入） |

## Python occurrence producer（pyrefly 預設面）

Python repo 的 occurrence 面預設生產者＝`pyrefly-index`（code-reality repo `crates/pyrefly-producer`；引擎 git-dep pin 實證 rev 非 tag——crates.io 只有占位套件，升級是顯式 commit）。**資料面準備主入口＝`code-reality build --repo <repo>` 一鍵**（工具表傘形；以下手動分步鏈＝除錯用）：

```
pyrefly-index --repo <repo>    # uv tool install pyrefly-producer 後（bin 落 ~/.local/bin）；dev cargo face＝cargo install --path ~/Github/code-reality/crates/pyrefly-producer；
                               # 或 cargo run --release -p pyrefly-producer --bin pyrefly-index -- --repo <repo>
```

→ in-repo slot `<repo>/.code-reality/`（data-plane 統一後 `~/.mosaic` 已退役；舊 slot 以 `code-reality sidecar_migrate --repo <repo>` 搬遷，缺索引錯誤自動提示過渡橋）→ `--stamp-meta` → `--build-cache` 時序；fail-loud——無 `.py` 檔即 Err。**時序安全語義（單跑 producer 後直接 build 亦安全）、refs 密度語義（對 LSP golden 的預期管理、`golden_corpus --normalize`）、scip-python fallback 專屬坑＝CR plugin skill 真相源**（吸收自本檔 A2-A5）。

**生態分工**：`lsp_harvest` 保留＝golden oracle 產生器（hover／diagnostics 等 type 面的 pyright 不在 producer 管轄）；不同 producer 不混用同槽＋lsp cache 優先短路陷阱＝CR plugin skill。

## repo profile（`.code-reality.toml`——repo 擁有；生態示例）

mosaic 形態（module 規則＋exclusions）：

```toml
exclude = ["stubs/", "ai-analysis/", ".venv/", "snapshot/"]  # 通用 default 僅 .venv/
[[module]]        # module_of 規則（有序首中）＋claims 前綴來源＋chain_tour PathResolver pkg_roots——prefix 覆蓋度＝幀存活度（路徑不在任何 prefix 下 resolve 失敗落 external skip；NT 實證 .py 幀全滅，補 python/+examples/ 前綴救回）
prefix = "mosaic_alpha/"
depth = 1         # module＝prefix 下第 depth 層目錄；根檔案歸 prefix 本身
```

NT 形態（加 boundary 掃描根——兩 repo 目錄結構不同，勿混抄）：

```toml
[[module]]
prefix = "crates/"
depth = 1
[[scan_root]]     # boundary 掃描根；缺 → boundary_build crash-only 要求顯式 --repo
path = "crates/**/*.rs"
pyi = "python/nautilus_trader/**/*.pyi"
```

registry auto-discovery repo（hazard 偵測的 `registry-auto-discovery` 規則——有 registry 掃描註冊機制的 repo 才寫，如 mosaic conditions/features）：

```toml
[[hazard_registry]]   # 定義檔在 package_prefix 下＋名稱尾 suffix → 註冊推定（callers 邊不涵蓋）
package_prefix = "mosaic_alpha/conditions/"
suffix = "Condition"
register_fn = "auto_register_conditions"
registry = "CONDITION_REGISTRY"
evidence = "mosaic_alpha/conditions/discovery.py:149"   # 可選——註冊鏈證據顯示用
```

**無 profile fallback、authoring 程序四步（判斷 module 規則→exclude 目錄粒度帶斜線→scan_root 僅 pyo3 對帳 repo→smoke 驗證）、`hazard_registry` 欄位語義＝CR plugin skill 真相源**（英文通用版，吸收自本檔 A7＋D8 收尾 0.1.7）；示例塊為生態內領域形態參考。

## 口徑限制（宣稱抽取——delta_tour `--ep`）

claims regex 由 `[[module]]` prefixes 衍生——只認這些前綴的路徑 mention；不符前綴的變更宣稱欄恆 NONE＝「未提供對照」，**不當「EP 無宣稱」解讀**。完整三態語義與讀法＝CR plugin skill "Reading claims output (delta_tour)" 段（吸收自本檔 A8）。

## 已知形狀假設（boundary——NT 專案）

`boundary_build` 深層形狀（pyi_module 段推導、method→class 同 crate join、pyclass derive 掃描）是 **NT 結構假設**：非 NT 佈局 crash（loud）屬設計、對帳語義未驗證——新 repo 消費先 smoke；Known Gaps 明細見工具 docstring（吸收版＝CR plugin skill）。落地後果：profile 檔在**被掃 repo root**（untracked `?? .code-reality.toml` 屬設計——repo 事實歸 repo，commit 與否由該 repo 決定）；sidecar 產物落 `<repo>/.code-reality/`（in-repo 自帶 gitignore）。
