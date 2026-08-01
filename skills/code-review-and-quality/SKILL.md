---
name: code-review-and-quality
description: 合併前多軸 code review。code 變更合併前審查品質（六軸：Correctness/Readability/Architecture/Security/Performance/Capability Coverage）。code review 的 profile 定義源（what to check）。通用審查邏輯（嚴重度/信心水準/審查者自證/LSP 查證/Writer-Reviewer 分離/多層驗證）見 review-engine。
---

# Code Review and Quality — code 六軸審查

code review 的 **profile 定義源**：六軸（what to check）。通用審查邏輯（嚴重度分級、信心水準、審查者自證、LSP 查證方法、Writer-Reviewer 分離、多層驗證）的真相源在 [review-engine](../review-engine/SKILL.md) — 本檔聚焦 code 六軸，不重複通用邏輯。

Six-axis review with quality gates. Every change gets reviewed before merge — no exceptions.

**Approve when the change definitely improves overall code health**, even if it isn't perfect. Don't block because it isn't exactly how you would have written it.

## The Six-Axis Review

### 1. Correctness

> **lens vs checklist 邊界**：Correctness **lens**（base perspective，所有 review 共用的視角）定義在 [review-engine](../review-engine/SKILL.md) 點 4 ③；本段是 **checklist**（what to check 細節，profile 層）。

- Matches spec/task requirements?
- Edge cases handled (null, empty, boundary values)?
- Error paths handled (not just happy path)?
- **Loud→silent regression**（diff 改 error handling 時必查）：diff 含 `raise`→`return None`、新增/拓寬 `try/except`、crash→filter、validation 緩步化時，flag 為**潛在 silent-corruption 引入**。「error paths handled」檢查的是**有無**錯誤路徑；本項檢查的是 diff 是否**把原本大聲的錯誤靜默化**——loud→silent 危險（會炸卻靜默腐敗下游），silent→loud 安全（虛驚、測試推翻）。不限交易 critical path，任何 error-path 改動都套用。見 [acceptance-evidence](../../rules/acceptance-evidence.md)「silent vs loud 不對稱風險」。
- Tests cover the change and actually test the right things?
- Off-by-one errors, race conditions, state inconsistencies?
  - 多 writer / state mutation invariant 破壞的判定（ownership vs write-site 粒度）見 [arch-thinking](../arch-thinking/SKILL.md)「變更路徑計數（mutation-path counting）」step —— 條件必填（觸及 mutable state 時）

### 2. Readability & Simplicity
- Names descriptive and consistent with project conventions?
- Control flow straightforward?
- Could this be done in fewer lines? (1000 lines where 100 suffice is a failure)
- Are abstractions earning their complexity? (Don't generalize until the third use case)
- Dead code artifacts: no-op variables, backwards-compat shims, `// removed` comments?

### 3. Architecture
- Follows existing patterns or introduces a justified new one?
- Clean module boundaries, dependencies flowing in right direction?
- Appropriate abstraction level (not over-engineered, not too coupled)?

### 4. Security

For detailed guidance, read [security-and-hardening](../security-and-hardening/SKILL.md) when security concerns are found.

- User input validated and sanitized?
- Secrets kept out of code, logs, and version control?
- SQL queries parameterized, outputs encoded for XSS?
- External data (APIs, logs, user content, config files) treated as untrusted?

### 5. Performance

For detailed profiling, read [performance-optimization](../performance-optimization/SKILL.md) when performance concerns are found.

- N+1 query patterns? Unbounded loops or data fetching?
- Missing pagination on list endpoints?
- Large objects created in hot paths?

### 6. Capability Coverage

For projects using UC-Driven Development, verify implementation against module instruction files' Capabilities tables (AGENTS.md preferred, CLAUDE.md legacy).

- Does implementation cover all Capabilities-defined behaviors?
- Are Capabilities-referenced behaviors present in the diff?
- Capabilities entry points point to library modules (not scripts/ — scripts/ is demo entry, not capability)?
- Skip for small changes (bug fix, docs)

## Review Process

### Step 1: Understand Context
- What is this change trying to accomplish?
- What spec or task does it implement?

### Step 2: Review Tests First
Tests reveal intent and coverage:
- Do they test behavior (not implementation details)?
- Edge cases covered?
- Would they catch a regression?

### Step 3: Review Implementation
Walk through code with the six axes.

### Step 4: Categorize Findings

嚴重度分級（3 級：Critical / Important / Suggestion）+ 信心水準標註見 [review-engine](../review-engine/SKILL.md) 嚴重度框架與信心水準段。Nit/FYI 已併入 Suggestion（統一 3 級，理由見 review-engine）。

### Step 5: Verify Verification
- What tests were run? Did the build pass?
- Manual testing done? Screenshots for UI changes?

## Dead Code Hygiene

After refactoring, check for orphaned code. **Deletion is a no-impact self-claim** ("zero callers") — treat it as Claim→Evidence→Trust: independently verify across the **full consumer surface** before removing; don't trust the author/commit self-claim (see [acceptance-evidence](../../rules/acceptance-evidence.md) Claim→Evidence→Trust「刪除/死碼自述同理」). This is the routine-review counterpart of what `/human-review` 判準 1 does on demand — the gap it fills is that post-build `/code-review` previously trusted the self-claim.

**Full consumer surface for "zero callers"** (LSP findReferences alone is insufficient — it misses dynamic dispatch and non-library consumers):
- LSP `findReferences` (static imports)
- rg the symbol name across .py/.yaml/.json — including `scripts/`, `lab/`, demo, `poc/`, saved configs (not just the module's own tree)
- dynamic dispatch: getattr/importlib, registry auto-discovery, StrEnum string-values-in-config
- for whole-file / whole-class deletion: actually execute an import of the affected consumers (`uv run python -c "import <consumer>"`) — static zero-hit ≠ runtime zero-consumer

```
DEAD CODE IDENTIFIED:
- formatLegacyDate() — replaced by formatDate()
- OldTaskCard component — replaced by TaskCard
→ Verified zero callers across full surface? (LSP + rg scripts/lab/configs + import test)
```

## Architecture Doc Drift Reminder

> 補 axis 6（只看「改到目錄的 Capabilities 表」）的盲區：**跨模組結構變更 → 架構文檔可能需更新**。code-review 是 read-only，只 **flag 提醒**（finding 指向 owner tool），不做 sync、不重複 [doc-health](../../commands/doc-health.md) 的 accuracy check（doc-health 問「文件準確嗎」；本項問「這結構變更該不該觸發文檔更新提醒」——正交）。

**觸發（structural signal — 非 file-count；1-file 高 ripple 也觸發，file-count gate 會漏此類改動）**：
- 新增 / 移除 / 改名 module（目錄）或 top-level package
- 新增 / 移除跨模組 import edge（尤其新依賴方向：反向耦合、新循環）
- 觸及已知 hub / ripple component（讀專案的跨模組依賴文檔——如 root AGENTS.md 的熱點表、`dependency-graph.md` 的 ripple rules（若存在）——比對 diff 是否碰 listed component）
- 新抽象層 / 新公開 Protocol / 新跨模組 base class
- fallback：≥3 files 跨多模組

**提醒對象 + owner（finding 指向，不自己做 sync）**：

| 架構文檔 | owner | 何時該更新 |
|---|---|---|
| `dependency-graph.md` | `/scan-project`（重生成）/ `/daily-maintain` | 新/移/改名 module、import edge 變、hub component 改 — **無 build-time owner，最易 silent drift** |
| 模組 AGENTS.md 架構段 / `architecture.md` | build 5b（未跑 /build 則手動） | 設計決策 / 新抽象 / 模組結構 / 依賴方向 變更 |
| `SYSTEM-MAP.md`（lifecycle） | metadata-sync / build 5a | 功能生命週期變化（新功能完成、狀態升級） |

**嚴重度**：Suggestion（mild signal）→ Important（強信號：新/移除 module 必更 `dependency-graph.md`）。

**不適用**：docs mode（純文檔審查本身就是改文檔；本提醒是「code 變更 → 架構文檔忘了跟」）。

## 通用審查邏輯（見 review-engine）

以下通用邏輯已移至 [review-engine](../review-engine/SKILL.md)，本檔不重複（避免跨命令 drift）：

- **嚴重度分級 + 信心水準**（原 5 級含 Nit/FYI → 統一 3 級 Critical/Important/Suggestion + confirmed/evidence-based/inferred；Critical 禁止 inferred）
- **審查者自證 / 誠信**（原 Reviewer Self-Verification + Honesty in Review — 每 claim 必須查證、findings 非定論、對外部行為判斷必須實證、不 rubber-stamp）
- **LSP 查證方法 + 自我否證義務**（原 LSP-Assisted Review — 符號用 LSP、文字用 rg、找不到 ≠ 不存在）
- **Writer-Reviewer 分離 + 多層驗證**（原 Multi-Model Review Pattern — 獨立 context 審查避免自審、review→judge→followup 各層都可能錯）

See also: [review-engine](../review-engine/SKILL.md)（通用審查邏輯真相源）, [security-and-hardening](../security-and-hardening/SKILL.md), [performance-optimization](../performance-optimization/SKILL.md)
