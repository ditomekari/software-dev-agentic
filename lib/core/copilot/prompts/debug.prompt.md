---
mode: agent
tools:
  - codebase
  - readFile
  - search
description: "Debug a reported bug — collects intake, searches for historical fixes via RAG, traces root cause across layers, and proposes a targeted fix."
---

Debug the issue described in `$ARGUMENTS`. If no description is provided, ask the user for:
1. Error message or stack trace
2. Expected vs actual behavior
3. Entry point — the screen, action, or method where the failure occurs

## Step 1 — Search Historical Fixes

If the `mobile-qontak` RAG MCP server is available:
- Call `search_similar_issues` with the error message and entry point as query
- If a high-confidence match is found, call `get_issue_fix` and present the historical fix to the user before proceeding
- Ask: "A similar past incident was found. Does this match your bug? [yes/no/partially]"
- If unavailable, continue silently

## Step 2 — Scope the Bug

From the stack trace or description, identify:
- The failing file(s) and approximate line numbers
- The BLoC event that triggered the failure (if applicable)
- The data layer call (repository / data source) involved

If the MCP server is available, call `warn_on_file_edit` for each suspect file. Flag files that have had 2+ past incidents — these are high-churn files that may have recurring patterns.

## Step 3 — Trace Root Cause

Read the identified files. Follow the call chain from entry point to failure:
1. Screen → BLoC event
2. BLoC event handler → UseCase
3. UseCase → Repository
4. Repository → DataSource / API call

At each layer, check:
- Layer import violations (data type leaking into domain, etc.)
- Null safety assumptions
- State emission sequence (`loading()` before async, `error()` on failure)
- Mapper assumptions (non-null fields mapped from nullable API fields)

Identify the layer where the failure originates.

## Step 4 — Propose Fix

Provide:
- **Root cause** (one sentence)
- **Code change** — file path + before/after snippet
- **Related files** that need updating (tests, mappers, DI registration)
- **Confidence**: High / Medium / Low — with reasoning

If confidence is Low, list the additional information needed to confirm the diagnosis.
