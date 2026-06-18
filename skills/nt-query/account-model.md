# nt-query — Account, Balance & Equity Model

Loaded on demand for questions about account types, balances, equity, margin, or PnL computation. `<NT_REPO>` is resolved in SKILL.md. This file gives the **non-derivable design model** (how `account_type` fans out across layers), the **two lifecycle paths** that most often get conflated, navigation seeds, and the failure modes that trap investigators. Authoritative concept docs: `<NT_REPO>/docs/concepts/accounting.md` and `portfolio.md` — read them first.

> **Margin query checklist** (if you're chasing a balance/equity/margin bug): (1) which `account_type`? it selects the 4 layers below; (2) margin has **two lifecycle paths** — pending (`orders_open`) vs filled — verify the one your scenario hits, not just one; (3) Cash/Margin `calculate_pnls` **branch by account_type** — don't read one and assume the other; (4) is the instrument's `margin_maint` actually set? default `0` is the #1 trap (gotcha #1).

## Layer — Cython is the runtime; Rust is the PyO3 equivalent

Accounting/balance/equity logic runs as **Cython** in this fork's runtime: `nautilus_trader/portfolio/portfolio.pyx` imports `AccountsManager` from `nautilus_trader.accounting.manager`, and `accounting/accounts/{cash,margin,base,betting}.pyx` implement `calculate_pnls` and balance logic. The Rust files under `crates/model/src/accounts/` and `crates/portfolio/src/manager.rs` are the **PyO3 equivalent** (for future Rust-native / PyO3 runtime) — they are **not** executed by the Cython `Portfolio`. **For implementation verification, read the `.pyx` under `accounting/`, not the Rust `.rs`.** Both layers implement the same logic; the docs contracts hold for either.

## The core model — `account_type` selects four independent layers

`AccountType` (CASH / MARGIN / BETTING), set at venue-attach time, decides **four things at once**. Confusing them is the #1 source of wrong assumptions about balances and equity.

| Layer | CASH (and BETTING) | MARGIN |
|---|---|---|
| Balance cash flow per fill (`calculate_pnls`) | ±full notional every fill → `cash.pyx::calculate_pnls` (`accounting/accounts/cash.pyx`) | only on position reduction → `margin.pyx::calculate_pnls` (`accounting/accounts/margin.pyx`); options realize every fill |
| Effect of BUY-open on `balances_total` | −notional (settles in full) | unchanged (collateral reserved via margin model) |
| `Portfolio.equity()` second term | `balances_total + Σ mark_value` (`portfolio/portfolio.pyx::equity`) | `balances_total + Σ unrealized_pnl` |
| Instrument eligibility | cannot trade futures/perpetuals; uncovered Equity SELL blocked (both in `backtest/engine.pyx`) | all instruments |

Docs ground truth: `accounting.md` ("Account types" table + "Balance model") and `portfolio.md` ("Equity formula"). **The docs already state the equity-formula split by account type — read `portfolio.md` before the source.** Source only confirms the formula is implemented as documented.

## Two lifecycle paths — never read one and conclude about the other

Balance/margin behavior also splits by **order lifecycle stage**, processed by separate code paths in `AccountsManager` (`nautilus_trader/accounting/manager.pyx`):

1. **Pending-order path** (order submitted, not yet filled) — iterates `orders_open`:
   - CASH → `_update_balance_locked` (reserve notional for the would-be position)
   - MARGIN → `_update_margin_init` (reserve initial margin)
2. **Filled-position path** (order has filled):
   - CASH → `calculate_pnls` (`cash.pyx`) settles ±notional into `balances_total`; the filled order leaves `orders_open`, so it no longer contributes `locked` → with no pending orders, CASH `locked=0`.
   - MARGIN → maintenance margin via `calculate_margin_maint` (`manager.pyx`), plus realized PnL only on reduction.

**Failure pattern this prevents:** reading `_update_margin_init` (the *pending* path) and concluding "a market order with no price is skipped, so nothing locks." That describes pending-order reservation — NOT what happens after the fill. Always verify the path matching your scenario's lifecycle stage. Same anti-pattern shape as the one rule: don't describe the whole from one part — here, don't describe one stage from another.

## Navigation seeds (concept → symbol → where)

Resolve symbols with LSP first; the file path is a fallback when LSP is blind (Cython) or to disambiguate. **Paths below are the Cython runtime truth; the Rust `crates/model/src/accounts/` + `crates/portfolio/src/manager.rs` are the PyO3 equivalent (see Layer note).**

| You want to find | Symbol (LSP seed) | File fallback (Cython runtime) |
|---|---|---|
| Where `account_type` is set (backtest) | `BacktestEngine.add_venue(account_type=...)` | `nautilus_trader/backtest/engine.pyx` |
| Convert account_type to/from string | `account_type_from_str()` / `account_type_to_str()` — **module functions, not classmethods** | `nautilus_trader/model/functions.pyx` (`.pyi` for LSP) |
| Test an account's type | `account.is_cash_account` / `.is_margin_account` / `.type` | `accounting/accounts/base.pyx` |
| Cash/betting cash-flow logic | `CashAccount.calculate_pnls` | `nautilus_trader/accounting/accounts/cash.pyx` |
| Margin cash-flow logic | `MarginAccount.calculate_pnls` | `nautilus_trader/accounting/accounts/margin.pyx` |
| The AccountsManager (both lifecycle paths) | `AccountsManager` | `nautilus_trader/accounting/manager.pyx` |
| Equity formula | `Portfolio.equity()` | `nautilus_trader/portfolio/portfolio.pyx` (+ docs `portfolio.md`) |
| Margin computation model | `StandardMarginModel` / `LeveragedMarginModel` (subclass `MarginModel`) | `nautilus_trader/accounting/margin_models.pyx` |
| Initial vs maintenance margin | `calculate_margin_init` / `calculate_margin_maint` | margin model + `accounting/manager.pyx` |

## Gotchas (non-derivable failure modes)

1. **`margin_init` / `margin_maint` default to `Decimal(0)`** when not passed (`nautilus_trader/model/instruments/equity.pyx`, likewise `futures_contract.pyx` / `crypto_future.pyx`). On a MARGIN venue, maintenance margin = `notional × margin_maint` = `notional × 0` = 0 → **nothing locked → equity inflates by the position's notional**. This is **by design** (docs `accounting.md` expects the caller to pass these — "both built-in models compute margin as a percentage of notional using the instrument's `margin_init` and `margin_maint` fields"), not an NT bug. **Any instrument on a MARGIN venue — equities, futures, perps — MUST set `margin_init`/`margin_maint`** (futures typically to the exchange's margin rate). Spot equities usually belong on a CASH venue, where margin fields are unused.
2. **`Portfolio.equity()` returns `dict[Currency, Money]`**, not a scalar. Extract by currency: `equity[ccy]`.
3. **`equity` / `mark_values` skip positions they cannot price** (no quote/trade/bar available). If equity understates, call `missing_price_instruments(venue)` first — docs `portfolio.md` flags this as the most common silent gap.
4. **`balances_total` ≠ `balance_available`.** Native equity uses `balances_total`. `balance_available = total − locked` (pending-order reservation). For CASH with no pending orders `locked=0` so they coincide; they diverge whenever pending orders exist. Use `balances_total` for equity.
5. **"Cash cannot short" is two separate restrictions**, both in `backtest/engine.pyx`: (a) Cash accounts cannot add futures/perpetuals instruments; (b) an uncovered Equity SELL (no opposing long to reduce) is rejected at `process_order` — but a reduce-only SELL (closing an existing long) is allowed. Neither is just an `account_type` label; both are matching-engine gates. (Live routes through the broker, which may not enforce these.)

## Custom MarginModel — subclassing & wiring

**Yes, you can subclass `MarginModel` from pure Python and the override fires at runtime.** `MarginModel` is a Cython `cdef class` (`accounting/margin_models.pyx`), but its calculation methods are declared **`cpdef`**, not `cdef` — and `cpdef` methods are explicitly designed to be overridable from Python (a plain `cdef` method could not be). So the `class RiskAdjustedMarginModel(MarginModel)` example in `accounting.md` is valid, not aspirational.

**What to override** (base signatures, `accounting/margin_models.pyx`):
- `calculate_margin_init(self, instrument, quantity, price, leverage, use_quote_for_inverse=False) -> Money` — initial / order margin.
- `calculate_margin_maint(self, instrument, side, quantity, price, leverage, use_quote_for_inverse=False) -> Money` — maintenance / position margin. **`side` (`PositionSide`) is passed in but the built-ins ignore it** — this is your hook for side-specific rates (Reg T long 25% / short 30%; Taiwan 融資 40% / 融券 130%).

**Two ways to wire a custom model:**
1. **Programmatic** — build it yourself, set it on the account:
   `account.set_margin_model(MyRegTMarginModel(...))` (`MarginAccount.set_margin_model`, `accounting/accounts/margin.pyx`).
2. **Config / factory** — `MarginModelConfig(model_type="yourpkg.module:RegTMarginModel", config={...})`. `MarginModelFactory.create()` (`nautilus_trader/backtest/config.py`) calls `resolve_path(model_type)` then `model_cls(config)` — so your `__init__(self, config: MarginModelConfig)` receives the config and reads params from `config.config` (a dict). Built-in `model_type` values are `"standard"` and `"leveraged"`.

**⚠️ Limitation a custom model CANNOT fix alone:** maintenance margin is computed with the **entry price** (`position.avg_px_open`), not current market value — `AccountsManager.update_positions` (`accounting/manager.pyx`) is what decides which `price` to pass into `calculate_margin_maint`. Real Reg T margin calls fire on current mark-to-market; to simulate that you must also override the manager, not just the model.

**When you actually need a custom model:** (a) side-specific maintenance (one instrument has one `margin_maint` field — can't natively encode long≠short); (b) asymmetric financing (Taiwan 融資/融券 are economically different products, not symmetric leverage). For plain symmetric percentage-of-notional (e.g. Reg T initial 50% both sides), `StandardMarginModel` with per-instrument `margin_init`/`margin_maint` set suffices — no subclass needed. Prefer `standard` over the default `leveraged` for stock venues (Reg T does not divide margin by leverage).

## Cross-mode behavior — backtest ≡ sandbox (NT design)

Paper/backtest/replay share the **same** matching + accounting engine: NT's `SandboxExecutionClient` (`nautilus_trader/adapters/sandbox/execution.py`) directly reuses backtest's `SimulatedExchange` + `BacktestExecClient` + `FillModel`/`FeeModel` (`from nautilus_trader.backtest.engine import SimulatedExchange`; `from nautilus_trader.backtest.execution_client import BacktestExecClient`), swapping only the clock (`LiveClock` vs `TestClock`) and message queue (real-time vs batched). So backtest Cash/Margin/margin-accounting behavior **extrapolates to paper/replay** — it is the same code path, not an assumption. **Live is the exception**: it routes through the broker adapter, so balance is broker-authoritative and does not pass through `SimulatedExchange` (see below).

## Live vs paper balance source

In **paper/backtest/replay**, NT computes balances from fills via the paths above. In **live**, the account balance is **fed from the broker** (the adapter translates venue responses into `AccountBalance`), not recomputed by `calculate_pnls`. So whether native `portfolio.equity(venue)` is correct for live depends on the adapter feeding a balance that already reflects position cost — verify the adapter's balance semantics; don't assume NT recomputes it.

## Worked example — floating-equity correctness (CASH)

**Bottom line:** after switching a stock venue to CASH, native `portfolio.equity(venue)` (`= balances_total + Σ mark_value`) is already correct — `cash.pyx::calculate_pnls` deducts notional on BUY, so `balances_total` reflects spent cash. Any `balance_available + total_market_value` workaround can retire (and was understating by `locked` under pending orders). For the full docs→source verification walkthrough (exact tool sequence), see [reference.md Example 4](reference.md).
