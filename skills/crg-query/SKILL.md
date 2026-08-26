---
name: crg-query
description: Query the code knowledge graph — now the code-reality engine face (CRG MCP retired 2026-08-26) — correctly. Use when you need structural facts file-scanning cannot give efficiently — blast radius / impact radius of a change, who calls whom (callers/callees), affected execution flows, hub/bridge nodes, module communities, dead code, architecture overview, or token-efficient review context scoping — in a project with a graph (`.code-review-graph/graph.db`; MCP `code-reality` engine tools, or CLI `code-reality graph_query <op> --repo <root>`). Provides the LSP-vs-CRG division (symbol→LSP, impact/callers/flows→CRG), the assume-present + warn-if-absent rule, and anti-over-reliance (graph = structure, not runtime behavior). Prevents manually re-tracing dependencies with LSP/rg when the graph has them, and inferring behavior/correctness from graph edges.
when_to_use: Fires in a graph-equipped project (`code-reality` MCP engine tools available or `.code-review-graph/graph.db` exists) when the task needs structural/impact facts — "who calls X", "blast radius of this change", "is X dead code", "hubs/communities", "scope my review to impacted nodes only". Load BEFORE manually tracing imports/callers with LSP findReferences or rg. Does NOT fire in projects without CRG (no warn noise). Parallels nt-query (discipline for a tool).
---

# crg-query — Query the code knowledge graph correctly

You're in a project with a **code knowledge graph** — the code-reality engine face over `.code-review-graph/graph.db` (graph CRG retired 2026-08-26; the db format stays). The graph already holds who-imports-whom, call edges, communities, flows. Confusing what the graph gives you vs what LSP / reading code gives you causes two expensive mistakes.

## The one rule

> **Graph shows STRUCTURE, not BEHAVIOR. "A depends on B" ≠ "changing B breaks A" and ≠ "A is correct."**

A graph edge (A calls B / A imports B) is a *static, parse-time fact*. It says a dependency exists — not that it is exercised at runtime, not that exercising it is correct, not that changing B breaks A (A may never hit the changed path). The graph collapses hours of manual import-tracing into one query; it does NOT collapse the judgment of "does this matter, is it correct."

**Corollary — don't extrapolate behavior from one edge.** Runtime behavior splits by branch/config/data; the graph holds the union of parse-time edges, not the runtime path. "A calls B" where B has a config-driven branch does not say which branch runs. When behavior matters, read the code (or run it). Same shape as the one rule — don't describe the runtime whole from a static part.

## Detect CRG — assume present, warn if absent

This skill assumes the project has CRG. Detect once per task:

1. **MCP tools present** — code-reality engine tools callable (impact_radius / detect_changes / hub_nodes / bridge_nodes / list_communities / architecture_overview / list_flows / affected_flows / semantic_search / get_review_context / get_minimal_context / refs / callers / closure / audit) → engine live, use it. 兩種部署形態共用這組工具名：Claude 端 stdio（per-project `cwd` 展開，repo 預設正確）與共享 HTTP server（launchd `com.user.crg-mcp` 常駐 `127.0.0.1:5555`；ZCode/Codex 已掛接，OpenCode 待接）。
2. **Graph DB exists** — `.code-review-graph/graph.db` in repo root → graph present; if MCP tools absent, use CLI `code-reality graph_query <op> --repo <root>` (see Fallback).
3. **Neither** — CRG not installed in this project.

🔴 **GATE — assume + warn, do not silently degrade.** A review/planning command that expects CRG (impact/callers/scoping) and finds it absent must emit a one-line `[WARN] graph not available — structural context (impact/callers/flows) degraded; build: code-reality scip_nodes --bootstrap --repo <root>`, then fall back. **Silent fallback = the user gets a worse review without knowing why.** Do not block — proceed with the fallback below.

## 🔴 Shared-server rule — every call carries repo_root

共享 HTTP server 沒有 per-session cwd：`repo_root` 是唯一的 repo 路由鍵。**每個 `code-reality:*` 呼叫都必須帶 `repo_root=<當前 repo root 絕對路徑>`**（`list_repos_tool` / `cross_repo_search_tool` 除外——registry 級）。

省略的失敗形態是**自信假陰性**而非報錯：server 落到自身 cwd 的空 graph，回 `"graph is empty"` + not_found（2026-08-24 spike 實證：NT graph 近 8 萬節點下查 `InstrumentId` 回空）。查詢結果出現 "graph is empty" 指紋＝漏了 repo_root，補上重試。ZCode 端由 PreToolUse hook（`hooks/require-crg-repo-root.py`）機械阻擋缺參數呼叫；Claude stdio 端 repo 預設正確，統一帶上無害。

## LSP vs CRG vs code-reality — the division (core)

Three facts backends, complementary not competing:

| You need | Tool | Why |
|---|---|---|
| Symbol **definition / signature / type** | **LSP** `hover` / `goToDefinition` | Live, precise, ~50ms |
| **Single-symbol** references (who uses X) | **LSP** `findReferences` | Precise for one symbol |
| Symbol **callers/callees** (direct) | **LSP** `incomingCalls`/`outgoingCalls` OR **CRG** `query_graph` callers_of/callees_of | Either; CRG if traversing further |
| **Rust repo** symbol refs/defs（trait 消歧） | **code-reality** MCP `refs`／CLI `scip_refs`（SCIP；`[SRC]` provenance＋stale 守衛、跨 session 一致） | **只蓋 Rust**（rust-analyzer SCIP）——Python repo 維持 LSP；LSP 亦可但 workspace 狀態相依 |
| **Rust repo** callers／transitive callers | **code-reality** MCP `callers`（sites 級）／`closure`（BFS）；CLI `scip_refs --callers`／`--closure` | CRG `query_graph` 跨語言但無 site 細節；LSP `incomingCalls` 單層 |
| **Transitive blast radius** (A changed → all downstream N hops) | **code-reality** `impact_radius` | LSP can't do transitive efficiently |
| **Change → risk score + affected nodes** (from a diff) | **code-reality** `detect_changes`（MCP tool；`analyze_changes` 是 `changes.py` 內部函式，非 MCP tool） | LSP has no diff/risk model |
| **Affected execution flows** (which call chains hit) | **CRG** `get_affected_flows` | LSP has no flow concept |
| **Token-efficient review scoping** (read only impacted) | **CRG** `get_minimal_context` / `get_review_context` | LSP has no context-budgeting |
| **Hub / bridge / community / architecture overview** | **code-reality** `hub_nodes` / `bridge_nodes` / `list_communities` (directory or `--leiden`) / `architecture_overview` | No LSP equivalent |
| **Dead code** (no callers + no tests) | **CRG** `refactor_tool` mode=dead_code | Stronger than LSP zero-hits (cross-checks tests) |
| **Semantic search** ("where do we handle X concept") | **code-reality** `semantic_search` (keyword face; embeddings not adopted) OR rg | LSP is name-based |
| **Comments / strings / config / TODO** | **rg** | Neither LSP nor CRG index non-code |

**Rule of thumb:** *symbol* → LSP; *graph* (impact/callers/flows/community/scope) → CRG; *text* → rg. **Rust repo＋SCIP index 在場**：symbol refs/callers/closure 優先 code-reality（只蓋 Rust；Python repo 不變）。For "what does this change affect," start at CRG `get_impact_radius`/`detect_changes`, then LSP/Read for the specific symbols.

## Standard CRG query map

| Need | CRG tool (MCP / CLI) |
|---|---|
| "who calls X" / "X calls whom" | `query_graph` callers_of / callees_of (CLI: `query`) |
| "change these files → what's hit" | `get_impact_radius` (CLI: `impact`) |
| "diff → risk + affected nodes" | `detect_changes`（MCP tool；`analyze_changes` 是 `changes.py` 內部函式，非 MCP tool）(CLI: `detect-changes`) |
| "which flows pass through X" | `get_affected_flows` / `get_flow` (CLI: `flows` / `flow`) |
| "token-cheap context for reviewing this change" | `get_minimal_context` / `get_review_context` |
| "architectural hotspots / chokepoints" | `get_hub_nodes` / `get_bridge_nodes` |
| "module clusters / coupling" | `list_communities` / `get_community` / `get_architecture_overview` (CLI: `communities` / `architecture`) |
| "is X dead code" | `refactor_tool` mode=dead_code (CLI: `dead-code`) |
| "find symbol by concept/keyword" | `semantic_search_nodes` (CLI: `search`) — needs embeddings; else rg |

> **Stale graph check:** Rust repos — `code-reality scip_refs <sym> --repo` prints `[SRC] scip index @ <sha> · repo HEAD @ <sha>`; mismatch → regenerate the index before trusting results. Graph freshness — rebuild with `scip_nodes --bootstrap` (Python: rerun `scripts/lsp_harvest.py` in the code-reality repo first). Graph facts are build-time; stale graph = stale facts (parallel: LSP workspace state-dependence — re-verify before concluding).

## 🔴 Anti-over-reliance (the failure this skill prevents)

Graph edges are **static parse-time** facts. They miss:

- **Dynamic dispatch** — `obj.method()` resolves by runtime type; graph edges the declared type's method, not the subclass that runs.
- **Config / data-driven branches** — graph has both branches; runtime takes one.
- **Reflection / string-based calls / plugin registries** — graph can't see them. CRG's post-build resolvers catch SOME framework patterns (Spring DI, Temporal, Python lowercase-receiver via Jedi) — best-effort, not complete.
- **Cross-process / network calls** — not in the local graph.

🔴 **GATE:** before concluding "X is dead code" / "this change is safe — nothing depends on it" / "A always calls B" — for any *dynamic* case, hold evidence beyond the graph: read the call site, check for dispatch/config/reflection. A graph "no callers" is strong for static calls, **blind for dynamic**. Label graph-only findings `evidence-based`, not `confirmed`, when behavior is in question. (Parallel: nt-query — a data structure is not evidence of a capability ceiling.)

## Boundary — discipline vs CRG's workflow skills

CRG's `install` generates **four workflow skills** (`debug-issue`, `explore-codebase`, `refactor-safely`, `review-changes`) — *step-by-step procedures* for a task with the graph, project-local (`.claude/skills/`).

**`crg-query` is the discipline** — *how to query the graph correctly* (LSP-vs-CRG, warn-if-absent, anti-over-reliance), global (ai-rules).

They compose: a CRG workflow gives the steps; `crg-query` governs *how each query in those steps is interpreted* (don't over-infer, fall back to LSP/code when behavior matters). On conflict, this skill's discipline wins — workflows don't suspend verification.

## Fallback — CRG absent or stale

- **Not installed** → `[WARN]` (above) + LSP `findReferences`/`incomingCalls` (single-symbol, no transitive) + scan-project dep_graph (folder/module-level ripple) + rg. Accept degraded: no transitive impact, no flows, no communities.
- **MCP tools absent but graph.db exists** → CLI 直用：`code-reality graph_query <op> --repo <repo-root>`（ops: impact_radius detect_changes hub bridge communities arch_overview flows affected_flows review_context minimal_context search symbols；`--union` 接 SCIP 邊、`--leiden` 社區分層）。
- **Graph stale** → Rust: regen index + `scip_nodes --bootstrap`; Python: rerun the LSP-harvest adapter. Or verify critical edges with LSP and note the staleness.

## Reference

- **CLI commands:** `code-reality --help`（graph_query 家族＋scip_refs/scip_edges/scip_nodes 等）
- **code-reality MCP 接線：** stdio `code-reality-mcp --stdio`（plugin 形態）或 streamable-http `127.0.0.1:8200/mcp`（launchd `com.code-reality.mcp`）；工具呼叫一律帶 `repo_root`（不自動偵測）。舊 CRG server（com.user.crg-mcp @5555）已於 2026-08-26 cutover 時 bootout——plist 留檔可回滾。
- 註：本檔表格內的工具名（`query_graph`、`get_impact_radius`…）省略 server 實際暴露名的 `_tool` 後綴（`query_graph_tool` 等）
- **engine semantics 真相源:** ai-rules `skills/code-reality/SKILL.md`（跨 repo 單一源）＋code-reality repo `crates/AGENTS.md`
- **Sibling facts discipline:** [lsp-navigation](../../rules/lsp-navigation.md) (symbol queries) — this skill is its graph counterpart
- **Consumers:** [review-engine](../review-engine/SKILL.md) (change-impact lens), [arch-thinking](../arch-thinking/SKILL.md) §二 結構機械 (structure-facts lens)
