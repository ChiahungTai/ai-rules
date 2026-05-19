---
name: ci-cd-and-automation
description: Automates CI/CD pipeline setup. Use when setting up or modifying build and deployment pipelines. Use when you need to automate quality gates, configure test runners in CI, or establish deployment strategies.
---

# CI/CD and Automation

## Core Principles

**Shift Left**: Catch problems as early as possible. Static analysis before tests, tests before staging, staging before production.

**Faster is Safer**: Smaller batches and more frequent releases reduce risk. A deployment with 3 changes is easier to debug than one with 30.

**No gate can be skipped**: If lint fails, fix lint. If a test fails, fix the code. Never disable rules or skip tests to make the pipeline pass.

## Feeding CI Failures Back to Agents

The highest-leverage CI pattern with AI agents:

1. CI fails → copy the failure output
2. Feed to agent: `"The CI pipeline failed with this error: [paste error]. Fix the issue and verify locally before pushing again."`
3. Agent fixes → pushes → CI runs again

```
Lint failure → Agent runs linter --fix and commits
Type error  → Agent reads error location and fixes the type
Test failure → Agent follows debugging-and-error-recovery skill
```

## Environment Management

```
.env.example       → Committed (template)
.env                → NOT committed (local dev)
CI secrets          → GitHub Secrets / vault
Production secrets  → Deployment platform / vault
```

CI should never have production secrets.

## Quality Gate Pipeline

Every change: lint → type check → unit tests → build → integration tests → security audit. All must pass before merge.

## Verification

- [ ] All quality gates present and passing
- [ ] Failures block merge (branch protection)
- [ ] Secrets in secrets manager, not in code
- [ ] Pipeline runs under 10 minutes
