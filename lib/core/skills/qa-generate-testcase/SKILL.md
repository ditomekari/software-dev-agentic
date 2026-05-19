---
name: qa-generate-testcase
description: Generate or regenerate mobile UI test cases from a Jira ticket, PRD, Figma design, or feature description. Outputs .csv to /test-cases/ and posts a Jira comment.
user-invocable: true
allowed-tools: Bash, Read, AskUserQuestion, Agent
---

## Arguments

`$ARGUMENTS` — optional Jira URL, Figma link, or feature description.

## Steps

### 0 — Check for existing output

```bash
find "$(git rev-parse --show-toplevel)/test-cases" -name "*_test_cases.csv" 2>/dev/null
```

If files exist, call `AskUserQuestion`:

```
question    : "Existing test case files found. What would you like to do?"
header      : "Action"
multiSelect : false
options     :
  - label: "Regenerate from changes", description: "Update existing test cases based on new code or PR diff"
  - label: "Create new test cases",   description: "Generate fresh test cases for a new feature"
```

Skip this step if no files are found.

### 1 — Determine mode

Call `AskUserQuestion`:

```
question    : "What would you like to do?"
header      : "Mode"
multiSelect : false
options     :
  - label: "Create new test cases",    description: "Generate from Jira, PRD, Figma, or description"
  - label: "Regenerate test cases",    description: "Update existing CSV based on code changes or PR diff"
```

### 2 — Gather context

**Create mode:**

If `$ARGUMENTS` is empty, call `AskUserQuestion`:

```
question    : "What is the source for these test cases?"
header      : "Source"
multiSelect : false
options     :
  - label: "Jira ticket URL",       description: "Fetch requirements and acceptance criteria from Jira"
  - label: "Figma design URL",      description: "Generate from screen designs and component states"
  - label: "Free-text description", description: "Describe the feature inline"
```

**Regenerate mode:**

Call `AskUserQuestion`:

```
question    : "What is the basis for regeneration?"
header      : "Basis"
multiSelect : false
options     :
  - label: "Git branch diff",      description: "Compare current branch against main"
  - label: "Existing CSV",         description: "Point to an existing /test-cases/*.csv file"
  - label: "PR reference",         description: "Provide a PR URL or branch name"
```

### 3 — Spawn orchestrator

Spawn `qa-testcase-worker` with the pre-loaded context:

> **Mode: <create | regenerate>**
>
> Input: <$ARGUMENTS or collected source>
>
> Basis (regenerate only): <diff source / CSV path / PR ref>
>
> Execute the full workflow. Write CSV output to `/test-cases/`. Post Jira comment if a Jira ticket is available.
