# Flutter — Testing

> Concepts and invariants: `reference/code-architecture/testing-theory.md`. This file covers Dart syntax and Flutter-specific patterns.

`flutter_test` + `bloc_test` + `mockito`. Test every layer in isolation: BLoC, use case, repository, mapper.

---

## Dependencies <!-- 13 -->

```yaml
dev_dependencies:
  flutter_test:
    sdk: flutter
  bloc_test: ^9.1.0
  mockito: ^5.4.0
  build_runner: ^2.4.0
```

---

## Test Pyramid <!-- 29 -->

```
test/
├── features/
│   └── employee/
│       ├── data/
│       │   ├── datasources/
│       │   │   └── employee_remote_data_source_test.dart
│       │   ├── mappers/
│       │   │   └── employee_mapper_test.dart
│       │   └── repositories/
│       │       └── employee_repository_impl_test.dart
│       ├── domain/
│       │   └── usecases/
│       │       └── get_employee_usecase_test.dart
│       └── presentation/
│           └── blocs/
│               └── employee_bloc_test.dart
├── helpers/
│   ├── mocks/
│   │   └── employee_mocks.dart     ← @GenerateNiceMocks declarations
│   └── fixtures/
│       └── employee_fixture.json
└── test_helper.dart
```

---

## What to Test Per Layer <!-- 11 -->

| Layer | What to test | What NOT to test |
|---|---|---|
| Domain (UseCases) | Business rules, Either return values, edge cases | Internal use case implementation details |
| Data (Mappers, RepositoryImpl) | Model → entity field mapping; AppException → Failure mapping | HTTP stack, real server responses |
| Presentation (BLoC) | State sequence via `blocTest`; use case call counts | Widget rendering, layout |
| UI (widget tests) | State-to-widget binding; event dispatch on interaction | Business logic, mapping logic |

---

## Mock Generation <!-- 32 -->

Declare all mocks for a feature in one file:

```dart
// test/helpers/mocks/employee_mocks.dart
import 'package:mockito/annotations.dart';
import 'package:your_app/features/employee/domain/repositories/employee_repository.dart';
import 'package:your_app/features/employee/domain/usecases/get_employee_usecase.dart';
import 'package:your_app/features/employee/data/datasources/employee_remote_data_source.dart';
import 'package:your_app/features/employee/data/mappers/employee_mapper.dart';

@GenerateNiceMocks([
  MockSpec<EmployeeRepository>(),
  MockSpec<GetEmployeeUseCase>(),
  MockSpec<UpdateEmployeeUseCase>(),
  MockSpec<EmployeeRemoteDataSource>(),
  MockSpec<EmployeeMapper>(),
])
void main() {}
```

Run after adding annotations:

```bash
dart run build_runner build --delete-conflicting-outputs
```

Generated file: `employee_mocks.mocks.dart` — import this in tests.

---

## Presenter Tests <!-- 95 -->

Use `bloc_test` — never test BLoC state by calling `act` and inspecting `state` manually.

```dart
// test/features/employee/presentation/blocs/employee_bloc_test.dart
import 'package:bloc_test/bloc_test.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:fpdart/fpdart.dart';
import 'package:mockito/mockito.dart';
import 'package:your_app/features/employee/presentation/blocs/employee_bloc.dart';
import 'package:your_app/features/employee/presentation/blocs/employee_event.dart';
import 'package:your_app/features/employee/presentation/blocs/employee_state.dart';
import 'package:your_app/features/employee/presentation/states/view_data_state.dart';

import '../../../../helpers/mocks/employee_mocks.mocks.dart';
import '../../../../helpers/fixtures/employee_fixtures.dart';

void main() {
  late MockGetEmployeeUseCase mockGetUseCase;
  late MockUpdateEmployeeUseCase mockUpdateUseCase;
  late EmployeeBloc bloc;

  setUp(() {
    mockGetUseCase = MockGetEmployeeUseCase();
    mockUpdateUseCase = MockUpdateEmployeeUseCase();
    bloc = EmployeeBloc(
      getEmployeeUseCase: mockGetUseCase,
      updateEmployeeUseCase: mockUpdateUseCase,
    );
  });

  tearDown(() => bloc.close());

  group('EmployeeBloc', () {
    test('initial state is correct', () {
      expect(bloc.state.employeeState.isInitial, isTrue);
    });

    group('LoadEmployee', () {
      blocTest<EmployeeBloc, EmployeeState>(
        'emits [loading, loaded] when use case succeeds',
        setUp: () {
          when(mockGetUseCase.call(any)).thenAnswer(
            (_) async => Right(tEmployeeEntity),
          );
        },
        build: () => bloc,
        act: (b) => b.add(
          const EmployeeEvent.loadEmployee(employeeId: '1'),
        ),
        expect: () => [
          isA<EmployeeState>().having(
            (s) => s.employeeState.isLoading,
            'isLoading',
            isTrue,
          ),
          isA<EmployeeState>().having(
            (s) => s.employeeState.isLoaded,
            'isLoaded',
            isTrue,
          ),
        ],
        verify: (_) {
          verify(mockGetUseCase.call('1')).called(1);
        },
      );

      blocTest<EmployeeBloc, EmployeeState>(
        'emits [loading, error] when use case fails',
        setUp: () {
          when(mockGetUseCase.call(any)).thenAnswer(
            (_) async => Left(tServerFailure),
          );
        },
        build: () => bloc,
        act: (b) => b.add(
          const EmployeeEvent.loadEmployee(employeeId: '1'),
        ),
        expect: () => [
          predicate<EmployeeState>(
            (s) => s.employeeState.isLoading,
          ),
          predicate<EmployeeState>(
            (s) => s.employeeState.hasError,
          ),
        ],
      );
    });
  });
}
```

---

## Use Case Tests <!-- 54 -->

```dart
// test/features/employee/domain/usecases/get_employee_usecase_test.dart
import 'package:flutter_test/flutter_test.dart';
import 'package:fpdart/fpdart.dart';
import 'package:mockito/mockito.dart';

import '../../../../helpers/mocks/employee_mocks.mocks.dart';
import '../../../../helpers/fixtures/employee_fixtures.dart';

void main() {
  late MockEmployeeRepository mockRepository;
  late GetEmployeeUseCase useCase;

  setUp(() {
    mockRepository = MockEmployeeRepository();
    useCase = GetEmployeeUseCase(repository: mockRepository);
  });

  group('GetEmployeeUseCase', () {
    test('returns entity when repository succeeds', () async {
      // Arrange
      when(mockRepository.getEmployee(any)).thenAnswer(
        (_) async => Right(tEmployeeEntity),
      );

      // Act
      final result = await useCase('1');

      // Assert
      expect(result, Right(tEmployeeEntity));
      verify(mockRepository.getEmployee('1')).called(1);
      verifyNoMoreInteractions(mockRepository);
    });

    test('returns failure when repository fails', () async {
      // Arrange
      when(mockRepository.getEmployee(any)).thenAnswer(
        (_) async => Left(tServerFailure),
      );

      // Act
      final result = await useCase('1');

      // Assert
      expect(result.isLeft(), isTrue);
    });
  });
}
```

---

## Repository Tests <!-- 75 -->

```dart
// test/features/employee/data/repositories/employee_repository_impl_test.dart
import 'package:flutter_test/flutter_test.dart';
import 'package:fpdart/fpdart.dart';
import 'package:mockito/mockito.dart';

import '../../../../helpers/mocks/employee_mocks.mocks.dart';
import '../../../../helpers/fixtures/employee_fixtures.dart';

void main() {
  late MockEmployeeRemoteDataSource mockDataSource;
  late MockEmployeeMapper mockMapper;
  late EmployeeRepositoryImpl repository;

  setUp(() {
    mockDataSource = MockEmployeeRemoteDataSource();
    mockMapper = MockEmployeeMapper();
    repository = EmployeeRepositoryImpl(
      remoteDataSource: mockDataSource,
      mapper: mockMapper,
    );
  });

  group('getEmployee', () {
    test('returns entity when datasource succeeds', () async {
      // Arrange
      when(mockDataSource.getEmployee(any)).thenAnswer(
        (_) async => tEmployeeModel,
      );
      when(mockMapper.toEntity(any)).thenReturn(tEmployeeEntity);

      // Act
      final result = await repository.getEmployee('1');

      // Assert
      expect(result, Right(tEmployeeEntity));
      verify(mockDataSource.getEmployee('1')).called(1);
      verify(mockMapper.toEntity(tEmployeeModel)).called(1);
    });

    test('returns failure when datasource throws AppException', () async {
      // Arrange
      when(mockDataSource.getEmployee(any)).thenThrow(
        AppException.server(message: 'Not found', statusCode: 404),
      );

      // Act
      final result = await repository.getEmployee('1');

      // Assert
      expect(result.isLeft(), isTrue);
      result.fold(
        (failure) => expect(failure, isA<ServerFailure>()),
        (_) => fail('Expected Left'),
      );
    });

    test('returns unknownFailure for unexpected exceptions', () async {
      // Arrange
      when(mockDataSource.getEmployee(any)).thenThrow(Exception('Crash'));

      // Act
      final result = await repository.getEmployee('1');

      // Assert
      expect(result.isLeft(), isTrue);
    });
  });
}
```

---

## Mapper Tests <!-- 54 -->

Mapper tests are plain unit tests — no mocks needed.

```dart
// test/features/employee/data/mappers/employee_mapper_test.dart
import 'package:flutter_test/flutter_test.dart';

void main() {
  late EmployeeMapper mapper;

  setUp(() {
    mapper = EmployeeMapper();
  });

  group('EmployeeMapper', () {
    test('maps all fields correctly', () {
      // Arrange
      const model = EmployeeModel(
        id: '1',
        name: 'Alice',
        email: 'alice@example.com',
        joinDate: '2024-01-15T00:00:00Z',
      );

      // Act
      final entity = mapper.toEntity(model);

      // Assert
      expect(entity.id, '1');
      expect(entity.name, 'Alice');
      expect(entity.email, 'alice@example.com');
      expect(entity.joinDate, DateTime.utc(2024, 1, 15));
    });

    test('handles null fields with defaults', () {
      // Arrange
      const model = EmployeeModel();

      // Act
      final entity = mapper.toEntity(model);

      // Assert
      expect(entity.id, '');
      expect(entity.name, '');
      expect(entity.email, '');
      expect(entity.joinDate, isNull);
    });
  });
}
```

---

## Mock vs Real <!-- 14 -->

| Use a mock/stub when… | Use a real implementation when… |
|---|---|
| The dependency has I/O (network, HTTP) | The dependency is pure (Mapper, domain use case with no I/O) |
| The test must control exact return values | The test verifies full integration wiring |
| Unit test speed matters | Correctness of data transformation matters |

**Never mock Mappers** — they are pure functions. Instantiate them directly and test with real input/output.

Use `@GenerateNiceMocks` for interfaces (`EmployeeRepository`, `EmployeeRemoteDataSource`, `GetEmployeeUseCase`). Pass mocks directly via constructor injection — avoid `getIt` in tests.

---

## Test Fixtures <!-- 33 -->

Centralize test data — don't define inline in every test.

```dart
// test/helpers/fixtures/employee_fixtures.dart
import 'package:fpdart/fpdart.dart';
import 'package:your_app/features/employee/data/models/employee_model.dart';
import 'package:your_app/features/employee/domain/entities/employee_entity.dart';
import 'package:your_app/features/employee/domain/errors/failure.dart';

const tEmployeeModel = EmployeeModel(
  id: '1',
  name: 'Alice',
  email: 'alice@example.com',
  joinDate: '2024-01-15T00:00:00Z',
);

final tEmployeeEntity = EmployeeEntity(
  id: '1',
  name: 'Alice',
  email: 'alice@example.com',
  joinDate: DateTime.utc(2024, 1, 15),
);

final tServerFailure = Failure.serverFailure(
  message: 'Server error',
  developerMessage: 'HTTP 500',
);
```

---

## Best Practices <!-- 11 -->

1. **AAA** — Arrange, Act, Assert — one concept per test
2. **Describe intent** — `'emits [loading, loaded] when LoadEmployee succeeds'`
3. **Use `blocTest`** — never test BLoC by reading `.state` after `act`
4. **Use `predicate<T>`** — when you care about shape, not exact value
5. **Mock at the boundary** — datasource for repository tests, repository for use case tests
6. **Test both paths** — success and failure for every method
7. **Run build_runner** after adding `@GenerateNiceMocks`
8. **Fixture file** — one fixtures file per feature, reused across test files

## Test Naming Convention <!-- 14 -->

Pattern: `'[description of what is tested when condition]'` (plain English inside `blocTest` / `test()`)

For plain `test()` calls use the `given/when/then` or `returns X when Y` style:

Examples:

- `'returns entity when repository succeeds'`
- `'returns failure when repository fails'`
- `'emits [loading, loaded] when use case succeeds'`
- `'emits [loading, error] when use case fails'`
- `'maps all fields correctly'`
- `'handles null fields with defaults'`
