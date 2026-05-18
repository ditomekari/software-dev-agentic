---
name: migrate
description: Migrate an existing agent or skill file to comply with software-dev-agentic conventions. Runs agent-migrate-worker then verifies the fix with arch-review-worker.
user-invocable: true
tools: Agent
---

## Arguments

```
/migrate [file]
```

- `file` — optional. Path to the agent or skill file to migrate. If omitted, the worker will ask.

## Steps

### 1 — Migrate

Spawn `agent-migrate-worker`.

If `file` was provided, pass it in the spawn prompt: `File: <file>`
If omitted, pass no arguments — the worker will ask interactively.

Validate: response must contain a migration report — STOP if no output.

### 2 — Verify

Extract the migrated file path from the report.

Spawn `arch-review-worker` with: `Scope: <migrated file path>. Check convention compliance.`

- Clean → confirm fix succeeded
- Violations remain → list as residual — user decides next step

### 3 — Report

Migration report + verification result. If residual violations: list them and suggest `/migrate` again.
