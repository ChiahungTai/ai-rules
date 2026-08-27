---
name: code-reality
description: "code_reality 工具鏈——repos 之上的 meta 層工具（Rust carrier，住 ~/Github/code-reality），跨 repo 消費單一入口。何時跑：implement 階段 1 baseline snapshot／post-build·code-review 弧模式 transition／debrief 機械底稿／cold-start boundary 掃描／「0 callers 可刪」判斷前 hub_refs hazard。含 repo profile（.code-reality.toml）schema 與 claims 口徑限制真相源。"
when_to_use: "Running code_reality tools (snapshot/transition/hub_refs+hazard/runtime_edges/boundary/boundary_build/delta_tour/chain_tour/graph_audit/scip_refs), authoring .code-reality.toml, or interpreting transition claims output. Tool availability check: .code-reality.toml in repo root OR code-reality snapshot --help exits 0."
argument-hint: "（程序 skill——不直接觸發；查閱用）"
allowed-tools: ["Read", "Bash"]
---

# code-reality 工具鏈（meta 層，Rust carrier）

工具住獨立 repo `~/Github/code-reality`（Rust carrier；repos 之上的 meta 層——**repo 事實歸 repo**，工具層不內建任何 repo 特例；binary 安裝見存在性偵測）。**呼叫形態**（從任意 repo cwd）：

```
code-reality <tool> --repo <repo-root> [args]
```

**存在性偵測（單一真相源——implement／code-review／debrief 三檔存在性述語直接引用；post-build 經 code-review 模式 B 間接）**：repo root 有 `.code-reality.toml`，或 `code-reality snapshot --help` exit 0（Rust 載體 `~/.cargo/bin/code-reality`——`cargo install --path ~/Github/code-reality/crates/code-reality` 安裝）。未裝 → 消費端跳過不阻擋（既有降級語義）。

**MCP 面（ZCode plugin）**：`refs`／`callers`／`closure`／`audit` 四工具對應 CLI `scip_refs` 家族——**CLI 無 `refs`/`callers` 子命令**，符號查詢 CLI 形態＝`code-reality scip_refs <symbol> --repo <repo>`（`--callers`／`--closure [--depth N]` 旗標）。instruction 引用工具名時標注面別（MCP `refs` vs CLI `scip_refs`）。

## 何時跑（程序接線）

| 時點 | 工具 | 消費者 |
|------|------|--------|
| implement 階段 1（build 起點） | `snapshot --label <ep>` | transition 的 before 基準 |
| 弧模式（code 已 commit、HEAD 越過 EP baseline） | `transition <a> <b> --ep <ep.md> --repo <repo>` | code-review 模式 B primed／post-build／implement 階段 6／debrief |
| hub symbol 波及盤點 | `hub_refs <symbol>`（內建 hazard 安全網；「可刪」判斷前必跑） | debrief 第 5 段 |
| CRG 同鍵去重受害符號 refs（Rust） | `scip_refs <Type.method> --repo <repo>`（repo-keyed slot，`--index` 顯式覆蓋）；`--audit --repo <repo>` 對帳 graph_audit 缺差 | graph_audit 發現缺差後的 callers 真相源 |
| runtime 逐函式耗時 | `runtime_edges`（viztracer trace） | 效能分析 |
| NT python↔Rust 邊 | `boundary_build --repo <nt>`（掃描建 sidecar）＋`boundary <symbol> --repo <nt>`（查詢） | v2 遷移地圖／縫分析 |
| 弧敘事載體 | `delta_tour`（snapshot 對 diff→tour）／`chain_tour`（callstack md→tours） | 人類 viewport |

**時點條件（transition 消費 gate——細節真相源 code-review 模式 B transition 段）**：HEAD == EP baseline（uncommitted）→ **不跑**（同 sha 零差異假陰性＋baseline sidecar 覆寫風險），退 LLM 對照＋`[WARN]`；snapshot 報 stale → 視同缺報告。

## 工具表（＋共用設施）

| 工具 | 職責 |
|------|------|
| `snapshot` | graph module-edge 導出（讀自有 `.code-reality/graph.db`）＋commit 錨定 sidecar（冪等；`_meta` 慣例） |
| `transition` | 兩 snapshot 邊集差異＋「EP 宣稱 vs 實際變動」對照 |
| `hub_refs` | hub symbol 廣度（callers/callees 按目錄、test/prod 切分）＋hazard 分層安全網（常駐 AST 級＋static_prod ≤ 2 觸發 rg 級 dynamic dispatch 偵測，規則在 `hazard` 模組——防「0 refs 可刪」誤判；`--hazard` 強制全掃、`--json` 含 `hazard_findings` 欄） |
| `runtime_edges` | viztracer trace → 逐函式 runtime 邊 |
| `boundary_build`／`boundary` | pyo3 宣告↔`.pyi` 合約 sidecar build／查詢 |
| `delta_tour`／`chain_tour` | 敘事/關聯載體（`.tour` 契約——渲染消費者 CodeTour）；chain_tour 產出同步 upsert `.tours/manifest.toml` |
| `tour_validate`／`tour_upgrade`／`tour_manifest` | corpus 治理：機械驗證（link 鍵／錨三態／manifest source）／舊格式遷移（pattern 補全＋cross-ref 活化，dry-run 預設）／manifest 讀寫 |
| `graph_audit` | 自有 graph.db **Rust 完整度稽核**——D1 同型別多 impl 風險掃描（per-block ≥2，非交集）＋D2 rust-analyzer symbols 對帳（kind 含 Test）；`--json` 鍵為治理鉤子契約；graph rebuild／rebase 大跳後跑（收編自 NT N1，2026-08-24 實測 219 缺差） |
| `scip_refs` | rust-analyzer SCIP 索引查詢——CRG 同鍵去重受害符號（見 graph_audit）的 def/refs 真相源 sidecar；`--audit` 與 graph_audit 缺差對帳（(定義檔, 方法名) 雙鍵歸屬）；索引 repo-keyed slot（`~/.mosaic/code-reality/scip/<repo-basename>/`——`--repo` 時 `--index` 可省略，多 repo 互蓋防護）＋生成後 `--stamp-meta --repo` 落版本 sidecar → 查詢首行 `[SRC] scip index @ <sha>`（與 repo HEAD 不一致 WARN＝漂移守衛；顯式 `--index` 無 sidecar 無 `--repo` 輸出不變）；衍生 sqlite 查詢面 `--build-cache`（落 `<index>.scip.db`，時序＝生成→stamp→build-cache；查詢自動優先，過期雙訊號〔mtime＋sidecar head〕自動重建，與 protobuf 路徑 stdout 位元組相同）；索引生成 ~8 分鐘、rebase 後重生（rust-analyzer scip，輸出寫 cwd） |
| `common`／`exclusions`／`profile`／`hazard` | 共用設施：`_meta`/`connect_ro`（WAL fallback）／排除前綴／profile 引擎／hub_refs hazard 判定層（六規則純函數——registry 表由 profile `[[hazard_registry]]` 注入） |

## repo profile（`.code-reality.toml`——repo 擁有）

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

無 profile：module fallback 頂層目錄、exclude 僅 `.venv/`、claims 恆 NONE、boundary crash-only、hazard registry 規則不命中（其餘 hazard 規則不依賴 profile）。

**authoring 程序**（新 repo 寫 profile——固定四步，勿即興）：

1. **判斷 module 規則**：找 code 主目錄（有實現邏輯的層，非 docs/tests/生成物）→ `prefix`＝主目錄（須尾斜線——profile 載入 assert，同 exclude）、`depth`＝「module 應是第幾層目錄」（`depth 1`＝prefix 直接子目錄；根檔案歸 prefix 本身）。多主目錄 repo 寫多條 `[[module]]`（有序首中）。判斷法：你希望 transition 對照表以什麼粒度列模組——那就是 module 層。**prefix 涵蓋度同時決定 chain_tour 幀存活**（幀路徑不在任何 prefix 下＝resolve 失敗落 external skip）——callstack 幀會經過的層都要涵蓋，含非「實現邏輯」的 stub 宣告層（如 `python/` .pyi）與 examples（NT 實證：缺 `python/`＋`examples/` 前綴致 .py 幀全滅）
2. **判斷 exclude**：非 code 目錄全列（文檔/研究產物/fixture/stubs/生成物 `dist`·`node_modules`）。**一律目錄粒度帶斜線**（`"docs/"` 非 `"docs"`——profile 載入 assert 強制；理由：startswith 匹配下無斜線會誤傷同名開頭檔，如 `.venv-setup.py`）
3. **scan_root 僅 pyo3 對帳 repo 需要**（rust 源 × `.pyi` stub 的 boundary 掃描）——一般 repo 不寫；非 NT 佈局的 `boundary_build` 會 crash-only（loud），屬設計
4. **smoke 驗證**：`code-reality snapshot --repo <repo> --label smoke` 跑一發，判讀 module 切分是否符合直覺（切錯→回步驟 1 改 prefix/depth）；之後 chain_tour 的 `not-in-graph` 統計是 graph 新鮮度信號、`external`/skip 統計是 prefix 覆蓋度信號（幀整批落 external＝prefix 缺層，回步驟 1 補）。profile 檔歸 repo root，commit 與否該 repo 自決

## 口徑限制（宣稱抽取——transition `--ep`／delta_tour）

claims regex 由 `[[module]]` prefixes 衍生（如 `mosaic_alpha/[a-z_0-9]+`）——**只認這些前綴的路徑 mention**。不符前綴的變更宣稱欄恆 NONE＝「未提供對照」（單欄邊集差異仍可用），**不當「EP 無宣稱」解讀**。相對路徑 mention（`adapters/sj/x.py` 形式）經 prefix 下目錄**存在性驗證**可正規化命中（`extract_ep_claims` 帶 repo_root 時；2026-08-25 dogfood 修）。delta_tour 宣稱**三態**：⚠ 只在可比較態；claims 空（profile 未載入/無可解析 mention）→ 整塊「未比對」零 ⚠＋stderr WARN；**claims 非空恆比對**——零命中＝如實呈現真漂移（⚠/✗）＋stderr 觀測 WARN（可能是真漂移或粒度問題）；步驟集由宣稱的 git range 嚴格推導（刪檔收斂單步、改名可走讀、範圍外結構上不可能）。

## 已知形狀假設（boundary——NT 專案）

`boundary_build` 深層形狀（pyi_module 段推導、method→class 同 crate join、pyclass derive 掃描）是 **NT 結構假設**：scan_root 可配，但 `pyi_module` 推導要求路徑含 `nautilus_trader` 段——**非 NT 佈局在此 crash（loud）**、對帳語義未驗證——新 repo 消費先 smoke（小樣本人工比對）。Known Gaps 明細見工具 docstring；Rust CALLS 邊品質口徑見 mosaic `ai-analysis/reports/rust-callgraph-probe.md`（同檔＋裸名 join 70% 命中——target 45% qualified 形態）。落地後果：profile 檔在**被掃 repo root**（如 NT checkout 會有一條 untracked `?? .code-reality.toml`）——屬設計（repo 事實歸 repo），commit 與否由該 repo 決定；snapshot/transition/boundary sidecar 產物預設落 `~/.mosaic/code-reality/`（sidecar home 延續——遷移 EP 凍結）。
