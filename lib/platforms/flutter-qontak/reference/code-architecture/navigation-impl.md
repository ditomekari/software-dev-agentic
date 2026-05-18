# Flutter Qontak — Navigation (go_router + Modular)

> Canonical terms: `lib/core/reference/code-architecture/ui-theory.md` — `## Navigator / Coordinator` section.

Navigation is modular: each feature module declares its own routes via `BaseModule.routes()`. The application module aggregates via `ModuleRegistrar`. Cross-module navigation uses the Module API pattern, never direct imports.

---

## Route Constants (per module) <!-- 18 -->

```dart
// features/[prefix]_inbox/lib/src/configs/inbox_routes.dart
abstract class InboxRoutes {
  InboxRoutes._();

  static const String inbox = '/inbox';
  static const String conversation = '/inbox/:conversationId';

  static String conversationPath(String id) => '/inbox/$id';
}
```

Export from the feature's barrel file so the app module can use named routes without importing internal paths.

---

## BaseModule Routes Implementation <!-- 32 -->

```dart
// features/[prefix]_inbox/lib/src/configs/inbox_module.dart
import 'package:[prefix]_core/[prefix]_core.dart';
import '../presentation/screens/inbox_screen.dart';
import '../presentation/screens/conversation_screen.dart';
import 'inbox_routes.dart';

class InboxModule implements BaseModule {
  @override
  List<RouteBase> routes() => [
        GoRoute(
          path: InboxRoutes.inbox,
          name: 'inbox',
          builder: (context, state) => const InboxScreen(),
          routes: [
            GoRoute(
              path: ':conversationId',
              name: 'conversation',
              builder: (context, state) => ConversationScreen(
                conversationId: state.pathParameters['conversationId']!,
              ),
            ),
          ],
        ),
      ];
}
```

---

## Cross-Module Navigation API <!-- 49 -->

Feature modules must not import each other. For navigation to another feature, define an abstract navigation API in `[prefix]_core` and implement it in the owning feature.

```dart
// shared/[prefix]_core/lib/src/module_api/inbox_navigation_api.dart
abstract class InboxNavigationApi {
  void goToInbox(BuildContext context);
  void goToConversation(BuildContext context, String conversationId);
}
```

```dart
// features/[prefix]_inbox/lib/src/module_api/inbox_navigation_api_impl.dart
import 'package:go_router/go_router.dart';
import 'package:injectable/injectable.dart';
import 'package:[prefix]_core/[prefix]_core.dart';
import '../configs/inbox_routes.dart';

@LazySingleton(as: InboxNavigationApi)
class InboxNavigationApiImpl implements InboxNavigationApi {
  @override
  void goToInbox(BuildContext context) =>
      context.goNamed('inbox');

  @override
  void goToConversation(BuildContext context, String conversationId) =>
      context.goNamed('conversation',
          pathParameters: {'conversationId': conversationId});
}
```

Any feature injects `InboxNavigationApi` — no direct dependency on `[prefix]_inbox`:

```dart
@injectable
class NotificationBloc extends Bloc<NotificationEvent, NotificationState> {
  NotificationBloc(this._inboxNav);
  final InboxNavigationApi _inboxNav;

  // When a notification is tapped
  void _onNotificationTapped(NotificationTapped event, Emitter emit) {
    _inboxNav.goToConversation(event.context, event.conversationId);
  }
}
```

---

## Navigating from Widgets <!-- 21 -->

```dart
// Push a new screen
context.push(InboxRoutes.conversationPath(id));

// Replace current screen (no back)
context.go(InboxRoutes.inbox);

// Pop
context.pop();

// Pop with result
context.pop(selectedItem);

// Named navigation
context.goNamed('conversation', pathParameters: {'conversationId': id});
```

---

## Navigating from BLoC (Side Effects) <!-- 38 -->

BLoC emits a navigation intent via state; the screen listens and calls `context.go/push`:

```dart
// In BLoC state — add a nav action field
@freezed
class InboxState with _$InboxState {
  const factory InboxState({
    required ViewDataState<List<Conversation>> inboxState,
    @Default(null) InboxNavAction? navAction,
  }) = _InboxState;
}

sealed class InboxNavAction {
  const factory InboxNavAction.openConversation(String id) = OpenConversation;
}
```

```dart
// In Screen — BlocListener handles navigation
BlocListener<InboxBloc, InboxState>(
  listenWhen: (prev, curr) => prev.navAction != curr.navAction,
  listener: (context, state) {
    final action = state.navAction;
    if (action == null) return;
    switch (action) {
      case OpenConversation(:final id):
        context.goNamed('conversation', pathParameters: {'conversationId': id});
    }
    context.read<InboxBloc>().add(const InboxEvent.clearNavAction());
  },
  child: ...,
)
```

---

## Auth Guard <!-- 18 -->

Global redirect in `ModuleRegistrar.router`:

```dart
static String? _globalGuard(BuildContext context, GoRouterState state) {
  final isAuthenticated = getIt<AuthSessionService>().isAuthenticated;
  final isPublicRoute = _publicRoutes.contains(state.matchedLocation);
  if (!isAuthenticated && !isPublicRoute) return '/login';
  if (isAuthenticated && state.matchedLocation == '/login') return '/inbox';
  return null;
}

static const _publicRoutes = {'/login', '/forgot-password', '/onboarding'};
```

---

## Deep Links <!-- 16 -->

```xml
<!-- android/app/src/main/AndroidManifest.xml -->
<intent-filter android:autoVerify="true">
  <action android:name="android.intent.action.VIEW" />
  <category android:name="android.intent.category.DEFAULT" />
  <category android:name="android.intent.category.BROWSABLE" />
  <data android:scheme="https" android:host="chat.qontak.com" />
</intent-filter>
```

GoRouter handles deep links automatically when paths match route definitions. No additional Dart config needed.

---

## Nested Navigation (Bottom Nav) <!-- 14 -->

```dart
ShellRoute(
  builder: (context, state, child) => MainScaffold(child: child),
  routes: [
    GoRoute(path: '/inbox', builder: (_, __) => const InboxScreen()),
    GoRoute(path: '/contacts', builder: (_, __) => const ContactsScreen()),
    GoRoute(path: '/profile', builder: (_, __) => const ProfileScreen()),
  ],
)
```

`ShellRoute` keeps the `MainScaffold` (bottom nav bar) alive while navigating between tabs.
