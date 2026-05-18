---
name: builder-domain-create-entity
description: |
  Create a Domain Entity data class for a new feature.
user-invocable: false
---

Create a Domain Entity following `.claude/reference/code-architecture/domain-impl.md ## Entities section` and naming conventions in `.claude/reference/project.md ## Conventions & Naming section`.

## Steps

1. **Grep** `.claude/reference/code-architecture/domain-impl.md` for `## Entities`; only **Read** the full file if the section cannot be located
2. **Locate** the correct path: `feature_[module]/src/main/java/co/talenta/feature_[module]/domain/entity/`
3. **Create** `[Entity].kt`

## Entity Pattern

```kotlin
data class FeatureEntity(
    val id: String,
    val name: String,
    val count: Int,
    val isActive: Boolean
)
```

Rules:
- Pure Kotlin data class — no `@SerializedName`, no Android imports
- All properties `val` (immutable domain objects)
- All properties non-nullable — use defaults only when the domain genuinely has one
- Field names use domain terminology, not API field names

## Output

Confirm the file path created and list all properties.
