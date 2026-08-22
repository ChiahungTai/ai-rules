---
name: code-reality
description: "code_reality 工具鏈——repos 之上的 meta 層工具（住 ~/Github/ai-rules），跨 repo 消費單一入口。何時跑：implement 階段 1 baseline snapshot／post-build·code-review 弧模式 transition／debrief 機械底稿／cold-start boundary 掃描。含 repo profile（.code-reality.toml）schema 與 claims 口徑限制真相源。"
when_to_use: "Running code_reality tools (snapshot/transition/hub_refs/runtime_edges/boundary/boundary_build/delta_tour/chain_tour/graph_csv), authoring .code-reality.toml, or interpreting transition claims output. Tool availability check: .code-reality.toml in repo root OR uv run --project ~/Github/ai-rules python -m code_reality.snapshot --help exits 0."
argument-hint: "（程序 skill——不直接觸發；查閱用）"
allowed-tools: ["Read", "Bash"]
---

# code-reality 工具鏈（meta 層，住 ai-rules）

工具在 `~/Github/ai-rules`（repos 之上——**repo 事實歸 repo**，工具層不內建任何 repo 特例）。**呼叫形態**（從任意 repo cwd）：

```
uv run --project ~/Github/ai-rules python -m code_reality.<tool> --repo <repo-root> [args]
```

**存在性偵測（單一真相源——implement／code-review／debrief 三檔存在性述語直接引用；post-build 經 code-review 模式 B 間接）**：repo root 有 `.code-reality.toml`，或 `uv run --project ~/Github/ai-rules python -m code_reality.snapshot --help` exit 0。未裝 → 消費端跳過不阻擋（既有降級語義）。

## 何時跑（程序接線）

| 時點 | 工具 | 消費者 |
|------|------|--------|
| implement 階段 1（build 起點） | `snapshot --label <ep>` | transition 的 before 基準 |
| 弧模式（code 已 commit、HEAD 越過 EP baseline） | `transition <a> <b> --ep <ep.md> --repo <repo>` | code-review 模式 B primed／post-build／implement 階段 6／debrief |
| hub symbol 波及盤點 | `hub_refs <symbol>` | debrief 第 5 段 |
| runtime 逐函式耗時 | `runtime_edges`（viztracer trace） | 效能分析 |
| NT python↔Rust 邊 | `boundary_build --repo <nt>`（掃描建 sidecar）＋`boundary <symbol> --repo <nt>`（查詢） | v2 遷移地圖／縫分析 |
| 弧敘事載體 | `delta_tour`（snapshot 對 diff→tour）／`chain_tour`（callstack md→tours）／`graph_csv`（graph.db→CSV） | 人類 viewport |

**時點條件（transition 消費 gate——細節真相源 code-review 模式 B transition 段）**：HEAD == EP baseline（uncommitted）→ **不跑**（同 sha 零差異假陰性＋baseline sidecar 覆寫風險），退 LLM 對照＋`[WARN]`；snapshot 報 stale → 視同缺報告。

## 工具表（九工具＋共用）

| 工具 | 職責 |
|------|------|
| `snapshot` | CRG module-edge 導出＋commit 錨定 sidecar（冪等；`_meta` 慣例） |
| `transition` | 兩 snapshot 邊集差異＋「EP 宣稱 vs 實際變動」對照 |
| `hub_refs` | hub symbol 廣度（callers/callees 按目錄、test/prod 切分） |
| `runtime_edges` | viztracer trace → 逐函式 runtime 邊 |
| `boundary_build`／`boundary` | pyo3 宣告↔`.pyi` 合約 sidecar build／查詢 |
| `delta_tour`／`chain_tour`／`graph_csv` | 敘事/關聯載體（`.tour` 契約——渲染消費者 CodeTour） |
| `common`／`exclusions`／`profile` | 共用設施：`_meta`/`connect_ro`（WAL fallback）／排除前綴／profile 引擎 |

## repo profile（`.code-reality.toml`——repo 擁有）

mosaic 形態（module 規則＋exclusions）：

```toml
exclude = ["stubs/", "ai-analysis/", ".venv/", "snapshot/"]  # 通用 default 僅 .venv/
[[module]]        # module_of 規則（有序首中）＋claims 前綴來源
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

無 profile：module fallback 頂層目錄、exclude 僅 `.venv/`、claims 恆 NONE、boundary crash-only。

## 口徑限制（宣稱抽取——transition `--ep`）

claims regex 由 `[[module]]` prefixes 衍生（如 `mosaic_alpha/[a-z_0-9]+`）——**只認這些前綴的路徑 mention**。不符前綴的變更宣稱欄恆 NONE＝「未提供對照」（單欄邊集差異仍可用），**不當「EP 無宣稱」解讀**。

## 已知形狀假設（boundary——NT 專案）

`boundary_build` 深層形狀（pyi_module 段推導、method→class 同 crate join、pyclass derive 掃描）是 **NT 結構假設**：scan_root 可配，但 `pyi_module` 推導要求路徑含 `nautilus_trader` 段——**非 NT 佈局在此 crash（loud）**、對帳語義未驗證——新 repo 消費先 smoke（小樣本人工比對）。Known Gaps 明細見工具 docstring；Rust CALLS 邊品質口徑見 mosaic `ai-analysis/reports/rust-callgraph-probe.md`（同檔＋裸名 join 70% 命中——target 45% qualified 形態）。落地後果：profile 檔在**被掃 repo root**（如 NT checkout 會有一條 untracked `?? .code-reality.toml`）——屬設計（repo 事實歸 repo），commit 與否由該 repo 決定；snapshot/transition/boundary sidecar 產物預設落 `~/.mosaic/code-reality/`（sidecar home 延續——遷移 EP 凍結）。
