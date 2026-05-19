---
name: qa-generate-automation
description: Generate Maestro YAML automation scripts from existing test case CSVs. Writes scripts to /test-automation/maestro/ in the downstream project.
user-invocable: true
allowed-tools: Bash, Read, Glob, AskUserQuestion, Agent
---

## Arguments

`$ARGUMENTS` — optional path to a test case CSV or feature identifier.

## Steps

### 0 — Check for existing automation scripts

```bash
find "$(git rev-parse --show-toplevel)/test-automation/maestro" -name "*.yaml" 2>/dev/null
```

If files exist, call `AskUserQuestion`:

```
question    : "Existing Maestro scripts found. What would you like to do?"
header      : "Action"
multiSelect : false
options     :
  - label: "Regenerate all scripts",    description: "Overwrite existing scripts from the CSV"
  - label: "Generate for new CSV only", description: "Add scripts for a new test case file"
```

### 1 — Locate test case CSV

If `$ARGUMENTS` points to a `.csv` file, use it directly.

Otherwise, list available CSVs:

```bash
find "$(git rev-parse --show-toplevel)/test-cases" -name "*_test_cases.csv" 2>/dev/null
```

If multiple found, call `AskUserQuestion`:

```
question    : "Which test case file should be used as input?"
header      : "Input CSV"
multiSelect : false
options     : (one entry per found CSV, label = filename)
```

If none found, inform the user to run `/qa-generate-testcase` first and stop.

### 2 — Confirm scope

Call `AskUserQuestion`:

```
question    : "Which test cases should be automated?"
header      : "Scope"
multiSelect : false
options     :
  - label: "Smoke tests only",  description: "Generate scripts for Smoke category test cases"
  - label: "All test cases",    description: "Generate scripts for every test case in the CSV"
```

### 3 — Spawn automation worker

Spawn `qa-automation-worker` with the CSV file path (do not inline file contents):

> **csv_path:** <absolute path to selected CSV>
>
> **scope:** <smoke-only | all>
>
> Generate Maestro YAML scripts. Write output to `/test-automation/maestro/`. One file per feature area named `{feature_area}.yaml`.
