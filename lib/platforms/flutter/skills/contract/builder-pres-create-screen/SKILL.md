---
name: builder-pres-create-screen
description: Create a Screen widget with BlocProvider and a View widget with BlocBuilder/BlocListener bindings.
user-invocable: false
---

Create a Screen following `.claude/reference/code-architecture/presentation-impl.md ## Screen Structure section`.

## Steps

1. **Read** the BLoC's Event and State files completely — must match types exactly
2. **Grep** `.claude/reference/code-architecture/presentation-impl.md` for `## Screen Structure` and `## BlocListener (Side Effects)`
3. **Locate** path: `lib/src/features/[feature]/presentation/screens/`
4. **Create** `[feature]_screen.dart`

## Screen Pattern

```dart
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../di/injection.dart';
import '../blocs/[feature]_bloc.dart';
import '../blocs/[feature]_event.dart';
import '../blocs/[feature]_state.dart';

class [Feature]Screen extends StatelessWidget {
  const [Feature]Screen({super.key, required this.[param]});

  final String [param];   // e.g. featureId

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (_) => getIt<[Feature]Bloc>()
        ..add([Feature]Event.load[Feature]([param]: [param])),
      child: const _[Feature]View(),
    );
  }
}

class _[Feature]View extends StatelessWidget {
  const _[Feature]View();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('[Feature]')),
      body: BlocConsumer<[Feature]Bloc, [Feature]State>(
        listenWhen: (prev, curr) =>
            prev.[feature]State != curr.[feature]State,
        listener: (context, state) {
          // side effects: navigation, toasts
        },
        buildWhen: (prev, curr) =>
            prev.[feature]State != curr.[feature]State,
        builder: (context, state) {
          final s = state.[feature]State;
          if (s.isLoading || s.isInitial) {
            return const Center(child: CircularProgressIndicator());
          }
          if (s.hasError) {
            return Center(child: Text(s.message ?? 'Error'));
          }
          if (s.data == null) {
            return const Center(child: Text('Not found'));
          }
          return [Feature]Content(entity: s.data!);
        },
      ),
    );
  }
}
```

## Output

Confirm file path and list all handled state cases and dispatched events.
