# Flutter Qontak CRM — Testing

> Concepts and invariants: `lib/core/reference/code-architecture/testing-theory.md`. This file covers Dart syntax and patterns for the CRM monorepo.

`flutter_test` + `bloc_test` + `mockito`. Each feature package has its own `test/` directory and runs independently via melos.

---

## Test Structure per Package <!-- 18 -->

```
features/crm_company/
└── test/
    ├── data/
    │   ├── datasources/
    │   │   └── company_remote_data_source_test.dart
    │   ├── mappers/
    │   │   └── company_mapper_test.dart
    │   └── repositories/
    │       └── company_repository_impl_test.dart
    ├── domain/
    │   └── usecases/
    │       └── get_company_usecase_test.dart
    ├── presentation/
    │   └── blocs/
    │       └── company_bloc_test.dart
    ├── helpers/
    │   ├── mocks/
    │   │   └── company_mocks.dart        ← @GenerateNiceMocks declarations
    │   └── fixtures/
    │       └── company_fixtures.dart
    └── test_helper.dart
```

---

## Dev Dependencies (per feature package) <!-- 10 -->

```yaml
# features/crm_company/pubspec.yaml
dev_dependencies:
  flutter_test:
    sdk: flutter
  bloc_test: ^9.1.7
  mockito: ^5.4.4
  build_runner: ^2.4.12
```

---

## Running Tests <!-- 12 -->

```bash
# All packages via melos
melos run test

# Single package
cd features/crm_company && flutter test

# With coverage
cd features/crm_company && flutter test --coverage

# Regenerate mocks after @GenerateNiceMocks changes
cd features/crm_company && dart run build_runner build --delete-conflicting-outputs
```

---

## Mock Generation <!-- 20 -->

```dart
// features/crm_company/test/helpers/mocks/company_mocks.dart
import 'package:mockito/annotations.dart';
import 'package:crm_company/src/domain/repositories/company_repository.dart';
import 'package:crm_company/src/domain/usecases/get_company_usecase.dart';   // WITH UseCase suffix
import 'package:crm_company/src/domain/usecases/add_company_usecase.dart';
import 'package:crm_company/src/data/data_sources/remote/company_remote_data_source.dart';

@GenerateNiceMocks([
  MockSpec<CompanyRepository>(),
  MockSpec<GetCompanyUseCase>(),           // UseCase suffix — matches CRM naming convention
  MockSpec<AddCompanyUseCase>(),
  MockSpec<CompanyRemoteDataSource>(),
])
void main() {}
```

Generated file: `company_mocks.mocks.dart`. Run `build_runner` after adding mocks.

**Rules:**
- One `*_mocks.dart` per feature package — append to it, never create duplicates
- `@GenerateNiceMocks` — never `@GenerateMocks`
- Mock interfaces and abstract classes — never mock concrete implementations or Mappers
- Use case class names follow CRM convention: `<Verb><Entity>UseCase` WITH suffix

---

## BLoC Tests <!-- 40 -->

```dart
// features/crm_company/test/presentation/blocs/company_bloc_test.dart
import 'package:bloc_test/bloc_test.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:fpdart/fpdart.dart';
import 'package:mockito/mockito.dart';
import 'package:qontak_common/qontak_common.dart';
import 'package:crm_company/src/presentation/bloc/company/company_bloc.dart';

import '../../helpers/mocks/company_mocks.mocks.dart';
import '../../helpers/fixtures/company_fixtures.dart';

void main() {
  late MockGetCompanyListUseCase mockGetCompanyListUseCase;
  late CompanyBloc bloc;

  setUp(() {
    mockGetCompanyListUseCase = MockGetCompanyListUseCase();
    bloc = CompanyBloc(
      getCompanyListUseCase: mockGetCompanyListUseCase, // named param
    );
  });

  tearDown(() => bloc.close());

  group('CompanyBloc', () {
    test('initial state is correct', () {
      expect(bloc.state.companyListState.status.isInitial, isTrue);
    });

    group('LoadRemoteCompany', () {
      blocTest<CompanyBloc, CompanyState>(
        'emits [loading, loaded] when use case succeeds',
        setUp: () {
          when(mockGetCompanyListUseCase.call(any))
              .thenAnswer((_) async => Right(tCompanyList));
        },
        build: () => bloc,
        act: (b) => b.add(const CompanyEvent.loadRemoteCompany()),
        expect: () => [
          predicate<CompanyState>(
            (s) => s.companyListState.status.isLoading,
            'companyListState is loading',
          ),
          predicate<CompanyState>(
            (s) => s.companyListState.status.isHasData,
            'companyListState has data',
          ),
        ],
        verify: (_) => verify(mockGetCompanyListUseCase.call(any)).called(1),
      );

      blocTest<CompanyBloc, CompanyState>(
        'emits [loading, error] when use case fails',
        setUp: () {
          when(mockGetCompanyListUseCase.call(any))
              .thenAnswer((_) async => Left(tServerFailure));
        },
        build: () => bloc,
        act: (b) => b.add(const CompanyEvent.loadRemoteCompany()),
        expect: () => [
          predicate<CompanyState>(
            (s) => s.companyListState.status.isLoading,
            'companyListState is loading',
          ),
          predicate<CompanyState>(
            (s) => s.companyListState.status.isError,
            'companyListState is error',
          ),
        ],
      );
    });
  });
}
```

**BLoC test rules:**
- Always `blocTest` — never test by calling `bloc.add()` then reading `.state`
- `tearDown` always calls `bloc.close()`
- BLoC constructor uses **named params**: `CompanyBloc(getCompanyListUseCase: mock...)`
- Use `predicate<State>()` with `.status.isHasData` and `.status.isError` — NOT `.isLoaded` or `.hasError`
- Success path + failure path per event — minimum two tests per event
- Initial state test verifies `.status.isInitial` on all state fields

---

## Use Case Tests <!-- 25 -->

```dart
void main() {
  late MockCompanyRepository mockRepository;
  late GetCompanyUseCase useCase;

  setUp(() {
    mockRepository = MockCompanyRepository();
    useCase = GetCompanyUseCase(repository: mockRepository);
  });

  group('GetCompanyUseCase', () {
    test('returns entity when repository succeeds', () async {
      // Arrange
      when(mockRepository.getCompany(any))
          .thenAnswer((_) async => Right(tCompany));
      // Act
      final result = await useCase(GetCompanyParams(id: 'id-1'));
      // Assert
      expect(result, Right(tCompany));
      verify(mockRepository.getCompany('id-1')).called(1);
      verifyNoMoreInteractions(mockRepository);
    });

    test('returns failure when repository fails', () async {
      // Arrange
      when(mockRepository.getCompany(any))
          .thenAnswer((_) async => Left(tServerFailure));
      // Act
      final result = await useCase(GetCompanyParams(id: 'id-1'));
      // Assert
      expect(result.isLeft(), isTrue);
    });
  });
}
```

---

## Mapper Tests <!-- 18 -->

No mocks needed — pure function tests:

```dart
void main() {
  group('CompanyMapper', () {
    test('fromResponseToEntity maps all fields', () {
      const response = CompanyResponse(
        id: 'id-1',
        name: 'PT Mekari',
        phone: '+62123',
        createdAt: '2026-01-15T00:00:00Z',
      );

      final entity = CompanyMapper.fromResponseToEntity(response);

      expect(entity.id, 'id-1');
      expect(entity.name, 'PT Mekari');
      expect(entity.phone, '+62123');
      expect(entity.createdAt, isNotNull);
    });

    test('handles null fields with defaults', () {
      const response = CompanyResponse();
      final entity = CompanyMapper.fromResponseToEntity(response);
      expect(entity.id, '');
      expect(entity.name, '');
      expect(entity.phone, isNull);
    });
  });
}
```

**Never mock Mappers** — they are pure static functions. Instantiate directly with real input/output.

---

## Test Fixtures <!-- 12 -->

```dart
// features/crm_company/test/helpers/fixtures/company_fixtures.dart
import 'package:qontak_common/qontak_common.dart';
import 'package:crm_company/src/domain/entities/company.dart';

final tCompany = Company(
  id: 'id-1',
  name: 'PT Mekari',
  phone: '+62123',
);

final tCompanyList = [tCompany];

final tServerFailure = Failure(message: 'Server error');
```

---

## Test Naming Convention <!-- 8 -->

Pattern: `'[returns/emits/calls] [expected] when [condition]'`

- `'returns entity when repository succeeds'`
- `'returns failure when repository fails'`
- `'emits [loading, loaded] when use case succeeds'`
- `'emits [loading, error] when use case fails'`
- `'fromResponseToEntity maps all fields'`
- `'handles null fields with defaults'`
