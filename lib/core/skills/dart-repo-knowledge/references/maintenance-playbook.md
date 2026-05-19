# Maintenance Playbook

## Issue Classification

Use one primary category before editing:

- `source-selection`: wrong source path, wrong pub-cache target, wrong lib root
- `git-history`: wrong repo root, Jira regex mismatch, PR regex mismatch
- `collection-naming`: unversioned, inconsistent, or non-reproducible collection names
- `query-quality`: exact symbol present but semantic retrieval is weak
- `coverage-gap`: source files or public APIs are missing from generated knowledge
- `redundancy-cleanup`: exact duplicate or concatenated content in agent or skill files

## External Repo Checklist

For pub-cache or external git repos, verify all of these before generation:

1. `--source` points at the correct `lib/` directory.
2. `--repo-dir` points at the actual git repo root.
3. `git log --oneline -n 40` from that repo shows the expected Jira pattern.
4. The chosen version label matches the source being indexed.
5. The target collection name is normalized and versioned.

## Validation Ladder

Run the narrowest checks first:

1. Focused unit test for the touched behavior.
2. One command smoke test for the affected CLI path.
3. One anchor query smoke check for a known symbol.
4. Read-only auditor run if collection quality may have changed.

## Redundancy Cleanup Rule

Only remove exact duplicates or clearly stale concatenated content.

Do not:

- merge unrelated workflows into one file just to reduce file count
- rewrite a stronger definition into a weaker generic one
- delete a file unless the surviving replacement is verified

## Completion Gate

A maintenance task is complete when:

- the focused regression is covered and passing
- the intended command path behaves correctly
- at least one anchor symbol is verified by query smoke check
- exact-duplicate cleanup preserves behavior
- collection naming and provenance are clear when version matters
