# Flutter Qontak — Navigation (Navigator 1.0 + Centralized RouteManager)

> Canonical terms: `lib/core/reference/code-architecture/ui-theory.md` — `## Navigator / Coordinator` section.

Navigation uses Flutter's `Navigator` 1.0 API with `MaterialPageRoute`. All routes are registered in a single `AppRouteManger` class in `lib/route_manager.dart`. There is no `go_router`.

---

## Route Constants <!-- 12 -->

All route name constants live in `QontakAppRoute` (in `lib/config/constants/`):

```dart
// Route names are string constants accessed via QontakAppRoute.[name]
// Examples found in route_manager.dart:
QontakAppRoute.splash       // → SplashScreen (default)
QontakAppRoute.login        // → LoginScreen (with LoginBloc)
QontakAppRoute.main         // → MainPage (with SignOutBloc + NavBarBloc)
QontakAppRoute.chatRoom     // → ChatRoomPage
QontakAppRoute.emailRoom    // → EmailRoomScreen
QontakAppRoute.inbox        // → InboxScreen
QontakAppRoute.contactDetail
QontakAppRoute.walkthrough  // → OnBoardingScreen
// ... all routes declared as static const String
```

---

## AppRouteManger (Centralized Router) <!-- 38 -->

A single `AppRouteManger` extends `RouteManager` (from `chat_core`) and handles ALL route resolution. `BlocProvider` wiring for route-scoped BLoCs lives here, not inside screen widgets.

```dart
// lib/route_manager.dart
class AppRouteManger extends RouteManager {
  @override
  Widget getRoute(String? name, Object? arguments) {
    switch (name) {
      case QontakAppRoute.login:
        return BlocProvider(
          create: (_) => LoginBloc(
            getSSOTokenUseCase: mainDependency(),
            prefHelper: coreDependency(),
          ),
          child: const LoginScreen(),
        );

      case QontakAppRoute.main:
        return MultiBlocProvider(
          providers: [
            BlocProvider(create: (_) => SignOutBloc(
              qontakMonitor: coreDependency(),
              userSignOut: coreDependency(),
            )),
            BlocProvider(create: (_) => NavBarBloc()),
          ],
          child: const MainPage(),
        );

      case QontakAppRoute.chatRoom:
        return ChatRoomPage(
          arguments: arguments! as ChatRoomArguments,
        );

      case QontakAppRoute.contactDetail:
        final args = arguments! as ContactDetailArguments;
        return MultiBlocProvider(
          providers: [
            BlocProvider(create: (_) => DetailContactBloc(
              getContactByIdUseCase: contactDependency(),
              getContactByIdLocalUseCase: contactDependency(),
              editContactLocalUseCase: contactDependency(),
              qontakMonitor: coreDependency(),
              offlineMode: coreDependency(),
            )),
            BlocProvider(create: (_) => messagingDependency<GetRoomBloc>()),
          ],
          child: ContactDetailScreen(arguments: args, profileSection: ...),
        );

      case QontakAppRoute.splash:
      default:
        return const SplashScreen();
    }
  }

  @override
  Route? onGenerateRoute(RouteSettings settings) {
    final child = getRoute(settings.name, settings.arguments);
    return MaterialPageRoute(builder: (_) => child, settings: settings);
  }
}
```

**Rules:**
- `BlocProvider` for route-scoped BLoCs goes inside the `case` block, NOT inside the Screen widget.
- Screens that need arguments receive a typed `*Arguments` object via `arguments! as XArguments`.
- The `default` case always returns `SplashScreen`.

---

## Navigating from Widgets/Services <!-- 22 -->

Navigation uses `NavigationHelper` (from `chat_core`) which wraps the global `navigatorKey`:

```dart
// Push a named route with arguments
navigationHelper.pushNamed(
  QontakAppRoute.chatRoom,
  arguments: ChatRoomArguments(room: room, isFromNotification: true),
);

// Replace current stack
navigationHelper.pushReplacementNamed(QontakAppRoute.main);

// Pop
Navigator.of(context).pop();

// From App widget (notification-driven navigation)
final NavigationHelper navigationHelper = coreDependency<NavigationHelper>();
navigationHelper.pushNamed(QontakAppRoute.emailRoom, arguments: EmailRoomArguments(...));
```

The global `navigatorKey` (`NavigationHelperImpl.navigatorKey`) is passed to `MaterialApp.navigatorKey` so `NavigationHelper` can navigate without a `BuildContext`.

---

## Navigating from BLoC (Side Effects) <!-- 20 -->

BLoC state drives navigation via `BlocListener` in the screen. The BLoC never touches `NavigationHelper` directly.

```dart
// In Screen — BlocListener handles navigation side effects
BlocListener<LoginBloc, LoginState>(
  listenWhen: (prev, curr) => prev.loginState != curr.loginState,
  listener: (context, state) {
    if (state.loginState.status.isHasData) {
      Navigator.of(context).pushReplacementNamed(QontakAppRoute.main);
    } else if (state.loginState.status.isError) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(state.loginState.message ?? 'Login failed')),
      );
    }
  },
  child: ...,
)
```

---

## Arguments Pattern <!-- 16 -->

Each route that needs data defines a typed `*Arguments` class (in the feature package):

```dart
// Defined in the feature package (e.g. chat_inbox)
class ChatRoomArguments {
  const ChatRoomArguments({
    required this.room,
    this.isFromNotification = false,
  });
  final Room room;
  final bool isFromNotification;
}

// Used in route_manager.dart
case QontakAppRoute.chatRoom:
  return ChatRoomPage(
    arguments: arguments! as ChatRoomArguments,
  );
```

---

## Nested Navigation (Bottom Nav) <!-- 12 -->

Bottom navigation is managed by `NavBarBloc` (app-level, in `MainPage`). Tab switching does NOT use nested navigators — it uses indexed widget switching driven by BLoC state.

```dart
// lib/presentation/screens/main_page.dart
// NavBarBloc.navBarIndex drives which tab widget is shown
BlocBuilder<NavBarBloc, NavBarState>(
  builder: (context, state) {
    final index = state.navBarIndex.data ?? 0;
    return IndexedStack(
      index: index,
      children: [...tabScreens],
    );
  },
)
```

---

## Notification-Driven Navigation <!-- 14 -->

The `App` widget's `build` method wraps the `MaterialApp` builder with a `BlocListener<NotificationBloc>` to handle push notification taps at the app level:

```dart
// lib/app.dart
builder: (context, child) {
  return BlocListener<NotificationBloc, NotificationState>(
    listener: (context, state) {
      final rn = state.roomOpenedState?.data;
      if (rn == null) return;
      final room = RoomMapper.fromNotification(notification: rn);
      if (rn.channel == ChannelType.email.channelType) {
        navigationHelper.pushNamed(QontakAppRoute.emailRoom,
            arguments: EmailRoomArguments(room: room, isFromNotification: true));
      } else {
        navigationHelper.pushNamed(QontakAppRoute.chatRoom,
            arguments: ChatRoomArguments(room: room, isFromNotification: true));
      }
    },
    child: SafeArea(top: false, bottom: Platform.isAndroid, child: child!),
  );
},
```
