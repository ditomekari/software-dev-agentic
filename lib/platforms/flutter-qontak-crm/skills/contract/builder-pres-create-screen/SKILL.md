---
name: builder-pres-create-screen
description: Create a Screen widget for Flutter Qontak CRM. BlocProvider lives in route_manager.dart — the screen only reads state and dispatches events. Uses .status.isHasData/.status.isError.
user-invocable: false
---

Create a Screen following `lib/platforms/flutter-qontak-crm/reference/code-architecture/presentation-impl.md ## Screen Structure`.

## Steps

1. **Read** the BLoC's Event and State files completely — must match types exactly
2. **Grep** `lib/presentation/route_manager.dart` for `MaterialPageRoute` to understand the route registration pattern
3. **Locate** path: `lib/presentation/screens/[feature]/` (app-level) or `features/[prefix]_[feature]/lib/src/presentation/screens/`
4. **Create** `[feature]_screen.dart`
5. **Update** `lib/presentation/route_manager.dart` — add the case block with `BlocProvider`

## Screen Pattern

```dart
// [feature]_screen.dart
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../bloc/[feature]/[feature]_bloc.dart';

class [Feature]Screen extends StatefulWidget {
  const [Feature]Screen({super.key});

  @override
  State<[Feature]Screen> createState() => _[Feature]ScreenState();
}

class _[Feature]ScreenState extends State<[Feature]Screen> {
  late final [Feature]Bloc _bloc;

  @override
  void initState() {
    super.initState();
    // Pull dependencies directly from the accessor — not via context
    _bloc = qontak[Feature]Dependency<[Feature]Bloc>()
      ..add(const [Feature]Event.load[Concept](id: ''));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: BlocConsumer<[Feature]Bloc, [Feature]State>(
        bloc: _bloc,
        listenWhen: (prev, curr) => prev.[feature]State != curr.[feature]State,
        listener: (context, state) {
          if (state.[feature]State.status.isHasData) {
            // navigate or show success
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
// lib/presentation/route_manager.dart — add inside the route switch
case AppRoute.[feature]:
  final args = settings.arguments as [Feature]Argument?;
  return MaterialPageRoute(
    settings: settings,
    builder: (_) => BlocProvider(
      create: (_) => [Feature]Bloc(
        get[Concept]UseCase: qontak[Feature]Dependency(),
      ),
      child: [Feature]Screen(args: args),
    ),
  );
```

## Rules

- Screens are `StatefulWidget` — fetch dependencies directly from the accessor in `initState`, not via `context`
- Use `.status.isHasData` (not `.isLoaded`), `.status.isError` (not `.hasError`)
- Navigation side effects go in `BlocListener` / `BlocConsumer.listener` — BLoC never calls navigation directly
- `listenWhen` and `buildWhen` must filter on the specific state field
- Add route constant to `AppRoute` if missing
- `BlocProvider` lives in `route_manager.dart`, not inside the screen widget

## Output

Confirm file path, list all handled state cases and dispatched events, and confirm route_manager.dart update.
