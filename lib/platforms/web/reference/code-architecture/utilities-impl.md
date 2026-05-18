# Web — Core Services & Utilities


Shared infrastructure used across all layers. Interface-based for testability.

---

## StorageService <!-- 120 -->

Abstracts key-value storage. Used for auth tokens, user preferences, cached data.

```typescript
// core/storage/StorageService.ts
export type StorageKey =
  // Auth
  | 'accessToken'
  | 'refreshToken'
  | 'tokenExpiration'
  // User
  | 'userId'
  | 'userEmail'
  | 'lastSyncDate'
  // App State
  | 'onboardingCompleted'
  | 'lastSelectedTab'
  | 'themePreference';

export interface StorageService {
  get<T>(key: StorageKey): T | null;
  set<T>(key: StorageKey, value: T): void;
  remove(key: StorageKey): void;
  clearAll(): void;
  has(key: StorageKey): boolean;
}

// localStorage implementation (client-side)
export class LocalStorageService implements StorageService {
  get<T>(key: StorageKey): T | null {
    if (typeof window === 'undefined') return null;
    try {
      const item = localStorage.getItem(key);
      return item ? (JSON.parse(item) as T) : null;
    } catch {
      return null;
    }
  }

  set<T>(key: StorageKey, value: T): void {
    if (typeof window === 'undefined') return;
    try {
      localStorage.setItem(key, JSON.stringify(value));
    } catch {
      // ignore write errors (e.g., quota exceeded)
    }
  }

  remove(key: StorageKey): void {
    if (typeof window === 'undefined') return;
    localStorage.removeItem(key);
  }

  clearAll(): void {
    if (typeof window === 'undefined') return;
    const keys: StorageKey[] = [
      'accessToken', 'refreshToken', 'tokenExpiration',
      'userId', 'userEmail', 'lastSyncDate',
      'onboardingCompleted', 'lastSelectedTab', 'themePreference',
    ];
    keys.forEach((key) => this.remove(key));
  }

  has(key: StorageKey): boolean {
    return this.get(key) !== null;
  }
}

// Secure in-memory storage (for sensitive data — cleared on page unload)
export class InMemoryStorageService implements StorageService {
  private store = new Map<StorageKey, unknown>();

  get<T>(key: StorageKey): T | null {
    return (this.store.get(key) as T) ?? null;
  }

  set<T>(key: StorageKey, value: T): void {
    this.store.set(key, value);
  }

  remove(key: StorageKey): void {
    this.store.delete(key);
  }

  clearAll(): void {
    this.store.clear();
  }

  has(key: StorageKey): boolean {
    return this.store.has(key);
  }
}

// Composite: in-memory for tokens, localStorage for preferences
export class SecureStorageService implements StorageService {
  private readonly sensitiveKeys: Set<StorageKey> = new Set([
    'accessToken',
    'refreshToken',
  ]);

  constructor(
    private readonly memoryStorage = new InMemoryStorageService(),
    private readonly localStorageService = new LocalStorageService()
  ) {}

  private serviceFor(key: StorageKey): StorageService {
    return this.sensitiveKeys.has(key) ? this.memoryStorage : this.localStorageService;
  }

  get<T>(key: StorageKey): T | null { return this.serviceFor(key).get(key); }
  set<T>(key: StorageKey, value: T): void { this.serviceFor(key).set(key, value); }
  remove(key: StorageKey): void { this.serviceFor(key).remove(key); }
  clearAll(): void { this.memoryStorage.clearAll(); this.localStorageService.clearAll(); }
  has(key: StorageKey): boolean { return this.serviceFor(key).has(key); }
}
```

---

## DateService <!-- 111 -->

Centralized date handling with timezone and formatting support. Wraps `date-fns` or the native `Intl` API.

```typescript
// core/date/DateService.ts
export type DateFormatStyle =
  | 'iso8601'        // "2024-01-15T14:30:00Z"
  | 'apiDate'        // "2024-01-15"
  | 'apiDateTime'    // "2024-01-15 14:30:00"
  | 'displayDate'    // "Jan 15, 2024"
  | 'displayDateTime'// "Jan 15, 2024, 2:30 PM"
  | 'displayTime'    // "2:30 PM"
  | 'relative'       // "2 days ago", "in 3 hours"
  | { custom: string }; // Custom Intl format

export interface DateService {
  now(): Date;
  format(date: Date, style: DateFormatStyle, locale?: string): string;
  parse(value: string, style: DateFormatStyle): Date | null;
  startOfDay(date: Date): Date;
  endOfDay(date: Date): Date;
  addDays(date: Date, days: number): Date;
  daysBetween(start: Date, end: Date): number;
  isSameDay(a: Date, b: Date): boolean;
  isToday(date: Date): boolean;
  isPast(date: Date): boolean;
  isFuture(date: Date): boolean;
}

export class DateServiceImpl implements DateService {
  now(): Date { return new Date(); }

  format(date: Date, style: DateFormatStyle, locale = 'en-US'): string {
    if (style === 'iso8601') return date.toISOString();
    if (style === 'apiDate') return date.toISOString().slice(0, 10);
    if (style === 'apiDateTime') return date.toISOString().slice(0, 19).replace('T', ' ');
    if (style === 'displayDate') {
      return new Intl.DateTimeFormat(locale, { dateStyle: 'medium' }).format(date);
    }
    if (style === 'displayDateTime') {
      return new Intl.DateTimeFormat(locale, { dateStyle: 'medium', timeStyle: 'short' }).format(date);
    }
    if (style === 'displayTime') {
      return new Intl.DateTimeFormat(locale, { timeStyle: 'short' }).format(date);
    }
    if (style === 'relative') {
      const rtf = new Intl.RelativeTimeFormat(locale, { numeric: 'auto' });
      const diffDays = this.daysBetween(date, this.now());
      return rtf.format(diffDays, 'day');
    }
    if (typeof style === 'object' && 'custom' in style) {
      // Use date-fns format() for custom patterns if available
      return date.toLocaleDateString(locale);
    }
    return date.toString();
  }

  parse(value: string, style: DateFormatStyle): Date | null {
    if (style === 'iso8601' || style === 'apiDateTime') {
      const d = new Date(value);
      return isNaN(d.getTime()) ? null : d;
    }
    if (style === 'apiDate') {
      const d = new Date(`${value}T00:00:00Z`);
      return isNaN(d.getTime()) ? null : d;
    }
    return null;
  }

  startOfDay(date: Date): Date {
    const d = new Date(date);
    d.setHours(0, 0, 0, 0);
    return d;
  }

  endOfDay(date: Date): Date {
    const d = new Date(date);
    d.setHours(23, 59, 59, 999);
    return d;
  }

  addDays(date: Date, days: number): Date {
    const d = new Date(date);
    d.setDate(d.getDate() + days);
    return d;
  }

  daysBetween(start: Date, end: Date): number {
    const msPerDay = 1000 * 60 * 60 * 24;
    return Math.round((end.getTime() - start.getTime()) / msPerDay);
  }

  isSameDay(a: Date, b: Date): boolean {
    return (
      a.getFullYear() === b.getFullYear() &&
      a.getMonth() === b.getMonth() &&
      a.getDate() === b.getDate()
    );
  }

  isToday(date: Date): boolean { return this.isSameDay(date, this.now()); }
  isPast(date: Date): boolean { return date < this.now(); }
  isFuture(date: Date): boolean { return date > this.now(); }
}
```

---



## Logger <!-- 43 -->

Structured logging abstraction. Swap implementation per environment.

```typescript
// core/logger/Logger.ts
export type LogLevel = 'debug' | 'info' | 'warn' | 'error';

export interface Logger {
  debug(message: string, context?: Record<string, unknown>): void;
  info(message: string, context?: Record<string, unknown>): void;
  warn(message: string, context?: Record<string, unknown>): void;
  error(message: string, error?: Error, context?: Record<string, unknown>): void;
}

export class ConsoleLogger implements Logger {
  constructor(private readonly prefix = '[App]') {}

  debug(message: string, context?: Record<string, unknown>): void {
    if (process.env.NODE_ENV !== 'production') {
      console.debug(`${this.prefix} ${message}`, context ?? '');
    }
  }

  info(message: string, context?: Record<string, unknown>): void {
    console.info(`${this.prefix} ${message}`, context ?? '');
  }

  warn(message: string, context?: Record<string, unknown>): void {
    console.warn(`${this.prefix} ${message}`, context ?? '');
  }

  error(message: string, error?: Error, context?: Record<string, unknown>): void {
    console.error(`${this.prefix} ${message}`, error, context ?? '');
  }
}

// Singleton for app-wide logging
export const logger: Logger = new ConsoleLogger();
```

---

## NetworkMonitor <!-- 50 -->

Connectivity state observation using the browser's `navigator.onLine` and `online`/`offline` events.

```typescript
// core/network/NetworkMonitor.ts
export type NetworkStatus = 'online' | 'offline';

export interface NetworkMonitor {
  readonly status: NetworkStatus;
  subscribe(callback: (status: NetworkStatus) => void): () => void;
}

export class BrowserNetworkMonitor implements NetworkMonitor {
  get status(): NetworkStatus {
    return typeof navigator !== 'undefined' && !navigator.onLine ? 'offline' : 'online';
  }

  subscribe(callback: (status: NetworkStatus) => void): () => void {
    const handleOnline = () => callback('online');
    const handleOffline = () => callback('offline');

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }
}

// React hook
// core/network/useNetworkStatus.ts
import { useState, useEffect } from 'react';

export function useNetworkStatus(monitor = new BrowserNetworkMonitor()) {
  const [status, setStatus] = useState<NetworkStatus>(monitor.status);

  useEffect(() => {
    const unsubscribe = monitor.subscribe(setStatus);
    return unsubscribe;
  }, [monitor]);

  return { isOnline: status === 'online', status };
}
```

---

## Validator <!-- 69 -->

Input validation for common form fields.

```typescript
// core/validation/Validator.ts
export type ValidationError =
  | 'empty'
  | 'invalidEmail'
  | 'invalidPhone'
  | 'tooShort'
  | 'tooLong'
  | 'invalidFormat';

export interface ValidationResult {
  valid: boolean;
  error?: ValidationError;
  message?: string;
}

export interface Validator {
  validate(value: string): ValidationResult;
}

export class EmailValidator implements Validator {
  validate(value: string): ValidationResult {
    if (!value.trim()) return { valid: false, error: 'empty', message: 'Email is required' };
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(value)) {
      return { valid: false, error: 'invalidEmail', message: 'Enter a valid email address' };
    }
    return { valid: true };
  }
}

export class LengthValidator implements Validator {
  constructor(private readonly min: number, private readonly max = Infinity) {}

  validate(value: string): ValidationResult {
    if (!value.trim()) return { valid: false, error: 'empty', message: 'This field is required' };
    if (value.length < this.min) {
      return { valid: false, error: 'tooShort', message: `Minimum ${this.min} characters` };
    }
    if (value.length > this.max) {
      return { valid: false, error: 'tooLong', message: `Maximum ${this.max} characters` };
    }
    return { valid: true };
  }
}

// React hook for form field validation
export function useFormField(validator: Validator) {
  const [value, setValue] = useState('');
  const [touched, setTouched] = useState(false);

  const result = touched ? validator.validate(value) : { valid: true };

  return {
    value,
    error: result.valid ? null : result.message ?? null,
    isValid: result.valid,
    onChange: (v: string) => { setValue(v); setTouched(true); },
    onBlur: () => setTouched(true),
  };
}
```

---

## ImageCache <!-- 49 -->

Asynchronous image loading leveraging Next.js `<Image>` component and browser cache.

```typescript
// core/image/ImageCache.ts

// In Next.js, most image caching is handled by the <Image> component.
// This utility handles cases where you need programmatic image prefetching.

export interface ImageCache {
  preload(urls: string[]): void;
  clearCache(): void;
}

export class BrowserImageCache implements ImageCache {
  private cache = new Map<string, HTMLImageElement>();

  preload(urls: string[]): void {
    urls.forEach((url) => {
      if (this.cache.has(url)) return;
      const img = new Image();
      img.src = url;
      this.cache.set(url, img);
    });
  }

  clearCache(): void {
    this.cache.clear();
  }
}

// React hook for image loading state
export function useImage(src: string) {
  const [status, setStatus] = useState<'loading' | 'loaded' | 'error'>('loading');

  useEffect(() => {
    if (!src) { setStatus('error'); return; }
    const img = new Image();
    img.onload = () => setStatus('loaded');
    img.onerror = () => setStatus('error');
    img.src = src;
  }, [src]);

  return { isLoading: status === 'loading', isError: status === 'error', isLoaded: status === 'loaded' };
}
```

---
