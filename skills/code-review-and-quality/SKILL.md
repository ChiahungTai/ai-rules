---
name: code-review-and-quality
description: Conducts multi-axis code review. Use before merging any change. Use when reviewing code written by yourself, another agent, or a human. Use when you need to assess code quality across multiple dimensions before it enters the main branch.
---

# Code Review and Quality

Six-axis review with quality gates. Every change gets reviewed before merge — no exceptions.

**Approve when the change definitely improves overall code health**, even if it isn't perfect. Don't block because it isn't exactly how you would have written it.

## The Six-Axis Review

### 1. Correctness
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

### 6. UC Coverage

For projects using UC-Driven Development, verify implementation against USE-CASES.md.

- Does implementation cover all UC-defined behaviors?
- Are UC-referenced behaviors present in the diff?
- EP segment UC IDs match USE-CASES.md?
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

| Severity | Meaning | Author Action |
|----------|---------|---------------|
| **Critical** | Security vulnerability, data loss, broken functionality | Must address before merge |
| **Important** | Architecture inconsistency, readability issue, performance risk | Should address |
| **Suggestion** | Style, naming, minor optimization | Author may ignore |
| **Nit** | Formatting, style preferences | Author may ignore |
| **FYI** | Informational only | No action needed |

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

## Honesty in Review

- **Don't rubber-stamp.** "LGTM" without evidence helps no one.
- **Don't soften real issues.** "This might be minor" when it's a bug is dishonest.
- **Quantify problems.** "N+1 adds ~50ms per item" beats "this could be slow."
- **Push back on approaches with clear problems.** Sycophancy is a failure mode.
- **Don't accept deferred cleanup promises.** "I'll clean it up later" never happens.
- **Accept override gracefully.** If the author has full context and disagrees, defer.

## Reviewer Self-Verification

Every claim in a review must be verified against actual code. Unverified claims waste the author's time and erode trust in reviews.

- **Claiming a file/directory exists** → Read it first
- **Claiming a naming conflict** → Check the import chain (is it actually a Python package? does the import work?)
- **Claiming a dependency order problem** → Trace the execution order across segments/files
- **Claiming something is missing** → Verify it doesn't exist elsewhere or under a different name

If you cannot verify a claim with the tools available, label it explicitly as **unverified** rather than stating it as fact.

## Multi-Model Review Pattern

Different models have different blind spots. For important reviews, use separate sessions:

```
Model A writes → Model B reviews → Model A addresses → Human final call
```

See also: [security-and-hardening](../security-and-hardening/SKILL.md), [performance-optimization](../performance-optimization/SKILL.md)
