---
name: test-driven-development
description: Drives development with tests. Use when implementing any logic, fixing any bug, or changing any behavior. Use when you need to prove that code works, when a bug report arrives, or when you're about to modify existing functionality.
---

# Test-Driven Development

Write a failing test before writing the code that makes it pass. Tests are proof — "seems right" is not done.

---

## The Prove-It Pattern (Bug Fixes)

**Do not start by fixing the bug.** Start by writing a test that reproduces it.

1. Write a test that demonstrates the bug → test FAILS (bug confirmed)
2. Implement the fix → test PASSES (fix proven)
3. Run full suite → no regressions

This guarantees the bug can't resurface silently.

## Tests Verify Intent, Not Just Behavior

Every test must encode **why** the behavior matters. A test that can't fail when business logic changes is a broken test.

**Worthless**: both the function and the test hardcode the same value — proves nothing.
**Meaningful**: test constrains the output against a business rule — would fail if logic changes.

**Rule**: If you can't write a test that fails when the business logic changes, either the function is wrong or the test is wrong.

## Test What Matters

- **State over interactions**: Assert on outcomes, not on which methods were called. Interaction tests break on refactor.
- **Real implementations over mocks**: Real > Fake > Stub > Mock. Over-mocking creates tests that pass while production breaks.
- **One assertion per concept**: Each test verifies one behavior, named descriptively.

## Subagent Testing Pattern

For complex bug fixes, spawn a subagent to write the reproduction test. The main agent then verifies the test fails, implements the fix, and verifies it passes. This separation ensures the test is written without knowledge of the fix.

## Browser Testing

For anything that runs in a browser, combine unit tests with runtime verification via Chrome DevTools MCP — DOM inspection, console errors, network requests, screenshots. See [browser-testing-with-devtools](../browser-testing-with-devtools/SKILL.md).

## Verification

After completing any implementation:

- [ ] Every new behavior has a corresponding test
- [ ] Bug fixes include a reproduction test that failed before the fix
- [ ] No tests were skipped or disabled
