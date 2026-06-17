# nt-query — Worked Examples & Concept→Symbol Seeds

Loaded on demand. `<NT_REPO>` is resolved in SKILL.md ("Locate the NT repo"). The full concept→doc→source map lives in `<NT_REPO>/docs/concepts/CLAUDE.md` (authoritative); this file adds (A) worked examples showing the exact tool sequence, and (B) common symbol seeds so you can `hover` immediately.

## A. Worked examples — the three query shapes

### Example 1 — Capability (the failure this skill prevents)

**Question:** "Does NT support multiple accounts under one venue?"

❌ **BAD path (over-conclusion):**
`rg "_index_venue_account" <NT_REPO>/nautilus_trader/cache/cache.pyx` → see `dict[Venue, AccountId]` (1:1) → conclude "one venue = one account is a hard limit, multi-account is dead."

This is the exact mistake: inferring a **capability ceiling** from one **implementation** data structure. The dict is a lookup index, not a constraint.

✅ **GOOD path (docs-first):**
1. `Read <NT_REPO>/docs/concepts/CLAUDE.md` → "Accounting" row → `accounting.md`.
2. `Read accounting.md` → finds explicit "multi-account venues" + the `account_id` scope parameter.
3. Symbol seed `account_for_venue` → `LSP hover` on `account_for_venue` → confirms signature takes `(venue, account_id)`.
4. **Answer:** Yes — multi-account per venue is supported (docs-authoritative). The 1:1 dict is just one of the indexes.

### Example 2 — Implementation (consumer-validated)

**Question:** "How does cache expose positions, and what does it return?"

1. `LSP documentSymbol` on the cache `.pyi` (or `workspaceSymbol "positions"`) → locate `Cache.positions(...)`.
2. `Read` the `.pyi` docstring of `positions` → real return type (stub signature may say `Any`; docstring carries the truth).
3. `rg "def positions" <NT_REPO>/nautilus_trader/cache/cache.pyx` → real filter logic / overloads the stub flattened.
4. **Answer:** grounded in stub + source, not memory.

### Example 3 — Event causal chain (mixed: concept + implementation)

**Question:** "How does an order fill become a position event?"

1. `Read <NT_REPO>/docs/concepts/events.md` → causal chain (fill → position event), handler dispatch order, tracing orders→positions.
2. `Read <NT_REPO>/docs/concepts/positions.md` → aggregation from fills, OMS snapshotting.
3. Symbol seeds (`Position`, `OrderFilled`, `PositionChanged`) → `LSP hover` / `findReferences` to confirm event types and dispatch.
4. **Answer:** the *contract* (docs) + the *types* (LSP).

## B. Common concept → symbol seeds

Seeds are starting points — always verify via `LSP hover` / docstring. **If a seed does not resolve, stubs may be stale → see SKILL.md "Fallback".**

| Concept | Doc | Primary symbol seed(s) |
|---|---|---|
| Multi-account / accounting | `accounting.md` | `account_for_venue(venue, account_id)`, `Account` |
| Positions / OMS | `positions.md` | `Position`, `OmsType` |
| Cache (central store) | `cache.md` | `Cache`, `positions(...)`; **`_index_venue_account` is the over-inference trap — implementation only** |
| Orders (incl. emulated) | `orders.md` | `Order`, `OrderFactory` |
| Value types (fixed-point) | `value_types.md` | `Price`, `Quantity`, `Money`, `Price.from_str(...)` |
| Strategies / lifecycle | `strategies.md` | `Strategy`, `on_start`, `on_bar`, `on_event`, `submit_order` |
| Execution flow | `execution.md` | `ExecutionEngine` |
| Data / bar aggregation | `data.md` | `DataEngine` |
| Backtesting | `backtesting.md` | `BacktestEngine`, `BacktestEngineConfig` |
| Live trading node | `live.md` | `TradingNode` |
| Instruments | `instruments.md` | `Instrument`, `InstrumentId` |
| Events (causal chain) | `events.md` | `OrderFilled`, `PositionChanged`, `PositionOpened` |
| Configuration | `configuration.md` | msgspec frozen dataclasses; `T` vs `Option<T>` convention |

For any concept not seeded here, `Read <NT_REPO>/docs/concepts/CLAUDE.md` → the concept doc → extract symbols from its text/examples → `LSP hover`.

## C. Why the stub layer needs this sequence

NT core modules are `.pyx` compiled to `.so`; without the generated `.pyi`, pyright/LSP is **completely blind** to them (`workspaceSymbol` / `findReferences` miss). The `.pyi` restores vision, but stubgen-pyx flattens Cython types to `Any` in signatures — the **docstring** is where precise types survive. Hence the sequence: locate via `.pyi` → read docstring for types → `rg .pyx` only when you need the real internal structure. Skipping the docstring (trusting the `Any` signature) loses the type information the stub exists to provide.
