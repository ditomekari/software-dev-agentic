---
name: builder-pres-create-screen
description: Create a Screen widget for Flutter Qontak. BlocProvider lives in route_manager.dart — the screen only reads state and dispatches events. Uses .status.isHasData/.status.isError.
user-invocable: false
---

Create a Screen following `lib/platforms/flutter-qontak/reference/code-architecture/presentation-impl.md ## Screen Structure` and `## BlocListener (Side Effects) sections`.

## Steps

1. **Read** the BLoC's Event and State files completely — must match types exactly
2. **Grep** `lib/platforms/flutter-qontak/reference/code-architecture/presentation-impl.md` for `## Screen Structure`; only **Read** the full file if the section cannot be located
3. **Grep** `lib/platforms/flutter-qontak/reference/code-architecture/navigation-impl.md` for `## AppRouteManger` to confirm the route constant and arguments pattern
4. **Locate** path: `lib/presentation/screens/[feature]/` (app-level) or `features/[prefix]_[feature]/lib/src/presentation/screens/`
5. **Create** `[feature]_screen.dart`
6. **Update** `lib/route_manager.dart` — add the `case QontakAppRoute.[feature]:` block with `BlocProvider`

## Screen Pattern

```dart
// [feature]_screen.dart
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../bloc/[feature]/[feature]_bloc.dart';

class [Feature]Screen extends StatelessWidget {
  const [Feature]Screen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: BlocConsumer<[Feature]Bloc, [Feature]State>(
        listenWhen: (prev, curr) => prev.[feature]State != curr.[feature]State,
        listener: (context, state) {
          if (state.[feature]State.status.isHasData) {
            // navigate or show success
            Navigator.of(context).pushReplacementNamed(QontakAppRoute.main);
          } else if (state.[feature]State.status.isError) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text(state.[feature]State.message ?? '[Feature] failed'),
              ),
            );
          }
        },
        buildWhen: (prev, curr) => prev.[feature]State != curr.[feature]State,
        builder: (context, state) {
          if (state.[feature]State.status.isLoading) {
            return const Center(child: CircularProgressIndicator());
          }
          if (state.[feature]State.status.isError) {
            return Center(
              child: Text(state.[feature]State.message ?? 'Something went wrong'),
            );
          }
          if (state.[feature]State.data == null) {
            return const Center(child: Text('No data'));
          }
          return [Feature]Content(data: state.[feature]State.data!);
        },
      ),
    );
  }
}
```

## Route Registration (in route_manager.dart)

```dart
// lib/route_manager.dart — add inside AppRouteManger.getRoute()
case QontakAppRoute.[feature]:
  return BlocProvider(
    create: (_) => [feature]Dependency<[Feature]Bloc>()
      ..add([Feature]Event.[verb][Concept]()),  // or dispatch initial event
    child: const [Feature]Screen(),
  );
```

## Rules

- Screens do NOT own `BlocProvider` — it lives in `route_manager.dart`
- Use `.status.isHasData` (not `.isLoaded`), `.status.isError` (not `.hasError`) — these are `ViewDataStatus` extension methods
- Navigation side effects go in `BlocListener` / `BlocConsumer.listener` — BLoC never calls `NavigationHelper` directly
- `listenWhen` and `buildWhen` must filter on the specific state field — not `(_, __) => true`
- Add route constant to `QontakAppRoute` if missing

## Output

Confirm file path, list all handled state cases and dispatched events, and confirm route_manager.dart update.
