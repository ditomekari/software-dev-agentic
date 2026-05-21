---
mode: agent
tools:
  - codebase
  - readFile
  - editFiles
  - search
description: "Create a CRM domain entity — @freezed, no Entity suffix, no fromJson. Runs type-query via RAG before writing each field to prevent duplicate types."
---

Create a domain entity for the concept described in `$ARGUMENTS`. If not provided, ask for the concept name and feature.

## Steps

### 1 — Type-query before each field

Before deciding the type for any field, check if a more precise type already exists:

- **RAG (primary):** Call `search_code("<concept> enum value object", project_slug: "crm")` via the mobile-qontak MCP server. If a matching enum, value object, or typed ID is returned — use it.
- **Grep fallback:** If RAG is unavailable or returns no results, search the workspace for the concept term in `features/*/lib/src/domain/`.
- **Create new type only** when both confirm it does not exist.

### 2 — Locate the path

```
features/[crm_or_qontak]_[feature]/lib/src/domain/entities/[concept].dart
```

### 3 — Rules when writing

- `@freezed` with `part '[concept].freezed.dart'` only — never `.g.dart`
- No `Entity` suffix — name after the business concept
- No `Map<String, dynamic>` or `dynamic` fields
- No `bool` fields set by user interaction — those belong in BLoC state
- `List<TypedValueObject>` not `List<String>` for relationship collections
- Required fields first; nullable `T?` only when the domain genuinely allows absence
- No `@JsonSerializable`, `fromJson`, or `toJson`
- Allowed imports: `dart:core`, `package:freezed_annotation`, `package:qontak_common` only

### 4 — Pattern

```dart
// features/[prefix]_[feature]/lib/src/domain/entities/[concept].dart
import 'package:freezed_annotation/freezed_annotation.dart';

part '[concept].freezed.dart';

@freezed
class [Concept] with _$[Concept] {
  const factory [Concept]({
    required String id,
    required String name,
    // required fields first; T? only when domain genuinely allows null
    DateTime? createdAt,
  }) = _[Concept];
}
```

### 5 — Verify after creation

Check the five semantic quality questions:
1. **Type** — is every field the most precise type available?
2. **Origin** — does any field receive an API value as-is? (mapper failure if so)
3. **Ownership** — does any field get set by a UI action? (belongs in BLoC state if so)
4. **Cardinality** — are `List<>` fields fixed-arity or backend-configurable?
5. **Vocabulary** — if unifying multiple APIs, are canonical domain terms used throughout?
