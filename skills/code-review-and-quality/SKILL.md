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
- Tests cover the change and actually test the right things?
- Off-by-one errors, race conditions, state inconsistencies?

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

After refactoring, check for orphaned code. **Ask before deleting** — don't silently remove things you're not sure about.

```
DEAD CODE IDENTIFIED:
- formatLegacyDate() — replaced by formatDate()
- OldTaskCard component — replaced by TaskCard
→ Safe to remove these?
```

## 通用審查邏輯（見 review-engine）

以下通用邏輯已移至 [review-engine](../review-engine/SKILL.md)，本檔不重複（避免跨命令 drift）：

- **嚴重度分級 + 信心水準**（原 5 級含 Nit/FYI → 統一 3 級 Critical/Important/Suggestion + confirmed/evidence-based/inferred；Critical 禁止 inferred）
- **審查者自證 / 誠信**（原 Reviewer Self-Verification + Honesty in Review — 每 claim 必須查證、findings 非定論、對外部行為判斷必須實證、不 rubber-stamp）
- **LSP 查證方法 + 自我否證義務**（原 LSP-Assisted Review — 符號用 LSP、文字用 rg、找不到 ≠ 不存在）
- **Writer-Reviewer 分離 + 多層驗證**（原 Multi-Model Review Pattern — 獨立 context 審查避免自審、review→judge→followup 各層都可能錯）

See also: [review-engine](../review-engine/SKILL.md)（通用審查邏輯真相源）, [security-and-hardening](../security-and-hardening/SKILL.md), [performance-optimization](../performance-optimization/SKILL.md)
