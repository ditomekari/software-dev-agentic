---
name: audit
description: Audit structural integrity and convention compliance of a persona, agent, or skill. Runs agent-audit-worker and arch-review-worker in parallel, then compiles results.
user-invocable: true
tools: Agent, AskUserQuestion
---

## Arguments

```
/audit [scope]
```

- `scope` — optional. A persona name (`builder`, `detective`), a file path, or `full`. If omitted, ask the user.

## Steps

### 1 — Resolve scope

If `scope` was not provided, ask:

> "What scope to audit? Options: a persona name (`builder`, `detective`, `tracker`, `auditor`, `installer`), a specific file path, or `full`."

### 2 — Run in parallel

Spawn both workers simultaneously — do not wait for one before starting the other:

- `agent-audit-worker` with: `Scope: <scope>. Check structural integrity only.`
- `arch-review-worker` with: `Scope: <scope>. Check convention compliance only.`

### 3 — Validate

Before compiling:
- Does each response contain findings or an explicit PASS? — STOP and report if either returned no output.

### 4 — Report

```
## Structural + Convention Audit — <scope>

### Structural Integrity (agent-audit-worker)
<findings>

### Convention Compliance (arch-review-worker)
<findings>

### Routing
[BROKEN reference] → /scaffold to create the missing component
[CRITICAL/WARNING violation] → /migrate to fix the violation
```
