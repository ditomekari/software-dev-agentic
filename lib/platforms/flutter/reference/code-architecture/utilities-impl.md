# Flutter — Core Services & Utilities

Shared infrastructure used across all layers. Interface-based for testability. Register all services via `get_it` + `injectable`.

---

## StorageService <!-- 110 -->

Abstracts key-value storage. `SharedPreferences` for preferences; `FlutterSecureStorage` for tokens.

```dart
// core/storage/storage_service.dart
abstract class StorageService {
  Future<void> set<T>(StorageKey key, T value);
  Future<T?> get<T>(StorageKey key);
  Future<void> remove(StorageKey key);
  Future<void> clearAll();
  Future<bool> contains(StorageKey key);
}

enum StorageKey {
  // Auth
  accessToken,
  refreshToken,
  tokenExpiration,
  // User
  userId,
  userEmail,
  lastSyncDate,
  // App State
  onboardingCompleted,
  lastSelectedTab,
}
```

```dart
// core/storage/shared_preferences_storage_service.dart
import 'package:shared_preferences/shared_preferences.dart';

@LazySingleton(as: StorageService)
class SharedPreferencesStorageService implements StorageService {
  final SharedPreferences _prefs;

  SharedPreferencesStorageService(this._prefs);

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
  Future<void> remove(StorageKey key) async => _prefs.remove(key.name);

  @override
  Future<void> clearAll() async {
    for (final key in StorageKey.values) {
      await remove(key);
    }
  }

  @override
  Future<bool> contains(StorageKey key) async => _prefs.containsKey(key.name);
}
```

```dart
// Secure storage for tokens (flutter_secure_storage)
@Named('secure')
@LazySingleton(as: StorageService)
class SecureStorageService implements StorageService {
  final FlutterSecureStorage _storage;
  static const _sensitiveKeys = {StorageKey.accessToken, StorageKey.refreshToken};

  SecureStorageService(@Named('flutterSecureStorage') this._storage);

  @override
  Future<void> set<T>(StorageKey key, T value) async {
    if (_sensitiveKeys.contains(key)) {
      await _storage.write(key: key.name, value: value.toString());
    }
  }

  @override
  Future<T?> get<T>(StorageKey key) async {
    final value = await _storage.read(key: key.name);
    return value as T?;
  }

  @override
  Future<void> remove(StorageKey key) => _storage.delete(key: key.name);

  @override
  Future<void> clearAll() async => _storage.deleteAll();

  @override
  Future<bool> contains(StorageKey key) async =>
      (await _storage.read(key: key.name)) != null;
}
```

---

## DateService <!-- 103 -->

Centralized date handling with timezone and formatting. Uses `intl` package.

```dart
// core/date/date_service.dart
abstract class DateService {
  DateTime get now;
  String format(DateTime date, DateFormatStyle style, {String locale});
  DateTime? parse(String value, DateFormatStyle style);
  DateTime startOfDay(DateTime date);
  DateTime endOfDay(DateTime date);
  DateTime addDays(DateTime date, int days);
  int daysBetween(DateTime start, DateTime end);
  bool isSameDay(DateTime a, DateTime b);
  bool isToday(DateTime date);
  bool isPast(DateTime date);
  bool isFuture(DateTime date);
}

enum DateFormatStyle {
  iso8601,       // "2024-01-15T14:30:00Z"
  apiDate,       // "2024-01-15"
  apiDateTime,   // "2024-01-15 14:30:00"
  displayDate,   // "Jan 15, 2024"
  displayDateTime, // "Jan 15, 2024, 2:30 PM"
  displayTime,   // "2:30 PM"
  relative,      // "2 days ago"
}
```

```dart
// core/date/date_service_impl.dart
import 'package:intl/intl.dart';

@LazySingleton(as: DateService)
class DateServiceImpl implements DateService {
  @override
  DateTime get now => DateTime.now();

  @override
  String format(DateTime date, DateFormatStyle style, {String locale = 'en_US'}) {
    return switch (style) {
      DateFormatStyle.iso8601 => date.toIso8601String(),
      DateFormatStyle.apiDate => DateFormat('yyyy-MM-dd').format(date),
      DateFormatStyle.apiDateTime => DateFormat('yyyy-MM-dd HH:mm:ss').format(date),
      DateFormatStyle.displayDate => DateFormat.yMMMd(locale).format(date),
      DateFormatStyle.displayDateTime => DateFormat.yMMMd(locale).add_jm().format(date),
      DateFormatStyle.displayTime => DateFormat.jm(locale).format(date),
      DateFormatStyle.relative => _relative(date),
    };
  }

  String _relative(DateTime date) {
    final diff = now.difference(date);
    if (diff.inDays.abs() > 0) return '${diff.inDays.abs()} day${diff.inDays.abs() == 1 ? '' : 's'} ${diff.isNegative ? 'from now' : 'ago'}';
    if (diff.inHours.abs() > 0) return '${diff.inHours.abs()} hour${diff.inHours.abs() == 1 ? '' : 's'} ${diff.isNegative ? 'from now' : 'ago'}';
    return 'just now';
  }

  @override
  DateTime? parse(String value, DateFormatStyle style) {
    try {
      return switch (style) {
        DateFormatStyle.iso8601 => DateTime.parse(value),
        DateFormatStyle.apiDate => DateFormat('yyyy-MM-dd').parse(value),
        DateFormatStyle.apiDateTime => DateFormat('yyyy-MM-dd HH:mm:ss').parse(value),
        _ => DateTime.tryParse(value),
      };
    } catch (_) { return null; }
  }

  @override
  DateTime startOfDay(DateTime date) => DateTime(date.year, date.month, date.day);

  @override
  DateTime endOfDay(DateTime date) => DateTime(date.year, date.month, date.day, 23, 59, 59, 999);

  @override
  DateTime addDays(DateTime date, int days) => date.add(Duration(days: days));

  @override
  int daysBetween(DateTime start, DateTime end) => end.difference(start).inDays;

  @override
  bool isSameDay(DateTime a, DateTime b) =>
      a.year == b.year && a.month == b.month && a.day == b.day;

  @override
  bool isToday(DateTime date) => isSameDay(date, now);

  @override
  bool isPast(DateTime date) => date.isBefore(now);

  @override
  bool isFuture(DateTime date) => date.isAfter(now);
}
```

---



## Logger <!-- 64 -->

Structured logging using the `logger` package. Swap implementation per environment.

```dart
// core/logger/app_logger.dart
import 'package:logger/logger.dart';

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
      printEmojis: true,
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

**Usage via DI:**
```dart
// Inject AppLogger wherever needed
class EmployeeRepository implements EmployeeRepositoryProtocol {
  final AppLogger _logger;
  EmployeeRepository(this._logger);

  @override
  Future<Either<Failure, Employee>> getEmployee(String id) async {
    try {
      // ...
    } catch (e, stack) {
      _logger.error('getEmployee failed', error: e, stackTrace: stack);
      return Left(Failure.unknownFailure(message: e.toString()));
    }
  }
}
```
