---
name: scaffold
description: Design and scaffold a new agentic component — skill, worker, orchestrator, or persona. Runs agent-scaffold-worker then verifies the new file with arch-review-worker.
user-invocable: true
tools: Agent
---

## Steps

### 1 — Scaffold

Spawn `agent-scaffold-worker`. The worker gathers all intent interactively — pass no pre-filled arguments.

Validate: response must contain an `## Output` section with scaffolded file path(s) — STOP if missing.

### 2 — Verify

Spawn `arch-review-worker` with: `Scope: <each scaffolded file path>. Check convention compliance.`

- Clean → confirm component is convention-compliant
- Violations → list as residual with hint: run `/migrate` to fix

### 3 — Report

Scaffold report + convention check result.
