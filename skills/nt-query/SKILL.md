---
name: nt-query
description: Query NautilusTrader (NT) correctly — docs-first for capability/concept, LSP-on-Cython-stubs for implementation. Use when investigating what NT supports ('NT 支援/能不能/能力/概念', multi-account, OMS, position 計算, accounting, value types, emulated orders) or where/how NT implements something (cache, model, execution, backtest config, 'NT symbol 在哪', BacktestEngine, TradingNode, Actor, on_bar, on_order_filled, submit_order). Prevents over-inferring a capability boundary from one source data structure.
when_to_use: Fires when a consumer project's LLM investigates NautilusTrader — "does NT support X", "NT 能不能", "how does NT compute position", "where is X defined in NT", or when reading nautilus_trader/ source / .pyi stubs. Load BEFORE diving into NT source.
---

# nt-query — Query NautilusTrader correctly

You're investigating **NautilusTrader (NT)** — the Cython+Rust quant platform. NT has two distinct knowledge layers; confusing them causes the most expensive mistake.

## The one rule

> **Docs decide CAPABILITY. Source reveals IMPLEMENTATION. Never infer a capability boundary from a single data structure.**

`dict[Venue, AccountId]` (a 1:1 helper index) is an *implementation choice*, not proof that "one venue = one account" is a hard limit. A data structure shows how something is built today — not what the platform can do.

## Locate the NT repo — resolve `<NT_REPO>` once

This skill needs a local NautilusTrader checkout (with `docs/concepts/`). All paths below use `<NT_REPO>`; resolve it in this order, then substitute everywhere (do this once per session):

1. **Override** — env var `NT_REPO_PATH` is set → use it. (A consumer may set this in `.claude/settings.json` `env` to point at a specific checkout or worktree.)
2. **Default** — `~/Github/nautilus_trader`; verify with `test -d ~/Github/nautilus_trader/docs/concepts`.
3. **Discover** — `fd -t d nautilus_trader ~` (or `find ~ -type d -name nautilus_trader -maxdepth 5`); pick the checkout that contains `docs/concepts/` (not a `.venv` site-packages copy).
4. **Not found** — stop and tell the user: "nt-query needs a local NautilusTrader checkout with `docs/concepts/`; set `NT_REPO_PATH` or give me the path."

If you are working inside an NT worktree, `<NT_REPO>` is that worktree's root (its `docs/concepts/` matches the code you're editing).

## Upstream docs vs this fork — pick the right truth

- **context7 / online docs** describe **upstream NT** — fine for general concepts and syntax (not fork-state claims).
- **`<NT_REPO>`** describes **this fork's runtime**, which diverges from upstream: Cython runtime in use, Rust/PyO3 migration incomplete (e.g. cache's PostgreSQL backing is still WIP).
- For any claim about what THIS fork actually does — capability, architecture, language layer, enabled features — ground in `<NT_REPO>`, not context7. context7 structurally cannot see this fork's state.
- Cautionary case: an overview once claimed "Cache is in Rust" (drawn from upstream-general context7). Ground truth is layered — `cache.pyx:Cache` (the in-memory core) is **Cython for hot-path performance**; only the DB-backing adapters wrap Rust (`nautilus_pyo3`). Two errors compounded: upstream-vs-fork drift **and** generalizing one layer's language (Rust backing) to the whole module — the same anti-pattern as the one rule (don't infer the whole from one part). When a module mixes layers, name the layer.

## Step 1 — Classify the query

| Shape | Signal words | Authoritative source |
|---|---|---|
| **Capability / concept** | "does NT support…", "can NT…", "is X a hard limit", "NT 能力/概念/支援" | `docs/concepts/` **first** → Step 2 |
| **Implementation / symbol** | "where is X", "signature of Y", "who calls Z", "NT symbol 在哪/實作" | **LSP on `.pyi`** → `.pyx` source → Step 3-4 |
| **API contract** | "what params does X take" | `docs/api_reference/` OR `.pyi` + docstring → Step 3 |

Most real questions are **mixed** ("can NT do X, and how do I call it?") → run the **capability path first**, then implementation.

## Step 2 — Capability path (docs-first)

1. Open `<NT_REPO>/docs/concepts/CLAUDE.md`. It maps each concept → doc file → source module, with a **"Non-derivable knowledge"** column that tells you what only the docs can answer.
2. Read the concept file (e.g. `accounting.md`, `positions.md`). Extract: (a) what NT explicitly says it supports, (b) any symbol names mentioned, (c) `:::note` / `:::warning` behavioral contracts.
3. **The docs statement IS the answer.** If `accounting.md` says "multi-account venues", multi-account is supported — full stop.
4. 🔴 **GATE — the failure this skill exists to prevent:** before concluding "NT can / cannot do X", you must hold **docs evidence** — an explicit statement, a `:::note`/`:::warning`, or a verified absence in the relevant concept doc. A source data structure is **not** evidence of a capability ceiling. If you only have a structure, stop and return to Step 2.1.
5. **The GATE follows claims, not query type.** It applies to any "NT can / cannot / is X" statement wherever it appears — including a line dropped inside an overview or a casual answer, not only when you run a dedicated capability query. Overview framing does not suspend verification: a specific, falsifiable, fork-dependent claim needs docs / `<NT_REPO>` evidence even mid-sentence. "Probably right, I'll leave it" is not evidence — some unverified claims are already wrong, and you cannot tell which without grounding.

## Step 3 — Implementation path (LSP on the stub layer)

Use the symbol names from Step 2 (or the query) as seeds:

- `workspaceSymbol "<Name>"`, or `documentSymbol` on the `.pyi` → locate the class/method
- `hover` → signature. **Then `Read` the `.pyi` docstring** — stub signatures are often `Any`, but the docstring carries the precise types (stubs were generated from `.pyx` precisely to preserve these).
- `findReferences` / `incomingCalls` → who uses it

NT `.pyi` sit next to the `.pyx`/`.so`; in a consumer repo they reach the LSP via `make sync-stubs`.

## Step 4 — Source truth (only when docs/stubs are insufficient)

`rg` the `.pyx` for the real internal structure. This answers *how* something is implemented — never *whether* it is possible.

**Discipline:** label every source finding as IMPLEMENTATION, not CAPABILITY. `cache._index_venue_account: dict[Venue, AccountId]` = "there is a venue→account lookup index" (implementation), NOT "NT allows only one account per venue" (capability — check docs).

## Fallback — LSP is blind / stubs stale

If LSP can't resolve NT Cython symbols (`workspaceSymbol` empty, or `attr-defined` / `Unknown` on `Bar` / `Price` / `Quantity` / `InstrumentId`):

→ **stubs are not synced.** Interim: `rg` the `.pyi` / `.pyx` directly. **Flag to the user: run `make sync-stubs` in the consumer repo** (common cause: `uv sync` or an NT upgrade wiped the venv `.pyi`). This is a known recurring failure — do not struggle silently.

## Reference material

- **Concept → doc → source map (authoritative — do not re-derive):** `<NT_REPO>/docs/concepts/CLAUDE.md`
- **Docs root navigation:** `<NT_REPO>/docs/CLAUDE.md`
- **NT module guide + LSP stub workflow:** `<NT_REPO>/CLAUDE.md`
- **LSP stub generation tools:** `<NT_REPO>/scripts/lsp_stubs/README.md`
- **The failure this prevents (case study):** `<NT_REPO>/ai-analysis/analysis/2026-06-16-nt-docs-over-source.md`
- **Worked examples (3 query shapes, exact tool calls) + common concept→symbol seeds:** [reference.md](reference.md)
