---
name: detective-debug-add-logs
description: Add strategic debug logs to a Flutter Qontak CRM codebase using QontakMonitor with [DebugTest] prefix. Uses qontakCommonDependency<QontakMonitor>().logCrashMonitor, not debugPrint.
user-invocable: false
tools: Read, Edit, Glob, Grep
---

Add debug instrumentation logs using `QontakMonitor` (from `qontak_common`, accessed via `qontakCommonDependency`) with `[DebugTest]` prefix.

## Log Format

```dart
// In repository / data source methods:
qontakCommonDependency<QontakMonitor>().logCrashMonitor(
  logName: '[DebugTest][ClassName][methodName] entry — param: $param',
);

// For error paths:
qontakCommonDependency<QontakMonitor>().logCrashMonitor(
  logName: '[DebugTest][ClassName][methodName] error — $error',
);

// In BLoC handlers (no QontakMonitor — use debugPrint for BLoC-level debug only):
debugPrint('[DebugTest][ClassName][methodName] state — before: $before, after: $after');
```

## Steps

Follow the `INSTRUMENTATION_BRIEF` provided by the caller:

1. `Grep` each target method name to locate the exact line
2. `Read` only the method body — not the full file
3. Insert log calls at entry, exit, branch points, and error handlers as specified
4. Add the `qontak_common` import if not already present in the file
5. Confirm each insertion

## Rules

- Log only at locations specified in the brief
- Never modify logic
- Never commit `[DebugTest]` logs — they are removed by `detective-debug-remove-logs`
- Use `QontakMonitor.logCrashMonitor` in repository/data source code — accessible via `qontakCommonDependency<QontakMonitor>()`
- Use `debugPrint` only in BLoC/presentation code where `QontakMonitor` is not accessible
- `logName` uses a string constant from the feature's logging constants file for production logs; for debug temp logs a descriptive string is acceptable

## Output

List each insertion: file path, method name, log type (entry / exit / branch / error).
