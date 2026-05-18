---
name: builder-test-create-mock
description: Scaffold a @GenerateNiceMocks declaration file for a Flutter Qontak feature package using mockito. Called by builder-test-* skills.
user-invocable: false
tools: Read, Write, Glob, Grep
---

Create or update the mock declaration file for a feature package using `mockito`'s `@GenerateNiceMocks`.

## Steps

1. **Glob** for `test/helpers/mocks/[feature]_mocks.dart` in the feature package
2. If it exists — **Read** it, then **Edit** to append missing `MockSpec<>` entries
3. If it does not exist — **Create** it with the pattern below
4. List the interfaces/classes to mock — caller provides this list

## Mock File Pattern

```dart
// features/[prefix]_[feature]/test/helpers/mocks/[feature]_mocks.dart
import 'package:mockito/annotations.dart';
// Import each class/interface to be mocked
import 'package:[prefix]_[feature]/src/domain/repositories/[feature]_repository.dart';
import 'package:[prefix]_[feature]/src/domain/usecases/get_[concept].dart';
import 'package:[prefix]_[feature]/src/data/datasources/[feature]_remote_data_source.dart';
// Cross-module module APIs
import 'package:[prefix]_core/[prefix]_core.dart';

@GenerateNiceMocks([
  MockSpec<[Feature]Repository>(),
  MockSpec<Get[Concept]>(),           // verb-only use case name
  MockSpec<[Feature]RemoteDataSource>(),
  // MockSpec<AuthModuleApi>(),       // add cross-module API mocks as needed
])
void main() {}
```

## After Creation

Tell the caller to run:

```bash
cd features/[prefix]_[feature] && dart run build_runner build --delete-conflicting-outputs
```

This generates `[feature]_mocks.mocks.dart` alongside the declaration file.

## Rules

- One `*_mocks.dart` file per feature package — append to it, never create duplicates
- `@GenerateNiceMocks` — never `@GenerateMocks`; nice mocks return sensible defaults without explicit stubs
- Mock interfaces and abstract classes — never mock concrete implementations or Mappers
- Use case class names follow verb-only convention (`GetInbox`, not `GetInboxUseCase`) — match exactly to the source file
- Generated file (`*.mocks.dart`) is excluded from lint via `analysis_options.yaml` — never edit it manually

## Output

Confirm mock file path, list all `MockSpec<>` entries added, and remind the caller to run `build_runner`.
