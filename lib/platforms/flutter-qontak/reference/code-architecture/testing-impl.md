# Flutter Qontak — Testing

> Concepts and invariants: `lib/core/reference/code-architecture/testing-theory.md`. This file covers Dart syntax and patterns for modular (melos) test setup.

`flutter_test` + `bloc_test` + `mockito`. Each feature package has its own `test/` directory and runs independently via melos.

---

## Test Structure per Package <!-- 28 -->

```
features/[prefix]_inbox/
└── test/
    ├── data/
    │   ├── datasources/
    │   │   └── inbox_remote_data_source_test.dart
    │   ├── mappers/
    │   │   └── conversation_mapper_test.dart
    │   └── repositories/
    │       └── inbox_repository_impl_test.dart
    ├── domain/
    │   └── usecases/
    │       └── get_inbox_test.dart
    ├── presentation/
    │   └── blocs/
    │       └── inbox_bloc_test.dart
    ├── helpers/
    │   ├── mocks/
    │   │   └── inbox_mocks.dart        ← @GenerateNiceMocks declarations
    │   └── fixtures/
    │       └── inbox_fixtures.dart
    └── test_helper.dart
```

---

## What to Test Per Layer <!-- 11 -->

| Layer | What to test | What NOT to test |
|---|---|---|
| Domain (UseCases) | Business rules, Either return values, edge cases | Internal use case implementation details |
| Data (Mappers, RepositoryImpl) | Model → entity field mapping; AppException → Failure mapping | HTTP stack, real server responses |
| Presentation (BLoC) | State sequence via `blocTest`; use case call counts | Widget rendering, layout |
| Module API (ModuleApiImpl) | Delegation to use cases; null/failure handling | Cross-module integration in production |

---

## Dev Dependencies (per feature package) <!-- 14 -->

```yaml
# features/[prefix]_inbox/pubspec.yaml
dev_dependencies:
  flutter_test:
    sdk: flutter
  bloc_test: ^9.1.7
  mockito: ^5.4.4
  build_runner: ^2.4.12
```

---

## Running Tests <!-- 18 -->

```bash
# All packages via melos
melos run test

# Single package
cd features/[prefix]_inbox && flutter test

# With coverage
cd features/[prefix]_inbox && flutter test --coverage

# Regenerate mocks after @GenerateNiceMocks changes
cd features/[prefix]_inbox && dart run build_runner build --delete-conflicting-outputs
```

---

## Mock Generation <!-- 24 -->

```dart
// test/helpers/mocks/inbox_mocks.dart
import 'package:mockito/annotations.dart';
import 'package:[prefix]_inbox/src/domain/repositories/inbox_repository.dart';
import 'package:[prefix]_inbox/src/domain/usecases/get_inbox.dart';
import 'package:[prefix]_inbox/src/data/datasources/inbox_remote_data_source.dart';
// Import Module API interfaces you need to mock
import 'package:[prefix]_core/[prefix]_core.dart';

@GenerateNiceMocks([
  MockSpec<InboxRepository>(),
  MockSpec<GetInbox>(),
  MockSpec<InboxRemoteDataSource>(),
  MockSpec<AuthModuleApi>(),         // ← mock cross-module APIs
])
void main() {}
```

Generated file: `inbox_mocks.mocks.dart`. Run `build_runner` after adding mocks.

---

## BLoC Tests <!-- 87 -->

```dart
// test/presentation/blocs/inbox_bloc_test.dart
import 'package:bloc_test/bloc_test.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:fpdart/fpdart.dart';
import 'package:mockito/mockito.dart';
import 'package:[prefix]_core/[prefix]_core.dart';
import 'package:[prefix]_inbox/src/presentation/blocs/inbox_bloc.dart';
import 'package:[prefix]_inbox/src/presentation/blocs/inbox_event.dart';
import 'package:[prefix]_inbox/src/presentation/blocs/inbox_state.dart';

import '../../helpers/mocks/inbox_mocks.mocks.dart';
import '../../helpers/fixtures/inbox_fixtures.dart';

void main() {
  late MockGetInbox mockGetInbox;
  late InboxBloc bloc;

  setUp(() {
    mockGetInbox = MockGetInbox();
    bloc = InboxBloc(mockGetInbox);
  });

  tearDown(() => bloc.close());

  group('InboxBloc', () {
    test('initial state is correct', () {
      expect(bloc.state.inboxState.isInitial, isTrue);
    });

    group('LoadInbox', () {
      blocTest<InboxBloc, InboxState>(
        'emits [loading, loaded] when use case returns conversations',
        setUp: () {
          when(mockGetInbox(any)).thenAnswer(
            (_) async => Right(tConversationList),
          );
        },
        build: () => bloc,
        act: (b) => b.add(const InboxEvent.loadInbox()),
        expect: () => [
          isA<InboxState>().having((s) => s.inboxState.isLoading, 'isLoading', isTrue),
          isA<InboxState>().having((s) => s.inboxState.isLoaded, 'isLoaded', isTrue),
        ],
        verify: (_) {
          verify(mockGetInbox(const NoParams())).called(1);
        },
      );

      blocTest<InboxBloc, InboxState>(
        'emits [loading, empty] when use case returns empty list',
        setUp: () {
          when(mockGetInbox(any)).thenAnswer(
            (_) async => const Right([]),
          );
        },
        build: () => bloc,
        act: (b) => b.add(const InboxEvent.loadInbox()),
        expect: () => [
          isA<InboxState>().having((s) => s.inboxState.isLoading, 'isLoading', isTrue),
          isA<InboxState>().having((s) => s.inboxState.isEmpty, 'isEmpty', isTrue),
        ],
      );

      blocTest<InboxBloc, InboxState>(
        'emits [loading, error] when use case fails',
        setUp: () {
          when(mockGetInbox(any)).thenAnswer(
            (_) async => Left(tServerFailure),
          );
        },
        build: () => bloc,
        act: (b) => b.add(const InboxEvent.loadInbox()),
        expect: () => [
          predicate<InboxState>((s) => s.inboxState.isLoading),
          predicate<InboxState>((s) => s.inboxState.hasError),
        ],
      );
    });
  });
}
```

---

## Use Case Tests <!-- 39 -->

```dart
void main() {
  late MockInboxRepository mockRepository;
  late GetInbox useCase;

  setUp(() {
    mockRepository = MockInboxRepository();
    useCase = GetInbox(mockRepository);
  });

  group('GetInbox', () {
    test('returns conversation list when repository succeeds', () async {
      when(mockRepository.getInbox()).thenAnswer(
        (_) async => Right(tConversationList),
      );

      final result = await useCase(const NoParams());

      expect(result, Right(tConversationList));
      verify(mockRepository.getInbox()).called(1);
      verifyNoMoreInteractions(mockRepository);
    });

    test('returns failure when repository fails', () async {
      when(mockRepository.getInbox()).thenAnswer(
        (_) async => Left(tServerFailure),
      );

      final result = await useCase(const NoParams());
      expect(result.isLeft(), isTrue);
    });
  });
}
```

---

## Mapper Tests <!-- 33 -->

No mocks needed — pure function tests:

```dart
void main() {
  group('ConversationMapper', () {
    test('fromResponseToEntity maps all fields', () {
      const response = ConversationResponse(
        id: 'c1',
        title: 'Test Chat',
        unreadCount: 3,
      );

      final entity = ConversationMapper.fromResponseToEntity(response);

      expect(entity.id, 'c1');
      expect(entity.title, 'Test Chat');
      expect(entity.unreadCount, 3);
    });

    test('handles null fields with defaults', () {
      const response = ConversationResponse();
      final entity = ConversationMapper.fromResponseToEntity(response);
      expect(entity.id, '');
      expect(entity.unreadCount, 0);
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

**Never mock Mappers** — they are pure functions. Instantiate directly and test with real input/output.

Use `@GenerateNiceMocks` for interfaces (`InboxRepository`, `InboxRemoteDataSource`, cross-module APIs like `AuthModuleApi`). Pass mocks directly via constructor injection — avoid `getIt` in tests.

---

## Test Fixtures <!-- 24 -->

```dart
// test/helpers/fixtures/inbox_fixtures.dart
import 'package:[prefix]_core/[prefix]_core.dart';
import 'package:[prefix]_inbox/src/domain/entities/conversation.dart';

final tConversation = Conversation(
  id: 'c1',
  title: 'Support Chat',
  unreadCount: 2,
  lastMessageAt: DateTime.utc(2026, 1, 15),
);

final tConversationList = [tConversation];

final tServerFailure = Failure.serverFailure(
  message: 'Server error',
  developerMessage: 'HTTP 500',
);
```

---

## Testing Module API Implementations <!-- 33 -->

```dart
// Test that AuthModuleApiImpl correctly delegates to domain use cases
void main() {
  late MockGetCurrentUser mockGetCurrentUser;
  late AuthModuleApiImpl api;

  setUp(() {
    mockGetCurrentUser = MockGetCurrentUser();
    api = AuthModuleApiImpl(mockGetCurrentUser);
  });

  test('getUserId returns id when authenticated', () async {
    when(mockGetCurrentUser(any)).thenAnswer(
      (_) async => Right(tCurrentUser),
    );

    final id = await api.getUserId();
    expect(id, tCurrentUser.id);
  });

  test('getUserId returns null when not authenticated', () async {
    when(mockGetCurrentUser(any)).thenAnswer(
      (_) async => Left(tServerFailure),
    );

    final id = await api.getUserId();
    expect(id, isNull);
  });
}
```

## Test Naming Convention <!-- 14 -->

Pattern: `'[returns/emits/calls] [expected] when [condition]'` (plain English inside `blocTest` / `test()`)

Examples:

- `'returns conversation list when repository succeeds'`
- `'returns failure when repository fails'`
- `'emits [loading, loaded] when use case returns conversations'`
- `'emits [loading, empty] when use case returns empty list'`
- `'emits [loading, error] when use case fails'`
- `'fromResponseToEntity maps all fields'`
- `'handles null fields with defaults'`
- `'getUserId returns id when authenticated'`
