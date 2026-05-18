# Flutter Qontak — Core Services & Utilities

> `lib/core/reference/code-architecture/utilities-theory.md` for design rationale.

Shared infrastructure lives in `shared/[prefix]_core/lib/src/`. Interface-based for testability. Register all via `get_it` + `injectable`.

---

## Logger <!-- 46 -->

```dart
// shared/[prefix]_core/lib/src/logging/app_logger.dart
abstract class AppLogger {
  void debug(String message, {Object? error, StackTrace? stackTrace});
  void info(String message, {Object? error, StackTrace? stackTrace});
  void warning(String message, {Object? error, StackTrace? stackTrace});
  void error(String message, {Object? error, StackTrace? stackTrace});
}

@LazySingleton(as: AppLogger)
class AppLoggerImpl implements AppLogger {
  final Logger _logger = Logger(
    printer: PrettyPrinter(
      methodCount: 2,
      errorMethodCount: 8,
      lineLength: 120,
      colors: true,
      printEmojis: false,
    ),
    level: kReleaseMode ? Level.warning : Level.debug,
  );

  @override
  void debug(String message, {Object? error, StackTrace? stackTrace}) =>
      _logger.d(message, error: error, stackTrace: stackTrace);

  @override
  void info(String message, {Object? error, StackTrace? stackTrace}) =>
      _logger.i(message, error: error, stackTrace: stackTrace);

  @override
  void warning(String message, {Object? error, StackTrace? stackTrace}) =>
      _logger.w(message, error: error, stackTrace: stackTrace);

  @override
  void error(String message, {Object? error, StackTrace? stackTrace}) =>
      _logger.e(message, error: error, stackTrace: stackTrace);
}
```

Inject `AppLogger` into repositories and services — never call `print` or `debugPrint` directly in feature code.

---

## HTTP Client (Mekari Network) <!-- 24 -->

Networking in `[prefix]_core`. Uses Mekari Network (internal, wraps Dio):

```dart
// shared/[prefix]_core/lib/src/network/network_module.dart
@module
abstract class NetworkModule {
  @lazySingleton
  Dio get dio => MekariNetwork.createDio(
        baseUrl: AppEnv.apiBaseUrl,
        interceptors: [
          AuthInterceptor(),
          ErrorInterceptor(),
          LoggingInterceptor(),
        ],
      );
}
```

Feature packages inject `Dio` directly — they never create their own `Dio` instance.

---

## StorageService <!-- 62 -->

```dart
// shared/[prefix]_core/lib/src/storage/storage_service.dart
abstract class StorageService {
  Future<void> set<T>(StorageKey key, T value);
  Future<T?> get<T>(StorageKey key);
  Future<void> remove(StorageKey key);
  Future<void> clearAll();
  Future<bool> contains(StorageKey key);
}

enum StorageKey {
  accessToken,
  refreshToken,
  userId,
  userEmail,
  onboardingCompleted,
  lastSelectedTab,
}
```

```dart
@LazySingleton(as: StorageService)
class SharedPreferencesStorageService implements StorageService {
  SharedPreferencesStorageService(this._prefs);
  final SharedPreferences _prefs;

  @override
  Future<void> set<T>(StorageKey key, T value) async {
    final k = key.name;
    if (value is String) await _prefs.setString(k, value);
    else if (value is int) await _prefs.setInt(k, value);
    else if (value is bool) await _prefs.setBool(k, value);
    else await _prefs.setString(k, jsonEncode(value));
  }

  @override
  Future<T?> get<T>(StorageKey key) async {
    final k = key.name;
    if (T == String) return _prefs.getString(k) as T?;
    if (T == int) return _prefs.getInt(k) as T?;
    if (T == bool) return _prefs.getBool(k) as T?;
    final raw = _prefs.getString(k);
    return raw != null ? jsonDecode(raw) as T? : null;
  }

  @override
  Future<void> remove(StorageKey key) => _prefs.remove(key.name);

  @override
  Future<void> clearAll() async {
    for (final key in StorageKey.values) await remove(key);
  }

  @override
  Future<bool> contains(StorageKey key) async => _prefs.containsKey(key.name);
}
```

---

## DateService <!-- 70 -->

```dart
// shared/[prefix]_core/lib/src/date/date_service.dart
abstract class DateService {
  DateTime get now;
  String format(DateTime date, DateFormatStyle style, {String locale});
  DateTime? parse(String value, DateFormatStyle style);
  bool isSameDay(DateTime a, DateTime b);
  bool isToday(DateTime date);
  int daysBetween(DateTime start, DateTime end);
}

enum DateFormatStyle {
  iso8601,        // "2024-01-15T14:30:00Z"
  apiDate,        // "2024-01-15"
  displayDate,    // "Jan 15, 2024"
  displayDateTime,// "Jan 15, 2024, 2:30 PM"
  displayTime,    // "2:30 PM"
  relative,       // "2 days ago"
}

@LazySingleton(as: DateService)
class DateServiceImpl implements DateService {
  @override
  DateTime get now => DateTime.now();

  @override
  String format(DateTime date, DateFormatStyle style, {String locale = 'en_US'}) =>
      switch (style) {
        DateFormatStyle.iso8601 => date.toIso8601String(),
        DateFormatStyle.apiDate => DateFormat('yyyy-MM-dd').format(date),
        DateFormatStyle.displayDate => DateFormat.yMMMd(locale).format(date),
        DateFormatStyle.displayDateTime => DateFormat.yMMMd(locale).add_jm().format(date),
        DateFormatStyle.displayTime => DateFormat.jm(locale).format(date),
        DateFormatStyle.relative => _relative(date),
      };

  String _relative(DateTime date) {
    final diff = now.difference(date);
    if (diff.inDays.abs() > 0) return '${diff.inDays.abs()}d ${diff.isNegative ? 'from now' : 'ago'}';
    if (diff.inHours.abs() > 0) return '${diff.inHours.abs()}h ago';
    return 'just now';
  }

  @override
  DateTime? parse(String value, DateFormatStyle style) {
    try {
      return switch (style) {
        DateFormatStyle.iso8601 => DateTime.parse(value),
        DateFormatStyle.apiDate => DateFormat('yyyy-MM-dd').parse(value),
        _ => DateTime.tryParse(value),
      };
    } catch (_) { return null; }
  }

  @override
  bool isSameDay(DateTime a, DateTime b) =>
      a.year == b.year && a.month == b.month && a.day == b.day;

  @override
  bool isToday(DateTime date) => isSameDay(date, now);

  @override
  int daysBetween(DateTime start, DateTime end) => end.difference(start).inDays;
}
```

---

## Auth Interceptor <!-- 22 -->

```dart
// shared/[prefix]_core/lib/src/network/auth_interceptor.dart
@injectable
class AuthInterceptor extends Interceptor {
  AuthInterceptor(this._storage);
  final StorageService _storage;

  @override
  Future<void> onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    final token = await _storage.get<String>(StorageKey.accessToken);
    if (token != null) {
      options.headers['Authorization'] = 'Bearer $token';
    }
    handler.next(options);
  }
}
```
