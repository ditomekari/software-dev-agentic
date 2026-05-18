---
name: builder-test-create-data
description: Create unit tests for Flutter Qontak Data layer artifacts — Mapper (pure function, no mocks) and Repository implementation (Exception → Failure via CoreMapperExceptionToFailure).
user-invocable: false
---

Create data layer tests following `lib/platforms/flutter-qontak/reference/code-architecture/testing-impl.md ## Mapper Tests` and `## Use Case Tests sections`.

## Steps

1. **Grep** `lib/platforms/flutter-qontak/reference/code-architecture/testing-impl.md` for `## Mapper Tests`; only **Read** the full file if sections cannot be located
2. **Read** the RepositoryImpl and/or Mapper file being tested
3. **Update** `test/helpers/mocks/[feature]_mocks.dart` — add `MockSpec<[Feature]RemoteDataSource>()` if testing the repository
4. **Update** `test/helpers/fixtures/[feature]_fixtures.dart` — add DTO model instances and failure fixtures
5. **Create** test files in `features/[prefix]_[feature]/test/data/repositories/` and/or `test/data/mappers/`

## Repository Test Pattern

```dart
// test/data/repositories/[feature]_repository_impl_test.dart
import 'package:flutter_test/flutter_test.dart';
import 'package:fpdart/fpdart.dart';
import 'package:mockito/mockito.dart';
import 'package:[prefix]_[feature]/src/data/repositories/[feature]_repository_impl.dart';

import '../../helpers/mocks/[feature]_mocks.mocks.dart';
import '../../helpers/fixtures/[feature]_fixtures.dart';

void main() {
  late Mock[Feature]RemoteDataSource mockDataSource;
  late [Feature]RepositoryImpl repository;

  setUp(() {
    mockDataSource = Mock[Feature]RemoteDataSource();
    repository = [Feature]RepositoryImpl(remoteDataSource: mockDataSource);
  });

  group('get[Concept]', () {
    test('returns entity when datasource succeeds', () async {
      // Arrange
      when(mockDataSource.get[Concept](any))
          .thenAnswer((_) async => t[Concept]Response);
      // Act
      final result = await repository.get[Concept]('id-1');
      // Assert
      expect(result.isRight(), isTrue);
      result.fold((_) => fail('Expected Right'), (entity) {
        expect(entity.id, t[Concept]Response.id);
      });
    });

    test('returns failure when Exception is thrown', () async {
      // Arrange
      when(mockDataSource.get[Concept](any))
          .thenThrow(Exception('Network error'));
      // Act
      final result = await repository.get[Concept]('id-1');
      // Assert
      expect(result.isLeft(), isTrue);
    });
  });
}
```

## Mapper Test Pattern (no mocks — pure functions)

```dart
// test/data/mappers/[concept]_mapper_test.dart
import 'package:flutter_test/flutter_test.dart';
import 'package:[prefix]_[feature]/src/data/mappers/[concept]_mapper.dart';
import 'package:[prefix]_[feature]/src/data/models/[concept]_response.dart';

void main() {
  group('[Concept]Mapper', () {
    test('fromResponseToEntity maps all fields', () {
      const response = [Concept]Response(
        id: 'id-1',
        name: 'Test',
        createdAt: '2026-01-15T00:00:00Z',
      );

      final entity = [Concept]Mapper.fromResponseToEntity(response);

      expect(entity.id, 'id-1');
      expect(entity.name, 'Test');
      expect(entity.createdAt, isNotNull);
    });

    test('handles null fields with defaults', () {
      const response = [Concept]Response();
      final entity = [Concept]Mapper.fromResponseToEntity(response);
      expect(entity.id, '');
      expect(entity.name, '');
    });
  });
}
```

## Rules

- Repository: two cases per method — success, `Exception` thrown (caught by `CoreMapperExceptionToFailure`)
- Mapper: two cases — all fields present, all fields null — instantiate directly, no mocks
- Never mock Mappers — they are pure static functions
- `Exception` (not `AppException`) is what `CoreMapperExceptionToFailure` catches in this codebase
- Run `dart run build_runner build --delete-conflicting-outputs` after adding `@GenerateNiceMocks`

## Output

Confirm test file paths and list all test group + test names.
