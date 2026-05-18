---
name: builder-test-create-presentation
description: Create BLoC tests for Flutter Qontak CRM using bloc_test. Checks .status.isHasData/.status.isError via predicate<State>, named constructor params in setUp.
user-invocable: false
---

Create BLoC tests for a Flutter Qontak CRM feature. Reference: `lib/platforms/flutter-qontak-crm/reference/code-architecture/testing-impl.md ## BLoC Tests`.

## Steps

1. **Read** the BLoC's Event, State, and BLoC files completely — map all events, state fields, and use case constructor params
2. **Update** `features/[prefix]_[feature]/test/helpers/mocks/[feature]_mocks.dart` — add `MockSpec` for each UseCase the BLoC receives
3. **Update** `features/[prefix]_[feature]/test/helpers/fixtures/[feature]_fixtures.dart` — add entity and failure fixtures
4. **Locate** test path: `features/[prefix]_[feature]/test/presentation/blocs/`
5. **Create** `[feature]_bloc_test.dart`

## BLoC Test Pattern

```dart
// test/presentation/blocs/[feature]_bloc_test.dart
import 'package:bloc_test/bloc_test.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:fpdart/fpdart.dart';
import 'package:mockito/mockito.dart';
import 'package:qontak_common/qontak_common.dart';
import 'package:[prefix]_[feature]/src/presentation/bloc/[feature]/[feature]_bloc.dart';

import '../../helpers/mocks/[feature]_mocks.mocks.dart';
import '../../helpers/fixtures/[feature]_fixtures.dart';

void main() {
  late MockGet[Concept]UseCase mockGet[Concept]UseCase;
  late [Feature]Bloc bloc;

  setUp(() {
    mockGet[Concept]UseCase = MockGet[Concept]UseCase();
    bloc = [Feature]Bloc(get[Concept]UseCase: mockGet[Concept]UseCase); // named param
  });

  tearDown(() => bloc.close());

  group('[Feature]Bloc', () {
    test('initial state is correct', () {
      expect(bloc.state.[feature]State.status.isInitial, isTrue);
    });

    group('Load[Concept]', () {
      blocTest<[Feature]Bloc, [Feature]State>(
        'emits [loading, loaded] when use case succeeds',
        setUp: () {
          when(mockGet[Concept]UseCase.call(any))
              .thenAnswer((_) async => Right(t[Concept]));
        },
        build: () => bloc,
        act: (b) => b.add(const [Feature]Event.load[Concept](id: 'id-1')),
        expect: () => [
          predicate<[Feature]State>(
            (s) => s.[feature]State.status.isLoading,
            '[feature]State is loading',
          ),
          predicate<[Feature]State>(
            (s) => s.[feature]State.status.isHasData,
            '[feature]State has data',
          ),
        ],
        verify: (_) => verify(mockGet[Concept]UseCase.call(any)).called(1),
      );

      blocTest<[Feature]Bloc, [Feature]State>(
        'emits [loading, error] when use case fails',
        setUp: () {
          when(mockGet[Concept]UseCase.call(any))
              .thenAnswer((_) async => Left(tServerFailure));
        },
        build: () => bloc,
        act: (b) => b.add(const [Feature]Event.load[Concept](id: 'id-1')),
        expect: () => [
          predicate<[Feature]State>(
            (s) => s.[feature]State.status.isLoading,
            '[feature]State is loading',
          ),
          predicate<[Feature]State>(
            (s) => s.[feature]State.status.isError,
            '[feature]State is error',
          ),
        ],
      );
    });
  });
}
```

## Rules

- **Always `blocTest`** — never test by calling `bloc.add()` then reading `.state`
- `tearDown` always calls `bloc.close()`
- BLoC constructor uses **named params** — `[Feature]Bloc(get[Concept]UseCase: mock...)`
- Use case mock name includes `UseCase` suffix: `MockGet[Concept]UseCase` (matches CRM naming convention)
- Use `predicate<State>()` with `.status.isHasData` and `.status.isError` — NOT `.isLoaded` or `.hasError`
- Success path + failure path per event — minimum two tests per event
- Initial state test verifies `.status.isInitial` on all state fields
- `verify()` in `blocTest.verify:` — confirms use case was called with correct args

## Output

Confirm test file path, mock additions, and list all test names grouped by event.
