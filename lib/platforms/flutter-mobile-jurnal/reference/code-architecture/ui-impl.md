# UI Layer — Flutter (Jurnal)

Platform-specific UI layer patterns. Canonical definitions: `reference/code-architecture/ui-theory.md`.

---

## Dependency Rule <!-- 9 -->

UI depends on Presentation only — never imports Domain or Data directly.

Allowed imports: `Bloc`/`Cubit` types, `State`/`Event` types, `flutter/material.dart` and other Flutter framework primitives.
Forbidden: use case interfaces, repository interfaces, DTOs, mappers, datasources.

---

## Screen <!-- 18 -->

A **Screen** is a `StatelessWidget` that owns `BlocProvider` setup. Each screen file includes its argument class via `part 'argument.dart'`. The view/content is split into a separate `content.dart` file.

**Module path:** `features/<feature>/lib/src/presentation/screens/<screen_name>/`
- `screen.dart` — `BlocProvider` + `argument.dart` part
- `argument.dart` — screen argument data class (part of `screen.dart`)
- `content.dart` — `StatefulWidget` or `StatelessWidget` with `BlocConsumer`/`BlocBuilder`

**Invariants:**
- BLoC resolved via `<Feature>Injector.find<MyBloc>()` — never `context.read` or `MyBloc()` inline
- `MultiBlocProvider` wraps content widget — never nested `BlocProvider` inside content
- Observes every `ViewDataState` variant via `BlocBuilder` — no state goes unhandled
- Sends events via the Bloc instance returned from `Injector.find` — never mutates state directly
- Contains no business logic — `if`/`switch` only decides what to render

**When to create:** One Screen directory per route. Created after the Bloc contract exists.

---

## Component / Sub-view <!-- 14 -->

A **Component** is a plain `StatelessWidget` (or `StatefulWidget`) with no BLoC awareness.

**Invariants:**
- Receives entities or primitive values as constructor parameters — no BLoC access
- `ChangeNotifier`-based controllers (e.g. `CustomFieldInputController`) used only for complex multi-widget coordination without BLoC
- No use case calls — all data passed in from the parent Screen
- Reuse check required before creating — search `features/<feature>/lib/src/presentation/widgets/` and `features/jurnal_core/lib/` first

**When to create:** When a UI element appears in ≥2 screens, or when a Screen section is complex enough to isolate for readability.

---

## Navigator / Coordinator <!-- 14 -->

Navigation uses GoRouter. Route constants and navigation actions follow the standard Flutter pattern.

**Invariants:**
- The Screen delegates navigation intent via `BlocListener` — never hard-codes a destination in a button handler
- The Bloc emits a navigation action field in `State` — the Screen's `BlocListener` calls `context.go/push`
- Route constants defined in a `Routes` class — the Screen never constructs path strings inline
- One `AppRouter` per app (or per module in modular setups) — not per screen

**When to create:** When a Screen navigates to another screen.

---

## DI Wiring <!-- 13 -->

**DI wiring** registers the `Bloc`/`Cubit` via the feature's `Injector` class, which wraps `get_it`/`injectable`.

**Invariants:**
- Bloc annotated `@injectable` — scope matches feature lifetime
- Use cases injected into the Bloc constructor via `injectable` — never instantiated inside the Bloc
- Screen resolves via `<Feature>Injector.find<MyBloc>()` — never constructed inline

**When to create:** After the Screen and Bloc exist. Required before the route is reachable.

---

## Creation Order <!-- 10 -->

```
screen.dart + argument.dart + content.dart → AppRouter route entry + Routes constant → Injector registration
```

The `Bloc` and its contract must exist before any UI layer file is written.

---

## Layer Invariants <!-- 10 -->

- Screen never mutates state directly — observes via `BlocBuilder`/`BlocConsumer` only
- Screen never calls use cases directly — all interactions dispatched as Bloc events
- Bloc resolved via `Injector.find` — never `MyBloc()` inline in widget tree
- Navigation delegated via `BlocListener` — Screen emits nav action, not destination
- No data layer knowledge — no DTOs, no datasources, no HTTP types visible in widget files

---

## Planner Search Patterns <!-- 8 -->

When exploring the UI layer, glob for:
- `**/presentation/screens/**/*screen.dart` — screen files
- `**/presentation/widgets/**/*.dart` — feature-scoped widget files
- `**/presentation/widgets/components/**/*.dart` — sub-component files
- `features/jurnal_core/lib/**/*.dart` — cross-feature shared widgets

---

## Design System Bindings <!-- 22 -->

MekariPixel (`mekari_pixel`) is the design system for this platform. Agents must prefer MekariPixel components over raw Material/Cupertino widgets.

**Import pattern:**
```dart
import 'package:mekari_pixel/mekari_pixel.dart';
```

**Applying the binding table:**
The `### Design System Bindings` block in the skill prompt maps UI element descriptions to resolved MekariPixel symbols. Use the mapped symbol wherever the description appears in widget code. If no binding exists for an element, fall back to the Material equivalent.

| Common mapping | MekariPixel symbol |
|---|---|
| Primary button | `MpButton` |
| Avatar / profile image | `MpAvatar` |
| List tile | `MpListTileX` |
| Text field / input | `MpTextField` |
| Icon | `MpIcon` |

**Catalog:** `builder-pres-resolve-design` resolves symbols from `.claude/reference/design-system/mekari-pixel-flutter-catalog.md` — place the catalog there in downstream projects.
