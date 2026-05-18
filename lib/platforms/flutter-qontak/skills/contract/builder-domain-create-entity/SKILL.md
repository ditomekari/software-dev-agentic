---
name: builder-domain-create-entity
description: Create a Domain Entity class for a Flutter Qontak feature using freezed. No fromJson, no Entity suffix.
user-invocable: false
---

Create a Domain Entity following `lib/platforms/flutter-qontak/reference/code-architecture/domain-impl.md ## Entities section`.

## Steps

1. **Grep** `lib/platforms/flutter-qontak/reference/code-architecture/domain-impl.md` for `## Entities`; only **Read** the full file if the section cannot be located
2. **Locate** the correct package path: `features/[prefix]_[feature]/lib/src/domain/entities/`
3. **Create** `[concept].dart` — named after the business concept, no `Entity` suffix

## Entity Pattern

```dart
// features/[prefix]_[feature]/lib/src/domain/entities/[concept].dart
import 'package:freezed_annotation/freezed_annotation.dart';

part '[concept].freezed.dart'; // .freezed.dart only — never .g.dart

@freezed
class [Concept] with _$[Concept] {
  const factory [Concept]({
    required String id,
    required String name,
    // required fields first; T? only when domain genuinely allows null
    DateTime? createdAt,
  }) = _[Concept];
  // no fromJson — entities are never deserialised from JSON
}
```

## Rules

- `@freezed` for immutability + `copyWith`
- Only `.freezed.dart` part — never `.g.dart`
- No `@JsonKey`, no `fromJson`, no `toJson`
- Named after the business concept — no `Entity` suffix
- All nullable DTO fields become non-null with defaults at the mapper boundary, not here
- Allowed imports: `dart:core`, `package:freezed_annotation`, `package:[prefix]_core/[prefix]_core.dart` only

## Output

Confirm file path and list all entity fields with their types.
