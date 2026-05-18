---
name: detective-debug-remove-logs
description: Remove all [DebugTest] debug log statements from a Flutter Qontak CRM codebase before committing.
user-invocable: false
tools: Grep, Edit, Glob
---

Remove all `[DebugTest]` debug log statements added during debugging.

## Steps

1. `Grep` for `\[DebugTest\]` across all `.dart` files in the project
2. For each match: remove the entire log statement line
   - `qontakCommonDependency<QontakMonitor>().logCrashMonitor(logName: '...[DebugTest]...')` → remove entire call
   - `debugPrint('[DebugTest]...')` → remove entire call
3. If a file's only `QontakMonitor` usage was `[DebugTest]` lines, check if the import can also be removed
4. Verify: run `Grep` again for `\[DebugTest\]` — result must be zero matches

## Rules

- Never remove non-`[DebugTest]` logging (production `logCrashMonitor` calls without `[DebugTest]`, `print`, `debugPrint` without `[DebugTest]`, etc.)
- Never remove adjacent code
- Do not remove the `qontak_common` import if it is used for other purposes in the same file

## Output

Confirm count of lines removed and final grep result showing zero matches.
