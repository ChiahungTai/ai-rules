---
name: api-and-interface-design
description: Guides stable API and interface design. Use when designing APIs, module boundaries, or any public interface. Use when creating REST or GraphQL endpoints, defining type contracts between modules, or establishing boundaries between frontend and backend.
---

# API and Interface Design

Design stable, well-documented interfaces that are hard to misuse. Good interfaces make the right thing easy and the wrong thing hard.

## Core Principles

### Hyrum's Law

> With a sufficient number of users of an API, all observable behaviors of your system will be depended on by somebody.

Every public behavior — including undocumented quirks, error message text, timing, and ordering — becomes a de facto contract. Be intentional about what you expose. Don't leak implementation details.

### Validate at Boundaries

Trust internal code. Validate at system edges: API route handlers, form submissions, external service responses, environment variable loading.

**Where NOT to validate**: between internal functions that share type contracts, in utilities called by already-validated code, on data from your own database. Over-validating internally adds noise and hides the real boundary.

**Third-party API responses are untrusted data.** Always validate their shape before using them in logic or decisions.

### 邊界 = Clean Architecture Adapter 邊界

「Validate at Boundaries」的 boundary，在 Clean Architecture 是 **adapter 邊界** — 介面（port）定義在內層（use case），實作在外層（adapter）。依賴向內：use case 定義 port，adapter 實作，infra 是外部細節。

- 驗證點 = adapter 邊界（系統邊緣：API、SDK、DB、跨進程）
- 內層（domain / use case）之間信任型別合約，不重複驗證
- 設計介面時，介面屬於內層（use case 定義 needs），實作屬於外層（adapter 提供）

**與 [architecture-thinking](../architecture-thinking/SKILL.md) 分工（RC-2 邊界）**：本 skill 設計**介面合約**（Hyrum's Law、Validate at Boundaries、穩定性）；architecture-thinking 檢視**整體結構**（分層依賴、bounded context）。介面是 adapter 邊界的具體化 — 設計介面用本 skill，看整體分層用 thinking。

### Prefer Addition Over Modification

Extend interfaces without breaking existing consumers. Add optional fields; don't change existing field types or remove fields. See [deprecation-and-migration](../deprecation-and-migration/SKILL.md) for safe removal.

### Consistent Error Semantics

Pick one error strategy and use it everywhere. Don't mix throwing, returning null, and returning `{ error }` — consumers can't predict behavior.

### Predictable Naming

- REST endpoints: plural nouns, no verbs (`GET /api/tasks`, not `GET /api/getTasks`)
- Boolean fields: `is`/`has`/`can` prefix
- Input/output separation: input types exclude server-generated fields

## Verification

- [ ] Every endpoint has typed input and output schemas
- [ ] Error responses follow a single consistent format
- [ ] Validation happens at system boundaries only
- [ ] New fields are additive and optional
- [ ] List endpoints support pagination
