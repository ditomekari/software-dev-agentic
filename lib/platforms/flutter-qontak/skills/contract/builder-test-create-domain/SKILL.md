---
name: builder-test-create-domain
description: Create unit tests for Flutter Qontak Domain layer artifacts — UseCase and Domain Service. Mock at repository boundary, AAA pattern.
user-invocable: false
---

Create domain tests following `lib/platforms/flutter-qontak/reference/code-architecture/testing-impl.md ## Use Case Tests section`.

## Steps

1. **Grep** `lib/platforms/flutter-qontak/reference/code-architecture/testing-impl.md` for `## Use Case Tests`; only **Read** the full file if the section cannot be located
2. **Read** the UseCase/Service file being tested — map all inputs, params classes, and return types
3. **Check** `test/helpers/mocks/[feature]_mocks.dart` — create or update with `@GenerateNiceMocks` for the repository
4. **Check** `test/helpers/fixtures/[feature]_fixtures.dart` — create or update with entity and failure fixtures
5. **Locate** test path: `features/[prefix]_[feature]/test/domain/usecases/`
6. **Create** `[verb]_[concept]_test.dart`

## UseCase Test Pattern

```dart
// features/[prefix]_[feature]/test/domain/usecases/get_[concept]_test.dart
import 'package:flutter_test/flutter_test.dart';
import 'package:fpdart/fpdart.dart';
import 'package:mockito/mockito.dart';
import 'package:[prefix]_[feature]/src/domain/usecases/get_[concept].dart';
import 'package:[prefix]_core/[prefix]_core.dart';

import '../../helpers/mocks/[feature]_mocks.mocks.dart';
import '../../helpers/fixtures/[feature]_fixtures.dart';

void main() {
  late Mock[Feature]Repository mockRepository;
  late Get[Concept] useCase;

  setUp(() {
    mockRepository = Mock[Feature]Repository();
    useCase = Get[Concept](repository: mockRepository);
  });

  group('Get[Concept]', () {
    test('returns entity when repository succeeds', () async {
      // Arrange
      when(mockRepository.get[Concept](any)).thenAnswer(
        (_) async => Right(t[Concept]),
      );
      // Act
      final result = await useCase(Get[Concept]Params(id: 'id-1'));
      // Assert
      expect(result, Right(t[Concept]));
      verify(mockRepository.get[Concept]('id-1')).called(1);
      verifyNoMoreInteractions(mockRepository);
    });

    test('returns failure when repository fails', () async {
      // Arrange
      when(mockRepository.get[Concept](any)).thenAnswer(
        (_) async => Left(tServerFailure),
      );
      // Act
      final result = await useCase(Get[Concept]Params(id: 'id-1'));
      // Assert
      expect(result.isLeft(), isTrue);
    });
  });
}
```

## Mock File Pattern

```dart
// test/helpers/mocks/[feature]_mocks.dart
import 'package:mockito/annotations.dart';
import 'package:[prefix]_[feature]/src/domain/repositories/[feature]_repository.dart';

@GenerateNiceMocks([
  MockSpec<[Feature]Repository>(),
])
void main() {}
```

## Fixtures Pattern

```dart
// test/helpers/fixtures/[feature]_fixtures.dart
import 'package:[prefix]_core/[prefix]_core.dart';
import 'package:[prefix]_[feature]/src/domain/entities/[concept].dart';

final t[Concept] = [Concept](
  id: 'id-1',
  name: 'Test [Concept]',
);

final tServerFailure = Failure.serverFailure(
  message: 'Server error',
  developerMessage: 'HTTP 500',
);
```

## Rules

- AAA: Arrange / Act / Assert — in that order, labelled with comments
- One concept per test
- Both success and failure paths for every method
- Mock at the repository boundary only — never mock the UseCase itself
- `verifyNoMoreInteractions` after the last expected call
- Run `dart run build_runner build --delete-conflicting-outputs` in the feature package after adding `@GenerateNiceMocks`

## Output

Confirm test file path, mock additions, fixture additions, and list all test names.
