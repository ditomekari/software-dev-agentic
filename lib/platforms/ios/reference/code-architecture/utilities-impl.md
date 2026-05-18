# iOS — Core Services & Utilities

Shared infrastructure used across all layers. Interface-based for testability.

---

## StorageService <!-- 100 -->

Abstract key-value storage for tokens, preferences, cached data.

```swift
// Core/Storage/StorageService.swift
protocol StorageService: Sendable {
    func get<T: Codable>(_ key: StorageKey) -> T?
    func set<T: Codable>(_ value: T, for key: StorageKey)
    func remove(_ key: StorageKey)
    func clearAll()
    func contains(_ key: StorageKey) -> Bool
}

enum StorageKey: String, Sendable {
    // Auth
    case accessToken
    case refreshToken
    case tokenExpiration

    // User
    case userId
    case userEmail
    case lastSyncDate

    // App State
    case onboardingCompleted
    case lastSelectedTab
}

// UserDefaults Implementation
final class UserDefaultsStorageService: StorageService {
    private let defaults: UserDefaults
    private let encoder: JSONEncoder
    private let decoder: JSONDecoder

    init(
        defaults: UserDefaults = .standard,
        encoder: JSONEncoder = .init(),
        decoder: JSONDecoder = .init()
    ) {
        self.defaults = defaults
        self.encoder = encoder
        self.decoder = decoder
    }

    func get<T: Codable>(_ key: StorageKey) -> T? {
        guard let data = defaults.data(forKey: key.rawValue) else { return nil }
        return try? decoder.decode(T.self, from: data)
    }

    func set<T: Codable>(_ value: T, for key: StorageKey) {
        guard let data = try? encoder.encode(value) else { return }
        defaults.set(data, forKey: key.rawValue)
    }

    func remove(_ key: StorageKey) {
        defaults.removeObject(forKey: key.rawValue)
    }

    func clearAll() {
        StorageKey.allCases.forEach { remove($0) }
    }

    func contains(_ key: StorageKey) -> Bool {
        defaults.object(forKey: key.rawValue) != nil
    }
}

// Keychain Implementation (for sensitive data)
final class KeychainStorageService: StorageService {
    // ... keychain implementation
}

// Composite (Keychain + UserDefaults)
final class SecureStorageService: StorageService {
    private let keychain = KeychainStorageService()
    private let userDefaults = UserDefaultsStorageService()

    private let sensitiveKeys: Set<StorageKey> = [
        .accessToken,
        .refreshToken
    ]

    private func service(for key: StorageKey) -> StorageService {
        sensitiveKeys.contains(key) ? keychain : userDefaults
    }

    func get<T: Codable>(_ key: StorageKey) -> T? { service(for: key).get(key) }
    func set<T: Codable>(_ value: T, for key: StorageKey) { service(for: key).set(value, for: key) }
    func remove(_ key: StorageKey) { service(for: key).remove(key) }
    func clearAll() { keychain.clearAll(); userDefaults.clearAll() }
    func contains(_ key: StorageKey) -> Bool { service(for: key).contains(key) }
}
```

**Usage:** Use `StorageHelper.getStringValue(key:)` for simple token reads. Use `StorageService` protocol for injectable, testable components.

---

## DateService <!-- 72 -->

Centralized date handling with timezone/formatting.

```swift
// Core/Date/DateService.swift
protocol DateService {
    var now: Date { get }
    var currentTimeZone: TimeZone { get }

    func format(_ date: Date, style: DateFormatStyle) -> String
    func parse(_ string: String, format: DateFormatStyle) -> Date?
    func startOfDay(_ date: Date) -> Date
    func endOfDay(_ date: Date) -> Date
    func addDays(_ days: Int, to date: Date) -> Date
    func daysBetween(_ start: Date, _ end: Date) -> Int
    func isSameDay(_ date1: Date, _ date2: Date) -> Bool
}

enum DateFormatStyle {
    case iso8601              // "2024-01-15T14:30:00Z"
    case apiDate              // "2024-01-15"
    case apiDateTime          // "2024-01-15 14:30:00"
    case displayDate          // "Jan 15, 2024"
    case displayDateTime      // "Jan 15, 2024 at 2:30 PM"
    case displayTime          // "2:30 PM"
    case relative             // "2 days ago"
    case custom(String)
}

final class DateServiceImpl: DateService {
    private let calendar: Calendar
    private let locale: Locale

    init(calendar: Calendar = .current, locale: Locale = .current) {
        self.calendar = calendar
        self.locale = locale
    }

    var now: Date { Date() }
    var currentTimeZone: TimeZone { calendar.timeZone }

    func format(_ date: Date, style: DateFormatStyle) -> String {
        switch style {
        case .iso8601: return ISO8601DateFormatter().string(from: date)
        case .apiDate: return formatWith("yyyy-MM-dd", date)
        case .displayDate:
            let formatter = DateFormatter()
            formatter.dateStyle = .medium
            formatter.timeStyle = .none
            formatter.locale = locale
            return formatter.string(from: date)
        case .custom(let format): return formatWith(format, date)
        default: return formatWith("yyyy-MM-dd HH:mm:ss", date)
        }
    }
}

extension DateService {
    func toAPIDate(_ date: Date) -> String { format(date, style: .apiDate) }
    func fromAPIDate(_ string: String) -> Date? { parse(string, format: .apiDate) }
    func isToday(_ date: Date) -> Bool { isSameDay(date, now) }
    func isPast(_ date: Date) -> Bool { date < now }
    func isFuture(_ date: Date) -> Bool { date > now }
}
```

**Usage:** For simple formatting use `Date+Extensions.swift` helpers. Use `DateService` for injectable, testable components.

---


## Null Safety Extensions <!-- 54 -->

**Always use extension methods for optional unwrapping — never force-unwrap or inline `?? value`.**

```swift
// Core/Extensions/Optional+NullSafety.swift

extension Optional where Wrapped: Numeric {
    func orZero() -> Wrapped { self ?? 0 }
    func orDefault(_ defaultValue: Wrapped) -> Wrapped { self ?? defaultValue }
}

extension Optional where Wrapped == String {
    func orEmpty() -> String { self ?? "" }
    func orDefault(_ defaultValue: String) -> String {
        guard let self = self, !self.trimmingCharacters(in: .whitespaces).isEmpty else {
            return defaultValue
        }
        return self
    }
}

extension Optional where Wrapped: Collection {
    func orEmpty() -> Wrapped { self ?? [] as! Wrapped }
    var isNilOrEmpty: Bool { self?.isEmpty ?? true }
}

extension Optional where Wrapped == Bool {
    func orFalse() -> Bool { self ?? false }
    func orTrue() -> Bool { self ?? true }
}

extension Optional {
    func orDefault(_ factory: @autoclosure () -> Wrapped) -> Wrapped { self ?? factory() }
    @discardableResult
    func orElse(_ action: () -> Wrapped) -> Wrapped { self ?? action() }
}
```

**Usage:**

```swift
let name = employee.nickname.orEmpty()
let count = employees?.count.orZero()
let limit = params.limit.orDefault(20)
let isEnabled = featureFlags?.newUI.orFalse()

// CRITICAL: Wrap optional chains in parentheses before calling extension methods
let title = ($0.dataState.data?.appBarTitle).orEmpty()     // ✅
let title = $0.dataState.data?.appBarTitle.orEmpty()       // ❌ compile error
```

---

## Logger <!-- 62 -->

Centralized logging with severity levels.

```swift
// Core/Logger/Logger.swift
import OSLog

enum LogLevel: Int, Comparable {
    case verbose = 0, debug = 1, info = 2, warning = 3, error = 4
    static func < (lhs: LogLevel, rhs: LogLevel) -> Bool { lhs.rawValue < rhs.rawValue }
}

protocol Logger {
    func log(_ message: String, level: LogLevel, file: String, function: String, line: Int)
}

extension Logger {
    func verbose(_ message: String, file: String = #file, function: String = #function, line: Int = #line) {
        log(message, level: .verbose, file: file, function: function, line: line)
    }
    func debug(_ message: String, file: String = #file, function: String = #function, line: Int = #line) {
        log(message, level: .debug, file: file, function: function, line: line)
    }
    func info(_ message: String, file: String = #file, function: String = #function, line: Int = #line) {
        log(message, level: .info, file: file, function: function, line: line)
    }
    func warning(_ message: String, file: String = #file, function: String = #function, line: Int = #line) {
        log(message, level: .warning, file: file, function: function, line: line)
    }
    func error(_ message: String, file: String = #file, function: String = #function, line: Int = #line) {
        log(message, level: .error, file: file, function: function, line: line)
    }
}

final class ConsoleLogger: Logger {
    private let minLevel: LogLevel
    private let osLogger: OSLog.Logger

    init(minLevel: LogLevel = .debug) {
        self.minLevel = minLevel
        self.osLogger = OSLog.Logger(subsystem: Bundle.main.bundleIdentifier ?? "app", category: "general")
    }

    func log(_ message: String, level: LogLevel, file: String, function: String, line: Int) {
        guard level >= minLevel else { return }
        let filename = (file as NSString).lastPathComponent
        osLogger.log(level: level.osLogType, "\(level.emoji) [\(filename):\(line)] \(function): \(message)")
    }
}

enum Log {
    nonisolated(unsafe) static var shared: Logger = ConsoleLogger()
    static func debug(_ message: String, file: String = #file, function: String = #function, line: Int = #line) { shared.debug(message, file: file, function: function, line: line) }
    static func info(_ message: String, file: String = #file, function: String = #function, line: Int = #line) { shared.info(message, file: file, function: function, line: line) }
    static func warning(_ message: String, file: String = #file, function: String = #function, line: Int = #line) { shared.warning(message, file: file, function: function, line: line) }
    static func error(_ message: String, file: String = #file, function: String = #function, line: Int = #line) { shared.error(message, file: file, function: function, line: line) }
}
```

---

## Helper Extensions <!-- 19 -->

Extension files live in `Talenta/Shared/Extension/`.

| Helper | File | Key Methods |
|--------|------|-------------|
| `String?` | `Extension+String?.swift` | `.orEmpty()`, `.ifNullOrEmptyReturnDash()` |
| `Int?` | `Extension+Int?.swift` | `.orZero()`, `.orOne()` |
| `Double?` | `Extension+Double?.swift` | `.orZero()` |
| `Bool?` | `Extension+Bool?.swift` | `.orFalse()`, `.orTrue()` |
| `Array?` | `Extension+Array?.swift` | `.orEmpty()` |
| `Date` | `Date+Extensions.swift` | `.toDMYString()`, `.toHHMMString()`, `.toYMDString()`, `.isToday`, `.isPast`, `.startOfDay` |
| `String` → Date | `Date+Extensions.swift` | `.toDate(format:)`, `.toTimeDate()` |
| `Double/Int` (currency) | `Extension+Double.swift` | `.toRupiahString()`, `.toFormattedString()` |
| `String` utilities | `Extension+String.swift` | `.removeWhitespace`, `.capitalizeFirstLetter`, `.isNumeric`, `.truncate(length:)`, `.masked` |
| `UIView` | `UIView+Extensions.swift` | `.addSubviews(...)`, `.roundCorners(...)`, `.addShadow(...)`, `.shake()` |
| `UIViewController` | `UIViewController+Extensions.swift` | `.showAlert(...)`, `.showErrorAlert(message:)`, `.showConfirmation(...)`, `.hideKeyboardWhenTappedAround()` |
| `BaseErrorModel` | `BaseErrorModel+Extensions.swift` | `.createEmptyDataError()`, `.createNetworkError()`, `.from(error:)` |
| `Observable` | `Observable+Extensions.swift` | `.unwrap()`, `.mapToVoid()`, `.retryWithDelay(...)` |
