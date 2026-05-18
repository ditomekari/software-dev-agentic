---
name: builder-test-create-data
description: Create unit tests for Flutter Qontak CRM Data layer — Mapper (pure function, no mocks) and RepositoryImpl (Exception → Failure via try/catch or TaskEither).
user-invocable: false
---

Create data layer tests for a Flutter Qontak CRM feature. Reference: `lib/platforms/flutter-qontak-crm/reference/code-architecture/testing-impl.md ## Mapper Tests`.

## Steps

1. **Read** the RepositoryImpl and/or Mapper file being tested
2. **Update** `features/[prefix]_[feature]/test/helpers/mocks/[feature]_mocks.dart` — add `MockSpec<[Feature]RemoteDataSource>()` if testing the repository
3. **Update** `features/[prefix]_[feature]/test/helpers/fixtures/[feature]_fixtures.dart` — add DTO model instances and failure fixtures
4. **Create** test files in `features/[prefix]_[feature]/test/data/repositories/` and/or `test/data/mappers/`

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
        expect(entity.id, t[Concept]Response.id ?? '');
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
// test/data/mappers/[feature]_mapper_test.dart
import 'package:flutter_test/flutter_test.dart';
import 'package:[prefix]_[feature]/src/data/mappers/[feature]_mapper.dart';
import 'package:[prefix]_[feature]/src/data/models/remote/[concept]_response.dart';

void main() {
  group('[Feature]Mapper', () {
    test('fromResponseToEntity maps all fields', () {
      const response = [Concept]Response(
        id: 'id-1',
        name: 'Test',
        createdAt: '2026-01-15T00:00:00Z',
      );

      final entity = [Feature]Mapper.fromResponseToEntity(response);

      expect(entity.id, 'id-1');
      expect(entity.name, 'Test');
      expect(entity.createdAt, isNotNull);
    });

    test('handles null fields with defaults', () {
      const response = [Concept]Response();
      final entity = [Feature]Mapper.fromResponseToEntity(response);
      expect(entity.id, '');
      expect(entity.name, '');
    });
  });
}
```

## Rules

- Repository: two cases per method — success, `Exception` thrown
- Mapper: two cases — all fields present, all fields null — instantiate directly, no mocks
- Never mock Mappers — they are pure static functions
- Run `dart run build_runner build --delete-conflicting-outputs` after adding `@GenerateNiceMocks`

## Output

Confirm test file paths and list all test group + test names.
