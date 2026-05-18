---
name: detective-debug-add-logs
description: Add strategic debug logs to a Flutter Qontak codebase using MkrLogHelper with [DebugTest] prefix. Uses qontak_common.MkrLogHelper, not debugPrint.
user-invocable: false
tools: Read, Edit, Glob, Grep
---

Add debug instrumentation logs using `MkrLogHelper` (from `qontak_common`, re-exported via `chat_core`) with `[DebugTest]` prefix.

## Log Format

```dart
// Import at top of file if not already present
import 'package:chat_core/chat_core.dart'; // re-exports MkrLogHelper

// Entry point
MkrLogHelper.log('[DebugTest][ClassName][methodName] entry — param: $param');

// State change
MkrLogHelper.log('[DebugTest][ClassName][methodName] state — before: $before, after: $after');

// Branch
MkrLogHelper.log('[DebugTest][ClassName][methodName] branch — condition: $condition');

// Error handler
MkrLogHelper.log('[DebugTest][ClassName][methodName] error — $error', isError: true);
```

## Steps

Follow the `INSTRUMENTATION_BRIEF` provided by the caller:

1. `Grep` each target method name to locate the exact line
2. `Read` only the method body — not the full file
3. Insert `MkrLogHelper.log('[DebugTest]...')` at entry, exit, branch points, and error handlers as specified
4. Add the `chat_core` import if not already present in the file
5. Confirm each insertion

## Rules

- Log only at locations specified in the brief
- Never modify logic
- Never commit `[DebugTest]` logs — they are removed by `detective-debug-remove-logs`
- Use `MkrLogHelper` not `debugPrint` — this codebase uses the internal `MkrLogHelper` from `qontak_common`
- `isError: true` for error handlers — routes to Crashlytics non-fatal in non-debug builds
