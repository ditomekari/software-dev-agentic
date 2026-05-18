---
name: sync-platform
description: Sync one or more existing platform reference impl files and contract skills against a real downstream codebase — diffs sections, gets user approval, then regenerates.
user-invocable: true
tools: Agent, Bash
---

## Arguments

No pre-filled arguments. Gather interactively in Step 1.

## Steps

### 1 — Gather Inputs

Ask the user (one question at a time):

1. "What is the absolute path to the downstream repo? (required)"
2. "Which platform(s) do you want to sync? Single name or comma-separated list, e.g. `flutter` or `ios,android` (required)"

Store as: `repo_path`, `platforms` (split on comma, trim whitespace)

### 2 — Validate repo_path

Run:

```bash
[ -d "$repo_path" ] && echo "EXISTS" || echo "MISSING"
```

If result is `MISSING`: report "repo_path not found on disk: <repo_path>" and STOP.

### 3 — Sync Each Platform

For each platform in `platforms`:

#### 3a — Spawn Worker

Spawn `agent-generate-platform-worker` with:

```
mode: sync
repo_path: <repo_path>
platform: <platform>
```

Wait for completion. Validate that the response contains an `## Output` section — STOP with "Worker returned no Output section for platform `<platform>`. Check agent-generate-platform-worker for errors." if missing.

#### 3b — Update Reference Counts

Run:

```bash
bash software-dev-agentic/scripts/update-ref-counts.sh lib/platforms/<platform>/reference/
```

### 4 — Check Skill Contracts (All Platforms)

After all platforms complete, run:

```bash
bash software-dev-agentic/scripts/check-skill-contracts.sh
```

### 5 — Report Summary

Present to the user:

```
Sync complete.

Platforms synced: <comma-separated list>

For each platform:
  Reference files updated: <count> (<list from worker ## Output>)
  Contract skills regenerated: <count> (<list from worker ## Output>)
  MISSING_PATTERN warnings: <list, or "none">

Contract check: <pass / violations listed>
```
