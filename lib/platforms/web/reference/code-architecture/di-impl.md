# Web — Dependency Injection

> Concepts and invariants: `reference/code-architecture/di-theory.md`. This file covers TypeScript syntax and web-specific patterns.

Next.js App Router has a hard split between **Server Components** (run only on the server) and **Client Components** (run in the browser). This changes how DI should work:

- **Server Components** cannot use React Context or hooks — but Node.js module caching already gives you singletons for free
- **Client Components** need React Context to share dependencies across the component tree

The strategy: **two containers, two runtimes**.

```
┌────────────────────────────────────────────────────────┐
│  Server Components (RSC)                               │
│  import directly from di/container.server.ts           │
│  → no Context, no Provider, no hook                    │
└────────────────────────────────────────────────────────┘
┌────────────────────────────────────────────────────────┐
│  Client Components ('use client')                      │
│  get deps from useDI() hook (React Context)            │
│  → DIProvider wraps client subtrees only               │
└────────────────────────────────────────────────────────┘
```

## Server Container <!-- 30 -->

Module-level exports are natural singletons in Node.js — the module is evaluated once and cached. No DI framework needed for server-side code.

```typescript
// di/container.server.ts
import 'server-only'; // hard compile error if accidentally imported in a Client Component

import { createHTTPClient, createUnauthenticatedHTTPClient } from '@/data/networking/AxiosHTTPClient';
import { ServerTokenStorage } from '@/core/storage/ServerTokenStorage';
import { TokenRefreshService } from '@/data/networking/TokenRefreshService';
import { EmployeeRemoteDataSourceImpl } from '@/data/data-sources/remote/EmployeeRemoteDataSourceImpl';
import { EmployeeRepositoryImpl } from '@/data/repositories/EmployeeRepositoryImpl';
import { GetEmployeesUseCaseImpl } from '@/domain/use-cases/employee/GetEmployeesUseCase';
import { GetEmployeeUseCaseImpl } from '@/domain/use-cases/employee/GetEmployeeUseCase';

// These are created once and reused across all server requests (module cache = singleton)
const tokenStorage = new ServerTokenStorage();
const unauthClient = createUnauthenticatedHTTPClient(process.env.API_BASE_URL!);
const tokenRefresher = new TokenRefreshService(unauthClient, tokenStorage);
const httpClient = createHTTPClient(process.env.API_BASE_URL!, tokenStorage, tokenRefresher);

const employeeRemoteDS = new EmployeeRemoteDataSourceImpl(httpClient);
const employeeRepository = new EmployeeRepositoryImpl(employeeRemoteDS);

// Use case factories — new instance per call (stateless, cheap)
export const getEmployeesUseCase = () => new GetEmployeesUseCaseImpl(employeeRepository);
export const getEmployeeUseCase = () => new GetEmployeeUseCaseImpl(employeeRepository);
```

## Client Container <!-- 61 -->

Only client-interactive dependencies live here. Uses `NEXT_PUBLIC_` env vars because this code runs in the browser.

```typescript
// di/container.client.ts
import 'client-only'; // hard compile error if accidentally imported in a Server Component

import { createHTTPClient, createUnauthenticatedHTTPClient } from '@/data/networking/AxiosHTTPClient';
import { LocalStorageTokenProvider } from '@/core/storage/LocalStorageTokenProvider';
import { TokenRefreshService } from '@/data/networking/TokenRefreshService';
import { EmployeeRemoteDataSourceImpl } from '@/data/data-sources/remote/EmployeeRemoteDataSourceImpl';
import { EmployeeRepositoryImpl } from '@/data/repositories/EmployeeRepositoryImpl';
import { GetEmployeesUseCaseImpl } from '@/domain/use-cases/employee/GetEmployeesUseCase';
import { DeleteEmployeeUseCaseImpl } from '@/domain/use-cases/employee/DeleteEmployeeUseCase';

export function createClientContainer() {
  // Networking
  const tokenStorage = new LocalStorageTokenProvider();
  const unauthClient = createUnauthenticatedHTTPClient(process.env.NEXT_PUBLIC_API_BASE_URL!);
  const tokenRefresher = new TokenRefreshService(unauthClient, tokenStorage);
  const httpClient = createHTTPClient(process.env.NEXT_PUBLIC_API_BASE_URL!, tokenStorage, tokenRefresher);

  // Repositories (singleton within this container)
  const employeeRepository = new EmployeeRepositoryImpl(
    new EmployeeRemoteDataSourceImpl(httpClient)
  );

  // Use case factories (new instance on each access — stateless, cheap)
  return {
    get getEmployeesUseCase() { return new GetEmployeesUseCaseImpl(employeeRepository); },
    get deleteEmployeeUseCase() { return new DeleteEmployeeUseCaseImpl(employeeRepository); },
    // add more as the app grows
  };
}

export type ClientContainer = ReturnType<typeof createClientContainer>;
```

```typescript
// di/DIContext.tsx
'use client';

import { createContext, useContext, useMemo, type ReactNode } from 'react';
import { createClientContainer, type ClientContainer } from './container.client';

const DIContext = createContext<ClientContainer | null>(null);

export function DIProvider({ children }: { children: ReactNode }) {
  // useMemo ensures createClientContainer() is called only once per mount
  const container = useMemo(() => createClientContainer(), []);
  return <DIContext.Provider value={container}>{children}</DIContext.Provider>;
}

export function useDI(): ClientContainer {
  const ctx = useContext(DIContext);
  if (!ctx) throw new Error('useDI must be used within DIProvider');
  return ctx;
}
```

## App Entry Point <!-- 74 -->

`DIProvider` no longer needs to wrap the entire app — only the client subtrees that need it. The root layout stays a Server Component:

```typescript
// app/layout.tsx  ← Server Component (no 'use client')
import { QueryClientProvider } from '@/presentation/providers/QueryClientProvider';
import { Toaster } from '@/presentation/common/Toaster';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        {/* QueryClientProvider is 'use client' internally — wraps only what needs it */}
        <QueryClientProvider>
          {children}
          <Toaster />
        </QueryClientProvider>
      </body>
    </html>
  );
}
```

```typescript
// app/(main)/layout.tsx  ← Client layout that needs DI
'use client';

import { DIProvider } from '@/di/DIContext';

export default function MainLayout({ children }: { children: React.ReactNode }) {
  return (
    <DIProvider>
      {children}
    </DIProvider>
  );
}
```

**Usage in a Server Component page** — import directly, no hook:

```typescript
// app/employees/page.tsx  ← Server Component
import { getEmployeesUseCase } from '@/di/container.server';
import { EmployeeListView } from '@/presentation/features/employee-list/EmployeeListView';

export default async function EmployeesPage() {
  // Data fetched on the server — arrives pre-loaded, zero client waterfall
  const initialData = await getEmployeesUseCase().execute({ page: 1, limit: 20 });

  return <EmployeeListView initialData={initialData} />;
}
```

**Usage in a Client Component** — via `useDI()` hook:

```typescript
// presentation/features/employee-list/EmployeeListView.tsx  ← Client Component
'use client';

import { useDI } from '@/di/DIContext';

export function EmployeeListView({ initialData }: { initialData?: PaginatedResult<Employee> }) {
  const { getEmployeesUseCase, deleteEmployeeUseCase } = useDI();

  const vm = useEmployeeListViewModel({
    getEmployeesUseCase,
    deleteEmployeeUseCase,
    initialData, // pre-loaded server data seeds the TanStack Query cache
  });
  // ...
}
```

## Decision Rule <!-- 12 -->

```
Is this component a Server Component?
  ├── YES → import from di/container.server.ts
  └── NO  → get from useDI() (React Context)

Does this env var go to the browser?
  ├── YES → NEXT_PUBLIC_API_BASE_URL (container.client.ts)
  └── NO  → API_BASE_URL (container.server.ts)
```

## DI Principles <!-- 13 -->

| Rule | Reason |
|------|--------|
| Server deps live in `container.server.ts` | Module cache = free singletons, stays off the client bundle |
| Client deps live in `container.client.ts` | Isolated from server secrets and Node.js APIs |
| `server-only` / `client-only` guards | Compile-time error if a container is used in the wrong runtime |
| Repositories are **singletons** | Shared state, caching |
| Use Cases are **factories** (`get` accessor) | Stateless, cheap to create |
| ViewModel hooks receive deps as arguments | Explicit, testable, no hidden globals |
| Services use **default parameter injection** | `constructor(validator = new ValidatorService())` — overridable in tests |
| For large-scale: split into per-feature containers | See Section 11.5–11.6 |

## Registration Order <!-- 24 -->

Instantiate in leaf-first order — infrastructure before consumers. Node.js module caching enforces this naturally for the server container:

```typescript
// container.server.ts — registration order
// 1. Infrastructure
const tokenStorage = new ServerTokenStorage();
const unauthClient = createUnauthenticatedHTTPClient(process.env.API_BASE_URL!);
const tokenRefresher = new TokenRefreshService(unauthClient, tokenStorage);
const httpClient = createHTTPClient(process.env.API_BASE_URL!, tokenStorage, tokenRefresher);

// 2. DataSources (depend on httpClient)
const employeeRemoteDS = new EmployeeRemoteDataSourceImpl(httpClient);

// 3. Repositories (depend on DataSource + Mapper)
const employeeRepository = new EmployeeRepositoryImpl(employeeRemoteDS);

// 4. Use Cases (factories — stateless, cheap; depend on Repository)
export const getEmployeesUseCase = () => new GetEmployeesUseCaseImpl(employeeRepository);
```

For the client container, the same order applies inside `createClientContainer()`.

## Scope Rules <!-- 11 -->

| Scope | Web pattern | Use for |
|---|---|---|
| Singleton (server) | Module-level `const` in `container.server.ts` | HTTP client, token storage, repositories — one per server process |
| Singleton (client) | Module-level inside `createClientContainer()` | Repositories — one per `DIProvider` mount |
| Factory | `get` accessor or inline `new` in ViewModel hook | Use Cases — stateless, cheap |
| Transient | Default parameter: `constructor(dep = new Dep())` | Pure domain services — overridable in tests |

**Never store mutable UI state in a container-level singleton.** ViewModel hooks manage their own state via `useState`/`useReducer` — the container only holds pure, stateless dependencies.

## Testing with DI <!-- 26 -->

ViewModel hooks receive dependencies as arguments — substitute mocks directly without touching the container:

```typescript
// Unit test — no DIProvider needed
const mockGetEmployeesUseCase = { execute: vi.fn() };
const mockDeleteEmployeeUseCase = { execute: vi.fn() };

const { result } = renderHook(
  () => useEmployeeListViewModel({
    getEmployeesUseCase: mockGetEmployeesUseCase,
    deleteEmployeeUseCase: mockDeleteEmployeeUseCase,
  }),
  { wrapper: createQueryClientWrapper() }
);
```

For server-side functions, override default-parameter services inline:

```typescript
// Override a domain service with a stub
const result = leaveRequestService.validate(entitlement, 3, date, MockValidatorService());
```

Never instantiate `container.server.ts` or `container.client.ts` in unit tests — test collaborators in isolation.
