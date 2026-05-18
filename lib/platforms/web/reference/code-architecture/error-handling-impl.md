# Web — Error Handling

> Concepts and invariants: `reference/code-architecture/error-handling-theory.md`. This file covers TypeScript syntax and web-specific patterns.

## Error Flow <!-- 14 -->

```
DataSource throws NetworkError
    ↓ caught by
Repository maps to DomainError
    ↓ propagated via
UseCase (passes through or enriches)
    ↓ caught by
ViewModel hook → TanStack Query error state
    ↓ rendered by
Component shows error UI
```

## Error Types <!-- 9 -->

```typescript
// data/networking/NetworkError.ts (already defined above)
// domain/errors/DomainError.ts (already defined above)
```

Error type definitions live in `contract/domain.md ## Domain Errors`. See `## Error Mapping` for layer mapping and `## Error UI` for UI display.

## Error Mapping <!-- 30 -->

`ErrorMapperImpl` follows the same interface-based pattern as other mappers (see Section 4.2). Repositories inject `ErrorMapper` to convert `NetworkError` → `DomainError`:

```typescript
// Usage in repository — pattern is already shown in Section 4.4
// The key principle: DataSource throws NetworkError, Repository catches and maps to DomainError

// Displaying errors in components — use TanStack Query's error state
const { error } = useQuery({ ... });
const message = error instanceof DomainError
  ? humanizeError(error.code)
  : 'Something went wrong';

// presentation/common/utils/errorMessages.ts
export function humanizeError(code: DomainErrorCode): string {
  const messages: Record<DomainErrorCode, string> = {
    notFound: 'The requested resource was not found.',
    validationFailed: 'Please check your input and try again.',
    unauthorized: 'You are not authorized to perform this action.',
    networkUnavailable: 'No internet connection. Please check your network.',
    serverError: 'Something went wrong on our end. Please try again.',
    unknown: 'An unexpected error occurred.',
  };
  return messages[code];
}
// Note: humanizeError lives in the presentation layer — user-facing message
// strings are a display concern, not a domain concept.
```

## Error UI <!-- 34 -->

React error boundaries catch rendering errors; TanStack Query's error state surfaces data-fetch errors.

```typescript
// app/employees/error.tsx — Next.js error boundary (per route segment)
'use client';

export default function EmployeesError({
  error,
  reset,
}: {
  error: Error;
  reset: () => void;
}) {
  return (
    <div className="flex flex-col items-center gap-4 p-8">
      <p className="text-error">{error.message}</p>
      <button onClick={reset} className="btn btn-primary">Try again</button>
    </div>
  );
}

// In components — TanStack Query error state (non-blocking)
const { error } = useQuery({ ... });
if (error) return <ErrorView message={humanizeError(error.code)} />;
```

**Rules:**
- Place `error.tsx` at the route segment level, not globally — scope errors to the affected section
- Never expose raw error codes or stack traces to users — use `humanizeError(code)`
- `humanizeError` lives in `presentation/common/utils/errorMessages.ts` (presentation layer, not domain)

---
