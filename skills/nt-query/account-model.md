# nt-query — Account, Balance & Equity Model

Loaded on demand for questions about account types, balances, equity, margin, or PnL computation. `<NT_REPO>` is resolved in SKILL.md. This file gives the **non-derivable design model** (how `account_type` fans out across layers), the **two lifecycle paths** that most often get conflated, the **margin-model side capabilities** (init vs maint), navigation seeds, and the failure modes that trap investigators. Authoritative concept docs: `<NT_REPO>/docs/concepts/accounting.md` and `portfolio.md` — read them first.

> **Margin query checklist** (if you're chasing a balance/equity/margin bug): (1) which `account_type`? it selects the 4 layers below; (2) margin has **two lifecycle paths** — pending (`orders_open`) vs filled — verify the one your scenario hits, not just one; (3) Cash/Margin `calculate_pnls` **branch by account_type** — don't read one and assume the other; (4) is the instrument's `margin_maint` actually set? default `0` is the #1 trap (gotcha #1); (5) sim vs live — who produced `balances_total` decides the right equity call (see "Equity is mode-aware").

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

### `account_type` is forced by what you trade, not a free choice

CASH can only hold **現股 (cash long)** — it blocks short sells and futures/perpetuals. Anything that shorts or uses leverage (融資 / 融券 / 期貨) **forces `MARGIN`**. A real stock account usually mixes 現股 + 融資 + 融券 in **one account**, so the account is `MARGIN`; pure-cash 現股 then lives *inside* that MARGIN account — and **needs `margin_maint` set to a non-zero value** (e.g. `Decimal("1.0")` locks the full cost, behaving cash-like). Left at the default `0` it inflates (gotcha #1). "Switch 現股 to CASH" is only possible for an account that does no short/margin at all.

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
| Initial vs maintenance margin | `calculate_margin_init` (no side) / `calculate_margin_maint` (has side) | margin model + `accounting/manager.pyx` |
| Account-wide margin (整戶 / cross-margin) | `MarginBalance` (`instrument_id=None`) | `accounting/` (+ docs `accounting.md` "Margin scopes") |
| Broker-authoritative account feeding (live) | `generate_account_state(..., reported=True)`, adapter `_on_account_summary` | `adapters/interactive_brokers/execution.py` (+ see IB reference below) |

## Gotchas (non-derivable failure modes)

1. **`margin_init` / `margin_maint` default to `Decimal(0)`** when not passed (`nautilus_trader/model/instruments/equity.pyx`, likewise `futures_contract.pyx` / `crypto_future.pyx`). On a MARGIN venue, maintenance margin = `notional × margin_maint` = `notional × 0` = 0 → **nothing locked → equity inflates by the position's notional**. This is **by design** (docs `accounting.md` expects the caller to pass these — "both built-in models compute margin as a percentage of notional using the instrument's `margin_init` and `margin_maint` fields"), not an NT bug. **Any instrument on a MARGIN venue — equities, futures, perps — MUST set `margin_init`/`margin_maint`** (futures typically to the exchange's margin rate). Spot equities usually belong on a CASH venue, where margin fields are unused.
2. **`Portfolio.equity()` returns `dict[Currency, Money]`**, not a scalar. Extract by currency: `equity[ccy]`.
3. **`equity` / `mark_values` skip positions they cannot price** (no quote/trade/bar available). If equity understates, call `missing_price_instruments(venue)` first — docs `portfolio.md` flags this as the most common silent gap.
4. **`balances_total` ≠ `balance_available`.** Native equity uses `balances_total`. `balance_available = total − locked` (pending-order reservation). For CASH with no pending orders `locked=0` so they coincide; they diverge whenever pending orders exist. Use `balances_total` for equity.
5. **"Cash cannot short" is two separate restrictions**, both in `backtest/engine.pyx`: (a) Cash accounts cannot add futures/perpetuals instruments; (b) an uncovered Equity SELL (no opposing long to reduce) is rejected at `process_order` — but a reduce-only SELL (closing an existing long) is allowed. Neither is just an `account_type` label; both are matching-engine gates. (Live routes through the broker, which may not enforce these.)

## Custom MarginModel — what subclassing can and cannot do

You **can** subclass `MarginModel` from pure Python and the override fires at runtime. `MarginModel` is a Cython `cdef class` (`accounting/margin_models.pyx`), but its calculation methods are declared **`cpdef`** — explicitly overridable from Python (a plain `cdef` method could not be). So the `class RiskAdjustedMarginModel(MarginModel)` example in `accounting.md` is valid.

**But the two methods have asymmetric power — read the signatures carefully:**

- **`calculate_margin_init(self, instrument, quantity, price, leverage, use_quote_for_inverse=False) -> Money`** — initial / order margin. **⚠️ There is NO `side` parameter.** `_update_margin_init` (`accounting/manager.pyx`) calls it per pending order *without* the order's side. So **initial margin is one rate per instrument — identical for a BUY (融資) and a SELL (融券 open)**. A subclass **cannot** make initial margin side-specific (the side isn't in the signature to receive). Differentiating 融資-init from 融券-init requires overriding `_update_margin_init` itself (heavy, fights NT) or using separate instrument ids (hacky).
- **`calculate_margin_maint(self, instrument, side, quantity, price, leverage, use_quote_for_inverse=False) -> Money`** — maintenance / position margin. **`side` (`PositionSide`) IS passed**, but the built-ins ignore it (`margin = notional × instrument.margin_maint`). This is your hook for **side-specific maintenance** (Reg T long 25% / short 30%; 融資 vs 融券). Still cannot distinguish two positions of the *same* side (e.g. 現股 vs 融資 are both `LONG`).

| Want to differentiate | `calculate_margin_init` | `calculate_margin_maint` (custom) | Verdict |
|---|---|---|---|
| 融資 (LONG) vs 融券 (SHORT) | ❌ no side | ✅ via `side` | **only maintenance, not initial** |
| 現股 vs 融資 (both LONG) | ❌ | ❌ (same side) | **not at all — needs app-level layer (e.g. position-id cond)** |

**Two ways to wire a custom model:**
1. **Programmatic** — `account.set_margin_model(MyModel(...))` (`MarginAccount.set_margin_model`, `accounting/accounts/margin.pyx`).
2. **Config / factory** — `MarginModelConfig(model_type="yourpkg.module:RegTMarginModel", config={...})`. `MarginModelFactory.create()` (`nautilus_trader/backtest/config.py`) calls `resolve_path(model_type)` then `model_cls(config)` — your `__init__(self, config: MarginModelConfig)` reads params from `config.config`. Built-in `model_type` values: `"standard"`, `"leveraged"`.

**⚠️ Limitation a custom model CANNOT fix alone:** maintenance margin is computed with the **entry price** (`position.avg_px_open`), not current market value — `AccountsManager.update_positions` (`accounting/manager.pyx`) decides which `price` to pass into `calculate_margin_maint`. Real Reg T margin calls fire on current mark-to-market; simulating that requires overriding the manager, not just the model.

**When you actually need a custom model:** side-specific *maintenance* (one instrument has one `margin_maint` field). For plain symmetric percentage-of-notional (e.g. Reg T initial 50% both sides), `StandardMarginModel` with per-instrument `margin_init`/`margin_maint` set suffices — no subclass. Prefer `standard` over the default `leveraged` for stock venues: `leveraged` **divides margin by leverage** (the crypto/perp exchange model where higher leverage lowers the margin requirement), which is wrong for stocks — Reg T is a fixed percentage regardless of leverage, so use `standard`.

## Cross-mode behavior — backtest ≡ sandbox (NT design)

Paper/backtest/replay share the **same** matching + accounting engine: NT's `SandboxExecutionClient` (`nautilus_trader/adapters/sandbox/execution.py`) directly reuses backtest's `SimulatedExchange` + `BacktestExecClient` + `FillModel`/`FeeModel` (`from nautilus_trader.backtest.engine import SimulatedExchange`; `from nautilus_trader.backtest.execution_client import BacktestExecClient`), swapping only the clock (`LiveClock` vs `TestClock`) and message queue (real-time vs batched). So backtest Cash/Margin/margin-accounting behavior **extrapolates to paper/replay** — it is the same code path, not an assumption. **Live is the exception**: it routes through the broker adapter, so balance is broker-authoritative and does not pass through `SimulatedExchange`.

## Equity is mode-aware — don't use one formula for sim + live

The right equity call depends on **who produced `balances_total`**:

- **paper/backtest/replay (NT-computed):** `balances_total` is the cash balance NT tracks from fills — it **excludes** open positions. Use `portfolio.equity(venue)` (= `balances_total + Σ unrealized_pnl` for MARGIN, `+ Σ mark_value` for CASH); it adds the position term correctly.
- **live (broker-authoritative):** the broker's `balances_total` is a **net liquidation value that already includes positions** (IB sets `total = NetLiquidation`; a Shioaji adapter should do the equivalent). So `portfolio.equity` — which adds `unrealized_pnl`/`mark_value` on top — **double-counts**. Use `account.balances_total()[ccy]` directly for live equity.

**Implication:** a single equity formula cannot span sim + live, because `balances_total` means different things (cash-only vs net). Branch by mode. A `balance_available + Σ mv` style workaround that tries to span both will be wrong on one side.

## IB reference — how a broker-authoritative account is fed

`adapters/interactive_brokers/` is NT's most complete pure-Python broker adapter and the template for any live broker adapter (e.g. Shioaji). Its account handling is the canonical "broker-authoritative" pattern:

- **`account_type = AccountType.MARGIN` hardcoded** (`InteractiveBrokersExecutionClient.__init__`, `execution.py`) — not configurable; a real margin broker is always MARGIN.
- **Never uses a `MarginModel`; instruments carry `margin_init`/`margin_maint = Decimal(0)`** (`parsing/instruments.py`) — the broker computes margin, NT does not.
- **`trading_mode: "paper" | "live"`** (`config.py`) selects only the IB Gateway port (`gateway.py`: paper 4002 / live 4001) — **account handling is identical in both** (broker-authoritative). Note: IB's *paper* is a broker-side paper server, NOT NT's internal `SandboxExecutionClient` sim — different quadrant.
- **Subscribes the broker account summary** (`client/account.py` `subscribe_account_summary` → `reqAccountSummary`); `_on_account_summary` (`execution.py`) builds the NT state from **5 broker tags** (all account-wide / 整戶): `NetLiquidation`→`AccountBalance.total` (**net equity — already includes positions**, so don't add them again), `FullAvailableFunds`→`free` (`locked` is derived as `total − free`, not a separate tag), `FullInitMarginReq`→`MarginBalance.initial` and `FullMaintMarginReq`→`MarginBalance.maintenance` (both `instrument_id=None`), `TotalCashValue`→`info` (not a balance field). Emitted via `generate_account_state(..., reported=True)` — `reported=True` flags it broker-authoritative (NT will not recompute).

A real broker adapter is a **thin shell**: connection + instrument loading + translating broker messages into NT `AccountState`/`Position`/`Order` events. Margin/equity are the broker's numbers; NT just stores them. So for a live broker, "which MarginModel" and "which equity formula" are moot — mirror IB: hardcode MARGIN, feed the broker's `NetLiquidation`/margin, set `reported=True`, and read equity from `balances_total`.

## Worked example — floating-equity correctness (CASH)

**Bottom line:** for a pure-CASH account (one that does no short/margin), native `portfolio.equity(venue)` (`= balances_total + Σ mark_value`) is correct — `cash.pyx::calculate_pnls` deducts notional on BUY, so `balances_total` reflects spent cash. Any `balance_available + total_market_value` workaround can retire (and was understating by `locked` under pending orders). For the full docs→source verification walkthrough (exact tool sequence), see [reference.md Example 4](reference.md). *(If the account also does 融資/融券 it must be MARGIN, not CASH — see "account_type is forced" above; then use the MARGIN equity term `Σ unrealized_pnl`.)*
