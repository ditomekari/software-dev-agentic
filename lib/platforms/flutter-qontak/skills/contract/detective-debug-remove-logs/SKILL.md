---
name: detective-debug-remove-logs
description: Remove all [DebugTest] MkrLogHelper debug statements from a Flutter Qontak codebase before committing.
user-invocable: false
tools: Grep, Edit, Glob
---

Remove all `MkrLogHelper.log('[DebugTest]...)` statements added during debugging.

## Steps

1. `Grep` for `\[DebugTest\]` across all `.dart` files in the project
2. For each match: remove the `MkrLogHelper.log(...)` line entirely
3. If a file's only `MkrLogHelper` usage was `[DebugTest]` lines, check if the import can also be removed
4. Verify: run `Grep` again for `\[DebugTest\]` — result must be zero matches

## Rules

- Never remove non-`[DebugTest]` logging (`MkrLogHelper.log` without `[DebugTest]`, `print`, `debugPrint`, etc.)
- Never remove adjacent code
- Do not remove the `chat_core` import if it is used for other purposes in the same file
