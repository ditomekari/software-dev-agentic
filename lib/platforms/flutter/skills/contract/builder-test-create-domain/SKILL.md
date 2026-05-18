---
name: builder-test-create-domain
description: Create unit tests for Domain layer artifacts — UseCase and Domain Service.
user-invocable: false
---

Create domain tests following `.claude/reference/code-architecture/testing-impl.md ## Use Case Tests section`.

## Steps

1. **Grep** `.claude/reference/code-architecture/testing-impl.md` for `## Use Case Tests`; only **Read** the full file if the section cannot be located
2. **Read** the UseCase/Service file being tested — map all inputs and return types
3. **Check** `test/helpers/mocks/[feature]_mocks.dart` — create or update it with `@GenerateNiceMocks`
4. **Check** `test/helpers/fixtures/[feature]_fixtures.dart` — create or update with test data
5. **Locate** test path: `test/features/[feature]/domain/usecases/`
6. **Create** `[verb]_[feature]_usecase_test.dart`

## UseCase Test Pattern

```dart
import 'package:flutter_test/flutter_test.dart';
import 'package:fpdart/fpdart.dart';
import 'package:mockito/mockito.dart';
import 'package:your_app/features/[feature]/domain/usecases/[verb]_[feature]_usecase.dart';

import '../../../../helpers/mocks/[feature]_mocks.mocks.dart';
import '../../../../helpers/fixtures/[feature]_fixtures.dart';

void main() {
  late Mock[Feature]Repository mockRepository;
  late [Verb][Feature]UseCase useCase;

  setUp(() {
    mockRepository = Mock[Feature]Repository();
    useCase = [Verb][Feature]UseCase(repository: mockRepository);
  });

  group('[Verb][Feature]UseCase', () {
    test('returns entity when repository succeeds', () async {
      // Arrange
      when(mockRepository.[method](any)).thenAnswer(
        (_) async => Right(t[Feature]Entity),
      );
      // Act
      final result = await useCase(t[Feature]Params);
      // Assert
      expect(result, Right(t[Feature]Entity));
      verify(mockRepository.[method](any)).called(1);
      verifyNoMoreInteractions(mockRepository);
    });

    test('returns failure when repository fails', () async {
      // Arrange
      when(mockRepository.[method](any)).thenAnswer(
        (_) async => Left(tServerFailure),
      );
      // Act
      final result = await useCase(t[Feature]Params);
      // Assert
      expect(result.isLeft(), isTrue);
    });
  });
}
```

Rules:
- AAA: Arrange / Act / Assert — in that order, labelled with comments
- One concept per test
- Both success and failure paths for every method
- Mock at the repository boundary only
- `verifyNoMoreInteractions` after the last expected call

## Output

Confirm test file path, mock additions, fixture additions, and list all test names.
