---
name: builder-data-create-mapper
description: Create a DTO model (Response/Request/Db) and a static Mapper class for a Flutter Qontak CRM feature. Mapper has private constructor and static methods named from{Source}To{Target}.
user-invocable: false
---

Create a DTO model and Mapper following `lib/platforms/flutter-qontak-crm/reference/code-architecture/data-impl.md ## DTO Models` and `## Mappers`.

## Steps

1. **Grep** `lib/platforms/flutter-qontak-crm/reference/code-architecture/data-impl.md` for `## DTO Models`; only **Read** the full file if the section cannot be located
2. **Verify** the domain entity exists in `features/[prefix]_[feature]/lib/src/domain/entities/`
3. **Locate** paths:
   - Remote model: `features/[prefix]_[feature]/lib/src/data/models/remote/`
   - Local/DB model: `features/[prefix]_[feature]/lib/src/data/models/local/`
   - Mapper: `features/[prefix]_[feature]/lib/src/data/mappers/`
4. **Create** `[concept]_response.dart` (and `[concept]_request.dart` / `[concept]_db.dart` if needed), then `[concept]_mapper.dart`

## Response Model Pattern (feature package — uses Response suffix)

```dart
// features/[prefix]_[feature]/lib/src/data/models/remote/[concept]_response.dart
import 'package:freezed_annotation/freezed_annotation.dart';

part '[concept]_response.freezed.dart';
part '[concept]_response.g.dart';

@freezed
class [Concept]Response with _$[Concept]Response {
  const factory [Concept]Response({
    @JsonKey(name: 'id') String? id,
    @JsonKey(name: 'name') String? name,
    @JsonKey(name: 'created_at') String? createdAt,
  }) = _[Concept]Response;

  factory [Concept]Response.fromJson(Map<String, dynamic> json) =>
      _$[Concept]ResponseFromJson(json);
}
```

## Mapper Pattern

```dart
// features/[prefix]_[feature]/lib/src/data/mappers/[concept]_mapper.dart
import 'package:[prefix]_[feature]/src/domain/entities/[concept].dart';
import '../models/remote/[concept]_response.dart';

class [Feature]Mapper {
  const [Feature]Mapper._(); // private constructor — pure static functions, no instantiation

  static [Concept] fromResponseToEntity([Concept]Response r) => [Concept](
        id: r.id ?? '',
        name: r.name ?? '',
        createdAt: r.createdAt != null ? DateTime.tryParse(r.createdAt!) : null,
      );

  // Add fromEntityToDb / fromDbToEntity only if local persistence is needed
}
```

## Rules

- All DTO fields nullable — API data is untrusted; handle defaults in mapper, not entity
- `@JsonKey(name:)` for snake_case ↔ camelCase mapping
- Both `.freezed.dart` and `.g.dart` parts required on DTOs (unlike entities which have only `.freezed.dart`)
- Mapper: private constructor `._()` to prevent instantiation; naming pattern `from{Source}To{Target}`
- One mapper class per domain entity (may have multiple static methods for different source types)
- Explicit null defaults in mapper — never assume API fields are present
- Date string → `DateTime` conversion in mapper, not entity
- No business logic in models
- Run `dart run build_runner build --delete-conflicting-outputs` in the feature package after creating DTO models

## Output

Confirm both file paths and list all mapped fields with their source → target names.
