# Flutter Qontak — Syntax Conventions

> `lib/core/reference/code-architecture/syntax-conventions-theory.md` for the design rationale.

Cross-cutting coding rules applied to every artifact, regardless of layer or package.

---

## Null Safety Extensions <!-- 31 -->

```dart
// shared/[prefix]_core/lib/src/utils/null_safety.dart
extension NullableStringX on String? {
  String orEmpty() => this ?? '';
  String orDefault(String fallback) =>
      (this == null || this!.trim().isEmpty) ? fallback : this!;
  bool get isNullOrEmpty => this == null || this!.isEmpty;
}

extension NullableNumX<T extends num> on T? {
  T orZero() => this ?? (0 as T);
  T orDefault(T fallback) => this ?? fallback;
}

extension NullableListX<T> on List<T>? {
  List<T> orEmpty() => this ?? [];
  bool get isNullOrEmpty => this == null || this!.isEmpty;
}

extension NullableBoolX on bool? {
  bool orFalse() => this ?? false;
  bool orTrue() => this ?? true;
}
```

Usage: `response.name.orEmpty()` not `response.name ?? ''` in feature code.

---

## Unlocalized Text Extension <!-- 16 -->

```dart
// shared/[prefix]_core/lib/src/utils/string_ext.dart
extension UnlocalizedString on String {
  String get unlocalized => this;
}

// Usage — marks intentionally untranslated strings
'Debug only'.unlocalized
```

Grep for `.unlocalized` to find all untranslated strings before a release.

---

## Code Style Rules <!-- 33 -->

```dart
// Trailing commas — always, for better diffs and auto-formatting
Widget build(BuildContext context) {
  return Column(
    children: [
      Text('Hello'),
      const SizedBox(height: 16),
    ], // ← trailing comma
  );
}

// Named parameters for anything beyond 2 positional args
void createMessage({
  required String content,
  required String conversationId,
  String? attachmentUrl,
}) {}

// const constructors wherever possible
const Text('Static label')
const SizedBox(height: 16)

// Never return raw exceptions from domain or data boundaries
// ❌
throw Exception('Something failed');
// ✅
return Left(Failure.serverFailure(message: 'Failed', developerMessage: '...'));
```

---

## Import Order <!-- 29 -->

```dart
// 1. Dart core
import 'dart:async';
import 'dart:convert';

// 2. Flutter
import 'package:flutter/material.dart';

// 3. Third-party packages (alphabetical)
import 'package:dio/dio.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:go_router/go_router.dart';
import 'package:injectable/injectable.dart';

// 4. Internal shared packages
import 'package:[prefix]_core/[prefix]_core.dart';
import 'package:[prefix]_dependencies/[prefix]_dependencies.dart';

// 5. Project imports within the same package (package: imports, not relative)
import 'package:[prefix]_inbox/src/domain/entities/conversation.dart';
```

**Rule:** Always use `package:` imports, never relative paths (`../`). This enforces clean boundaries between layers.

---

## Code Generation Commands <!-- 17 -->

```bash
# Per feature package
cd features/[prefix]_auth && dart run build_runner build --delete-conflicting-outputs

# Via melos (all packages)
melos run build_runner

# Watch mode (development)
dart run build_runner watch --delete-conflicting-outputs
```

Generated files: `*.freezed.dart`, `*.g.dart`, `injection.config.dart`, `*.mocks.dart`.

---

## analysis_options.yaml <!-- 26 -->

Apply to the root workspace AND every package:

```yaml
# analysis_options.yaml
include: linter-rules/analysis_options.yaml  # Mekari Linter (git submodule)

analyzer:
  exclude:
    - '**/*.g.dart'
    - '**/*.freezed.dart'
    - '**/*.mocks.dart'
    - '**/injection.config.dart'
    - '**/l10n/**'

linter:
  rules:
    - always_use_package_imports  # never relative imports
    - require_trailing_commas
    - prefer_single_quotes
    - avoid_print
```

---

## Naming Quick-Reference <!-- 18 -->

| Artifact | File name | Class name |
|---|---|---|
| Entity | `conversation.dart` | `Conversation` |
| API response DTO | `conversation_response.dart` | `ConversationResponse` |
| API request DTO | `send_message_request.dart` | `SendMessageRequest` |
| DB model | `conversation_db.dart` | `ConversationDb` |
| Mapper | `conversation_mapper.dart` | `ConversationMapper` |
| Repository interface | `conversation_repository.dart` | `ConversationRepository` |
| Repository impl | `conversation_repository_impl.dart` | `ConversationRepositoryImpl` |
| DataSource interface + impl | `conversation_remote_data_source.dart` | `ConversationRemoteDataSource` / `ConversationRemoteDataSourceImpl` |
| UseCase | `get_conversations.dart` | `GetConversations` |
| BLoC | `inbox_bloc.dart` | `InboxBloc` |
| Screen | `inbox_screen.dart` | `InboxScreen` |
| Module impl | `inbox_module.dart` | `InboxModule` |
| Module API abstract | `inbox_module_api.dart` | `InboxModuleApi` |
| Module API impl | `inbox_module_api_impl.dart` | `InboxModuleApiImpl` |
