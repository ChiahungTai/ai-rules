# nt-query — Worked Examples & Concept→Symbol Seeds

Loaded on demand. `<NT_REPO>` is resolved in SKILL.md ("Locate the NT repo"). The full concept→doc→source map lives in `<NT_REPO>/docs/concepts/CLAUDE.md` (authoritative); this file adds (A) worked examples showing the exact tool sequence, and (B) common symbol seeds so you can `hover` immediately.

## A. Worked examples — the five query shapes

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
2. `Read` the `.pyi` docstring of `positions` → element type (stub says `list`; the docstring gives `list[Position]` — collection element types still live in docstrings, not signatures).
3. `rg "def positions" <NT_REPO>/nautilus_trader/cache/cache.pyx` → real filter logic / overloads the stub flattened.
4. **Answer:** grounded in stub + source, not memory.

### Example 3 — Event causal chain (mixed: concept + implementation)

**Question:** "How does an order fill become a position event?"

1. `Read <NT_REPO>/docs/concepts/events.md` → causal chain (fill → position event), handler dispatch order, tracing orders→positions.
2. `Read <NT_REPO>/docs/concepts/positions.md` → aggregation from fills, OMS snapshotting.
3. Symbol seeds (`Position`, `OrderFilled`, `PositionChanged`) → `LSP hover` / `findReferences` to confirm event types and dispatch.
4. **Answer:** the *contract* (docs) + the *types* (LSP).

### Example 4 — Balance/equity correctness (mixed: concept + implementation, the account-model trap)

**Question:** "After switching my venue to CASH, is `portfolio.equity()` giving the correct floating total equity — or do I still need my `balance_available + market_value` workaround?"

❌ **BAD path (path-extrapolation):**
Read `_update_margin_init` in `nautilus_trader/accounting/manager.pyx` → see it skips orders with no price → conclude "NT doesn't lock anything on open → equity must be wrong, keep the workaround." This reads the **pending-order path** and concludes about **post-fill** behavior — two different paths (the corollary in SKILL.md).

✅ **GOOD path (docs-first, then verify the formula + the cash flow):**
1. `Read <NT_REPO>/docs/concepts/portfolio.md` → "Equity formula": **CASH = `balances_total + Σ mark_value`**. ← the contract is stated here.
2. `Read <NT_REPO>/docs/concepts/accounting.md` → "Account types": Cash locks notional for pending orders; "Balance model": `total == locked + free`.
3. Confirm the cash flow that makes the formula hold: `Read <NT_REPO>/nautilus_trader/accounting/accounts/cash.pyx` → `calculate_pnls` inserts `-notional` on BUY → `balances_total` already reflects spent cash. (Accounting runs as Cython at runtime — see [account-model.md](account-model.md) "Layer".)
4. Confirm native uses `balances_total` (not `balance_available`): `rg "balances_total" <NT_REPO>/nautilus_trader/portfolio/portfolio.pyx` → inside `equity()`.
5. **Answer:** native `portfolio.equity(venue)` is correct for CASH. The workaround retires — it used `balance_available = total − locked`, understating by `locked` whenever pending orders existed. Caveats: `equity()` returns `dict[Currency, Money]`; call `missing_price_instruments(venue)` if it understates.

For the full account_type → 4-layers map, the two lifecycle paths, and gotchas (incl. the `margin_maint=0` silent trap), load [account-model.md](account-model.md).

### Example 5 — Usage contract (designer intent: is calling X in context Y safe?)

**Question:** "My TradingNode runs in a daemon thread. Can I call `node.stop()` / `node.dispose()` from the main thread to shut it down?"

❌ **BAD path (over-conclusion from method signature):**
`LSP hover` on `node.stop` → `stop(self) -> None` → "it's a public method, callable from anywhere" → call it cross-thread → intermittent `RuntimeError("Event loop stopped before Future completed")` that looks like an NT bug.

This is the exact anti-pattern: inferring a **usage boundary** from a method signature. "Public method" ≠ "safe in any context."

✅ **GOOD path (designer intent — examples + NT's own API choices + source):**
1. `rg -n "Thread.*daemon" <NT_REPO>/examples/live/` → **mixed, don't generalize from one family**: most examples (binance/bybit) use main-thread `run()` + SIGINT; but IB examples (`connect_with_tws.py` etc.) DO call `node.stop()` from a daemon timer thread.
2. NT's own cross-thread API choice: `rg "run_coroutine_threadsafe" <NT_REPO>/nautilus_trader/` → NT uses it (IB `client.py`) for cross-thread scheduling; `loop.create_task` is in-loop only. Does NT route `stop` through `run_coroutine_threadsafe`? No → `stop` isn't designed for cross-thread call.
3. Confirm via source: `Read <NT_REPO>/nautilus_trader/live/node.py` (`stop`, ~L381) → schedules via in-loop-only `loop.create_task(self.stop_async())`, wrapped in `try/except RuntimeError` that **swallows** the error. A cross-thread call hits wrong-thread `create_task` → `RuntimeError` silently swallowed.
4. **Answer:** No — `node.stop()/dispose()` are single-thread-contract APIs. IB examples "get away with it" only because the error is swallowed (that swallowed error is the tell, not a sanction). The shutdown race you see IS the contract violation. Fix = align to the contract (schedule stop in-loop via `loop.call_soon_threadsafe`, let `run()` return naturally, then `dispose()` when the loop is stopped) — not patch the symptom.

## B. Common concept → symbol seeds

Seeds are starting points — always verify via `LSP hover` / docstring. **If a seed does not resolve, stubs may be stale → see SKILL.md "Fallback".**

| Concept | Doc | Primary symbol seed(s) |
|---|---|---|
| Multi-account / accounting | `accounting.md` | `account_for_venue(venue, account_id)`, `Account` |
| Balance / equity / margin | `accounting.md` + `portfolio.md` | `Portfolio.equity()`, `CashAccount.calculate_pnls`, `MarginAccount.calculate_pnls`, `account_type_from_str()` — **load [account-model.md](account-model.md) for the full map + Cython-vs-Rust layer note** |
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

NT core modules are `.pyx` compiled to `.so`; without the generated `.pyi`, pyright/LSP is **completely blind** to them (`workspaceSymbol` / `findReferences` miss). The fork-maintained `.pyi` (regenerable via `scripts/lsp_stubs/`) restores vision. The generator now preserves **cross-package types precisely** (`order() -> Order | None`, real `Order`/`Position`/`Instrument`) — so for single-object returns, trust the signature. Two cases still need the **docstring**: (a) collection element types (stub says `list`/`dict`, docstring says `list[Position]`), and (b) return types the generator couldn't resolve (still `Any`, e.g. `cache.mark_price() -> Any` — its docstring gives `MarkPriceUpdate | None`). Hence the sequence: locate via `.pyi` → `hover` for the (now precise) signature → read docstring for collection elements / semantics → `rg .pyx` only for real internal structure.
