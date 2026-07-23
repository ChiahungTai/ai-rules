---
name: crg-query
description: Query code-review-graph (CRG) — the code knowledge graph — correctly. Use when you need structural facts file-scanning cannot give efficiently — blast radius / impact radius of a change, who calls whom (callers/callees), affected execution flows, hub/bridge nodes, module communities, dead code, architecture overview, or token-efficient review context scoping — in a project where CRG is installed (MCP `mcp__code-review-graph__*` tools, `.code-review-graph/graph.db`, or `code-review-graph` CLI). Provides the LSP-vs-CRG division (symbol→LSP, impact/callers/flows→CRG), the assume-present + warn-if-absent rule, and anti-over-reliance (graph = structure, not runtime behavior). Prevents manually re-tracing dependencies with LSP/rg when the graph has them, and inferring behavior/correctness from graph edges.
when_to_use: Fires in a CRG-equipped project (MCP `mcp__code-review-graph__*` tools available, `.code-review-graph/graph.db` exists, or `code-review-graph` CLI detected) when the task needs structural/impact facts — "who calls X", "blast radius of this change", "is X dead code", "hubs/communities", "scope my review to impacted nodes only". Load BEFORE manually tracing imports/callers with LSP findReferences or rg. Does NOT fire in projects without CRG (no warn noise). Parallels nt-query (discipline for a tool).
---

# crg-query — Query the code knowledge graph correctly

You're in a project with **code-review-graph (CRG)** — a Tree-sitter → SQLite structural graph exposed via MCP / CLI. The graph already holds who-imports-whom, call edges, communities, flows. Confusing what the graph gives you vs what LSP / reading code gives you causes two expensive mistakes.

## The one rule

> **Graph shows STRUCTURE, not BEHAVIOR. "A depends on B" ≠ "changing B breaks A" and ≠ "A is correct."**

A graph edge (A calls B / A imports B) is a *static, parse-time fact*. It says a dependency exists — not that it is exercised at runtime, not that exercising it is correct, not that changing B breaks A (A may never hit the changed path). The graph collapses hours of manual import-tracing into one query; it does NOT collapse the judgment of "does this matter, is it correct."

**Corollary — don't extrapolate behavior from one edge.** Runtime behavior splits by branch/config/data; the graph holds the union of parse-time edges, not the runtime path. "A calls B" where B has a config-driven branch does not say which branch runs. When behavior matters, read the code (or run it). Same shape as the one rule — don't describe the runtime whole from a static part.

## Detect CRG — assume present, warn if absent

This skill assumes the project has CRG. Detect once per task:

1. **MCP tools present** — `mcp__code-review-graph__*` callable → CRG live, use it.
2. **Graph DB exists** — `.code-review-graph/graph.db` in repo root → CRG installed; if MCP tools absent, the server isn't running (see Fallback).
3. **Neither** — CRG not installed in this project.

🔴 **GATE — assume + warn, do not silently degrade.** A review/planning command that expects CRG (impact/callers/scoping) and finds it absent must emit a one-line `[WARN] CRG graph not available — structural context (impact/callers/flows) degraded; install: uvx code-review-graph install && build`, then fall back. **Silent fallback = the user gets a worse review without knowing why.** Do not block — proceed with the fallback below.

## LSP vs CRG — the division (core)

Two facts backends, complementary not competing:

| You need | Tool | Why |
|---|---|---|
| Symbol **definition / signature / type** | **LSP** `hover` / `goToDefinition` | Live, precise, ~50ms |
| **Single-symbol** references (who uses X) | **LSP** `findReferences` | Precise for one symbol |
| Symbol **callers/callees** (direct) | **LSP** `incomingCalls`/`outgoingCalls` OR **CRG** `query_graph` callers_of/callees_of | Either; CRG if traversing further |
| **Transitive blast radius** (A changed → all downstream N hops) | **CRG** `get_impact_radius` | LSP can't do transitive efficiently |
| **Change → risk score + affected nodes** (from a diff) | **CRG** `detect_changes`（MCP tool；`analyze_changes` 是 `changes.py` 內部函式，非 MCP tool） | LSP has no diff/risk model |
| **Affected execution flows** (which call chains hit) | **CRG** `get_affected_flows` | LSP has no flow concept |
| **Token-efficient review scoping** (read only impacted) | **CRG** `get_minimal_context` / `get_review_context` | LSP has no context-budgeting |
| **Hub / bridge / community / architecture overview** | **CRG** `get_hub_nodes` / `get_bridge_nodes` / `list_communities` / `get_architecture_overview` | No LSP equivalent |
| **Dead code** (no callers + no tests) | **CRG** `refactor_tool` mode=dead_code | Stronger than LSP zero-hits (cross-checks tests) |
| **Semantic search** ("where do we handle X concept") | **CRG** `semantic_search_nodes` (needs `embed`) OR rg | LSP is name-based |
| **Comments / strings / config / TODO** | **rg** | Neither LSP nor CRG index non-code |

**Rule of thumb:** *symbol* → LSP; *graph* (impact/callers/flows/community/scope) → CRG; *text* → rg. For "what does this change affect," start at CRG `get_impact_radius`/`detect_changes`, then LSP/Read for the specific symbols.

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

> **Stale graph check:** CRG tool responses carry `_graph.head_matches_build`. If `false` (code changed since last build) → run `update` (`uvx code-review-graph update`) before trusting impact/caller results. Graph facts are build-time; stale graph = stale facts (parallel: LSP workspace state-dependence — re-verify before concluding).

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
- **MCP tools absent but graph.db exists** → server not running. Use CLI directly: `uvx code-review-graph <subcommand>` (same GraphStore). Or restart the AI tool to load the MCP server.
- **Graph stale** (`head_matches_build: false`) → `uvx code-review-graph update`; or note "graph pre-dates recent changes" and verify critical edges with LSP.

## Reference

- **CRG CLI commands:** `code-review-graph --help` (build / update / status / query / impact / detect-changes / dead-code / communities / architecture / search / refactor / serve …)
- **CRG architecture / tool map:** `<CRG_REPO>/code_review_graph/AGENTS.md` (resolve `<CRG_REPO>` — default `~/Github/code-review-graph`)
- **Sibling facts discipline:** [lsp-navigation](../../rules/lsp-navigation.md) (symbol queries) — this skill is its graph counterpart
- **Consumers:** [review-engine](../review-engine/SKILL.md) (change-impact lens), [arch-thinking](../arch-thinking/SKILL.md) §二 結構機械 (structure-facts lens)
