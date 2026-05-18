---
name: builder-test-create-domain
description: Create unit tests for Flutter Qontak CRM Domain layer — UseCase and Domain Service. Mock at repository boundary, AAA pattern.
user-invocable: false
---

Create domain tests for a Flutter Qontak CRM feature. Reference: `lib/platforms/flutter-qontak-crm/reference/code-architecture/testing-impl.md ## Use Case Tests`.

## Steps

1. **Read** the UseCase/Service file being tested — map all inputs, params classes, and return types
2. **Check** `features/[prefix]_[feature]/test/helpers/mocks/[feature]_mocks.dart` — create or update with `@GenerateNiceMocks` for the repository
3. **Check** `features/[prefix]_[feature]/test/helpers/fixtures/[feature]_fixtures.dart` — create or update with entity and failure fixtures
4. **Locate** test path: `features/[prefix]_[feature]/test/domain/usecases/`
5. **Create** `[verb]_[concept]_usecase_test.dart`

## UseCase Test Pattern

```dart
// features/[prefix]_[feature]/test/domain/usecases/get_[concept]_usecase_test.dart
import 'package:flutter_test/flutter_test.dart';
import 'package:fpdart/fpdart.dart';
import 'package:mockito/mockito.dart';
import 'package:[prefix]_[feature]/src/domain/usecases/get_[concept]_usecase.dart';
import 'package:qontak_common/qontak_common.dart';

import '../../helpers/mocks/[feature]_mocks.mocks.dart';
import '../../helpers/fixtures/[feature]_fixtures.dart';

void main() {
  late Mock[Feature]Repository mockRepository;
  late Get[Concept]UseCase useCase;

  setUp(() {
    mockRepository = Mock[Feature]Repository();
    useCase = Get[Concept]UseCase(repository: mockRepository);
  });

  group('Get[Concept]UseCase', () {
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
// features/[prefix]_[feature]/test/helpers/mocks/[feature]_mocks.dart
import 'package:mockito/annotations.dart';
import 'package:[prefix]_[feature]/src/domain/repositories/[feature]_repository.dart';

@GenerateNiceMocks([
  MockSpec<[Feature]Repository>(),
])
void main() {}
```

## Fixtures Pattern

```dart
// features/[prefix]_[feature]/test/helpers/fixtures/[feature]_fixtures.dart
import 'package:qontak_common/qontak_common.dart';
import 'package:[prefix]_[feature]/src/domain/entities/[concept].dart';

final t[Concept] = [Concept](
  id: 'id-1',
  name: 'Test [Concept]',
);

final tServerFailure = Failure(message: 'Server error');
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
