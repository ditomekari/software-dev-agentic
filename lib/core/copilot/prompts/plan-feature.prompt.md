---
mode: agent
tools:
  - codebase
  - readFile
  - editFiles
  - search
description: "Plan a new feature across all Clean Architecture layers — produces artifact tables (Domain / Data / Presentation / Widgets) ready for implementation."
---

Plan the feature described in `$ARGUMENTS`. If no description is provided, ask the user:
1. Feature name (e.g. `company_detail`, `inbox_filter`)
2. What operations does it perform? (list, create, update, delete, read-only, or combination)
3. Does it involve multiple data sources or APIs?
4. New screen, or extending an existing one?

## Planning Steps

Work through each layer top-down. Do not write any code yet — produce artifact tables only.

### Domain Layer

1. **Entities** — list each entity with its key fields and types. Apply entity rules:
   - Use typed enums for status/category fields, not `String`
   - Use named typed fields for fixed-arity relations
   - No UI state fields

2. **Repository Interface** — one interface per aggregate root; list methods with signature

3. **UseCases** — one per operation: `<Verb><Entity>UseCase`. If the screen needs data from 2+ repositories → add `Get<Screen>PageDataUseCase` returning `<Screen>PageData` read model

4. **Read Models** — if Page Init UseCase is needed: `<Screen>PageData` as a `@freezed` class in `domain/read_models/`

### Data Layer

1. **DTOs** — one per API endpoint / response shape
2. **Mappers** — one per source; if multi-source, note the merge strategy
3. **DataSources** — remote and/or local
4. **RepositoryImpl** — note if multi-source merging is required

### Presentation Layer

1. **BLoC** — events list, state shape (`ViewDataState<T>` per async operation)
2. **Screen** — name and which BLoC(s) it uses
3. **Components** — list each reusable widget component

### Design System / Widget Check

For each UI component, search MekariPixel (`mekari_pixel_query` if available) and qontak_component_lib (CRM only) before listing as a new custom widget.

| Component | Source | Symbol or Note |
|---|---|---|
| (keyword) | MekariPixel / qontak_component_lib / New | `MpXxx` / `QontakXxx` / scope |

## Output Format

Present the complete plan as tables. Then ask:

> **Ready to implement?**
> Confirm the plan and I will create all artifacts in layer order.

Wait for confirmation before generating any files.
