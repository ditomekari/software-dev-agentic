---
name: builder-domain-create-entity
description: Create a Domain Entity class for a new feature using freezed.
user-invocable: false
---

Create a Domain Entity following `.claude/reference/code-architecture/domain-impl.md ## Entities section`.

## Steps

1. **Grep** `.claude/reference/code-architecture/domain-impl.md` for `## Entities`; only **Read** the full file if the section cannot be located
2. **Locate** the correct feature path: `lib/src/features/[feature]/domain/entities/`
3. **Create** `[feature]_entity.dart`

## Entity Pattern

```dart
import 'package:freezed_annotation/freezed_annotation.dart';

part '[feature]_entity.freezed.dart'; // .freezed.dart only — never .g.dart; entities are not serialised

@freezed
class [Feature]Entity with _$[Feature]Entity {
  const factory [Feature]Entity({
    required String id,
    required String name,
    // required fields first; T? only when domain genuinely allows null
    DateTime? createdAt,
  }) = _[Feature]Entity;
  // no fromJson — entities are never deserialised from JSON
}
```

## Output

Confirm file path and list all entity fields.
