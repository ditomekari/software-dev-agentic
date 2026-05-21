---
name: builder-domain-create-entity
description: Create a Domain Entity class for a Flutter Qontak CRM feature using freezed. No fromJson, no Entity suffix.
user-invocable: false
---

Create a Domain Entity following `lib/platforms/flutter-qontak-crm/reference/code-architecture/domain-impl.md ## Entities`.

## Steps

1. **Grep** `lib/platforms/flutter-qontak-crm/reference/code-architecture/domain-impl.md` for `## Entities`; only **Read** the full file if the section cannot be located
2. **Locate** the correct package path: `features/[crm_or_qontak]_[feature]/lib/src/domain/entities/`
3. **Type-query before each field** — before deciding the type of any field:
   - Call `search_code("<concept> enum value object", project_slug="crm")`
   - If a matching type is returned, use it; do not create a duplicate
   - If RAG is unavailable or empty: `Grep` for the concept in `features/*/lib/src/domain/`
   - Create a new type only if both confirm it does not exist
4. **Create** `[concept].dart` — named after the business concept, no `Entity` suffix

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
- Allowed imports: `dart:core`, `package:freezed_annotation`, `package:qontak_common` only

## Output

Confirm file path and list all entity fields with their types.
