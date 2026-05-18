# Flutter Qontak Platform

Flutter · Modular Clean Architecture · BLoC · get_it/injectable · melos

Extends the `flutter` platform with patterns for multi-package (melos workspace)
modular architecture as standardized in the Mekari Flutter Architecture Standardization.

> Single-package patterns (entity, BLoC, mapper, etc.) live in `../flutter/reference/`.
> This platform covers only what's unique to the modular structure.

## Structure

```
lib/platforms/flutter-qontak/
  reference/
    index.md                              # What to read when
    project.md                            # Workspace layout, dependency graph, naming
    builder/
      modular-structure-impl.md           # Module types, BaseModule, ModuleRegistrar
      module-communication-impl.md        # Module API pattern (core abstraction + DI)
      di-impl.md                          # Per-module DI with Injectable MicroPackages
      localization-impl.md                # Per-feature .arb files
      flavor-impl.md                      # production/staging/sandbox flavor setup
      tech-stack-impl.md                  # Recommended dependencies and rationale
```

## Key Concepts

| Concept | Where |
|---|---|
| Workspace layout, module types, package naming | `reference/project.md` |
| Creating a new feature module | `reference/code-architecture/modular-structure-impl.md` |
| Cross-module communication | `reference/code-architecture/module-communication-impl.md` |
| DI per module | `reference/code-architecture/di-impl.md` |
| Localization per feature | `reference/code-architecture/localization-impl.md` |
| Flavors | `reference/code-architecture/flavor-impl.md` |
| Tech stack | `reference/code-architecture/tech-stack-impl.md` |

## Relationship to `flutter` Platform

Layer-level patterns (entity, repository, mapper, BLoC, testing) are identical.
This platform only adds the **module-level** organization layer on top.

Source: [Flutter Architecture Standardization](https://jurnal.atlassian.net/wiki/spaces/MOBI/pages/49042883442)
