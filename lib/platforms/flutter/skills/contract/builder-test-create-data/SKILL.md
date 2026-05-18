---
name: builder-test-create-data
description: Create unit tests for Data layer artifacts — Mapper, Repository implementation.
user-invocable: false
---

Create data layer tests following `.claude/reference/code-architecture/testing-impl.md ## Repository Tests, ## Mapper Tests sections`.

## Steps

1. **Grep** `.claude/reference/code-architecture/testing-impl.md` for `## Repository Tests` and `## Mapper Tests`
2. **Read** the RepositoryImpl and/or Mapper file being tested
3. **Update** `test/helpers/mocks/[feature]_mocks.dart` with any missing mock specs
4. **Update** `test/helpers/fixtures/[feature]_fixtures.dart` with models and responses
5. **Create** test files in `test/features/[feature]/data/repositories/` and/or `data/mappers/`

## Repository Test Pattern

```dart
void main() {
  late Mock[Feature]RemoteDataSource mockDataSource;
  late Mock[Feature]Mapper mockMapper;
  late [Feature]RepositoryImpl repository;

  setUp(() {
    mockDataSource = Mock[Feature]RemoteDataSource();
    mockMapper = Mock[Feature]Mapper();
    repository = [Feature]RepositoryImpl(
      remoteDataSource: mockDataSource,
      mapper: mockMapper,
    );
  });

  group('get[Feature]', () {
    test('returns entity when datasource succeeds', () async {
      // Arrange
      when(mockDataSource.get[Feature](any))
          .thenAnswer((_) async => t[Feature]Model);
      when(mockMapper.toEntity(any)).thenReturn(t[Feature]Entity);
      // Act
      final result = await repository.get[Feature]('1');
      // Assert
      expect(result, Right(t[Feature]Entity));
    });

    test('returns ServerFailure when AppException thrown', () async {
      when(mockDataSource.get[Feature](any)).thenThrow(
        AppException.server(message: 'Not found', statusCode: 404),
      );
      final result = await repository.get[Feature]('1');
      expect(result.isLeft(), isTrue);
      result.fold((f) => expect(f, isA<ServerFailure>()), (_) => fail('Expected Left'));
    });

    test('returns unknownFailure for unexpected exception', () async {
      when(mockDataSource.get[Feature](any)).thenThrow(Exception('Crash'));
      final result = await repository.get[Feature]('1');
      expect(result.isLeft(), isTrue);
    });
  });
}
```

## Mapper Test Pattern (no mocks needed)

```dart
void main() {
  late [Feature]Mapper mapper;
  setUp(() => mapper = [Feature]Mapper());

  group('[Feature]Mapper', () {
    test('maps all fields correctly', () {
      final entity = mapper.toEntity(t[Feature]Model);
      expect(entity.id, t[Feature]Model.id);
      expect(entity.name, t[Feature]Model.name);
    });

    test('handles null fields with defaults', () {
      final entity = mapper.toEntity(const [Feature]Model());
      expect(entity.id, '');
      expect(entity.name, '');
    });
  });
}
```

Rules:
- Repository: three cases per method — success, `AppException`, unexpected `Exception`
- Mapper: two cases — all fields present, all fields null
- `AppException` caught → specific Failure subtype asserted
- Mapper tests need no mocks — instantiate directly

## Output

Confirm test file paths and list all test group + test names.
