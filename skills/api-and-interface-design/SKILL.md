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
