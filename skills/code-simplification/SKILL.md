---
name: code-simplification
description: Simplifies code for clarity. Use when refactoring code for clarity without changing behavior. Use when code works but is harder to read, maintain, or extend than it should be. Use when reviewing code that has accumulated unnecessary complexity.
---

# Code Simplification

Reduce complexity while preserving exact behavior. Goal: code that is easier to read, understand, modify, and debug. Not fewer lines — faster comprehension.

## Five Principles

1. **Preserve Behavior Exactly** — All inputs, outputs, side effects, error behavior, and edge cases must remain identical. If unsure, don't make the change.
2. **Follow Project Conventions** — Simplification that breaks project consistency is churn, not improvement.
3. **Prefer Clarity Over Cleverness** — Explicit code beats compact code when the compact version requires a mental pause.
4. **Maintain Balance** — Don't over-simplify: inlining aggressively, combining unrelated logic, or removing extensibility abstractions makes code worse.
5. **Scope to What Changed** — Default to simplifying recently modified code. Avoid drive-by refactors of unrelated code.

## Process

### 1. Chesterton's Fence

Before changing or removing anything, understand **why it exists**. Check git blame. If you can't explain why the code was written this way, you're not ready to simplify.

### 2. Identify Signals

**Structural**: Deep nesting (3+ levels), long functions (50+ lines), boolean flags as params, repeated conditionals.

**Naming**: Generic names (`data`, `result`, `temp`), abbreviated names, misleading names.

**Redundancy**: Duplicated logic, dead code, wrappers that add no value, over-engineered patterns (factory-for-a-factory).

### 3. Apply Incrementally

One simplification at a time. Run tests after each. Submit refactoring changes **separately** from feature or bug fix changes.

### 4. Verify

Is the simplified version genuinely easier to understand? If not, revert.

## Verification

- [ ] All existing tests pass without modification
- [ ] Each simplification is reviewable and incremental
- [ ] No error handling removed or weakened
- [ ] No dead code left behind
