---
name: generate-platform
description: Onboard a brand-new platform into the toolkit — scans a downstream repo, generates platform reference impl files, and derives contract skills.
user-invocable: true
tools: Agent, Bash
---

## Arguments

No pre-filled arguments. Gather interactively in Step 1.

## Steps

### 1 — Gather Inputs

Ask the user (one question at a time):

1. "What is the absolute path to the downstream repo? (required)"
2. "What is the platform name? e.g. `flutter`, `ios`, `android`, `web` (required)"
3. "Are there any architecture doc paths inside that repo I should read for context? Comma-separated, or press enter to skip."

Store as: `repo_path`, `platform`, `arch_docs`

### 2 — Validate repo_path

Run:

```bash
[ -d "$repo_path" ] && echo "EXISTS" || echo "MISSING"
```

If result is `MISSING`: report "repo_path not found on disk: <repo_path>" and STOP.

### 3 — Check Platform Does Not Exist

Run:

```bash
[ -d "lib/platforms/$platform" ] && echo "EXISTS" || echo "MISSING"
```

If result is `EXISTS`: tell the user "Platform `<platform>` already exists. Run `sync-platform` instead." and STOP.

### 4 — Spawn Worker

Spawn `agent-generate-platform-worker` with:

```
mode: generate
repo_path: <repo_path>
platform: <platform>
arch_docs: <arch_docs>
```

Wait for completion. Validate that the response contains an `## Output` section — STOP with "Worker returned no Output section. Check agent-generate-platform-worker for errors." if missing.

### 5 — Update Reference Counts

Run:

```bash
bash software-dev-agentic/scripts/update-ref-counts.sh lib/platforms/<platform>/reference/
```

### 6 — Check Skill Contracts

Run:

```bash
bash software-dev-agentic/scripts/check-skill-contracts.sh --platform=<platform>
```

### 7 — Report

Present to the user:
- Platform onboarded: `<platform>`
- Reference files written (from worker `## Output`)
- Contract skills written (from worker `## Output`)
- Any `MISSING_PATTERN` warnings (from worker `## Output`)
- Result of `check-skill-contracts.sh`
