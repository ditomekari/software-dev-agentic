---
name: builder-test-create-presentation
description: Create BLoC tests using bloc_test, covering all events and state transitions.
user-invocable: false
---

Create BLoC tests following `.claude/reference/code-architecture/testing-impl.md ## Presenter Tests section`.

## Steps

1. **Read** the BLoC's Event, State, and BLoC files completely — map all events and state fields
2. **Update** `test/helpers/mocks/[feature]_mocks.dart` — add `MockSpec` for each UseCase the BLoC calls
3. **Update** `test/helpers/fixtures/[feature]_fixtures.dart` — add entity and failure fixtures
4. **Locate** test path: `test/features/[feature]/presentation/blocs/`
5. **Create** `[feature]_bloc_test.dart`

## BLoC Test Pattern

```dart
import 'package:bloc_test/bloc_test.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:fpdart/fpdart.dart';
import 'package:mockito/mockito.dart';
import 'package:your_app/features/[feature]/presentation/blocs/[feature]_bloc.dart';
import 'package:your_app/features/[feature]/presentation/blocs/[feature]_event.dart';
import 'package:your_app/features/[feature]/presentation/blocs/[feature]_state.dart';

import '../../../../helpers/mocks/[feature]_mocks.mocks.dart';
import '../../../../helpers/fixtures/[feature]_fixtures.dart';

void main() {
  late Mock[Verb][Feature]UseCase mockUseCase;
  late [Feature]Bloc bloc;

  setUp(() {
    mockUseCase = Mock[Verb][Feature]UseCase();
    bloc = [Feature]Bloc([verb][Feature]UseCase: mockUseCase);
  });

  tearDown(() => bloc.close());

  group('[Feature]Bloc', () {
    test('initial state is correct', () {
      expect(bloc.state.[feature]State.isInitial, isTrue);
    });

    group('Load[Feature]', () {
      blocTest<[Feature]Bloc, [Feature]State>(
        'emits [loading, loaded] when use case succeeds',
        setUp: () {
          when(mockUseCase.call(any))
              .thenAnswer((_) async => Right(t[Feature]Entity));
        },
        build: () => bloc,
        act: (b) => b.add(
          [Feature]Event.load[Feature](id: '1'),
        ),
        expect: () => [
          predicate<[Feature]State>((s) => s.[feature]State.isLoading),
          predicate<[Feature]State>((s) => s.[feature]State.isLoaded),
        ],
        verify: (_) => verify(mockUseCase.call(any)).called(1),
      );

      blocTest<[Feature]Bloc, [Feature]State>(
        'emits [loading, error] when use case fails',
        setUp: () {
          when(mockUseCase.call(any))
              .thenAnswer((_) async => Left(tServerFailure));
        },
        build: () => bloc,
        act: (b) => b.add(
          [Feature]Event.load[Feature](id: '1'),
        ),
        expect: () => [
          predicate<[Feature]State>((s) => s.[feature]State.isLoading),
          predicate<[Feature]State>((s) => s.[feature]State.hasError),
        ],
      );
    });
  });
}
```

Rules:
- **Always `blocTest`** — never test by calling `bloc.add()` then reading `.state`
- `tearDown` always calls `bloc.close()`
- Success path + failure path per event — minimum two tests per event
- `predicate<State>()` checks state shape; `expect: [exact state]` checks exact value
- `verify()` in `blocTest.verify:` — confirms use case was called with correct args
- Initial state test (one per BLoC) verifies all fields are `isInitial`

## Coverage per event

- At least: success path, failure path
- If event has guard conditions (early returns): one test per guard

## Output

Confirm test file path, mock additions, and list all test names grouped by event.
