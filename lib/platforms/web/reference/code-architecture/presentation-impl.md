# Web — Presentation Layer

> Concepts and invariants: `reference/code-architecture/presentation-theory.md`. This file covers TypeScript syntax and web-specific patterns.

## State Management <!-- 33 -->

A unified state type for all view states — mirrors the `ViewState<T>` enum from the SwiftUI kit.

```typescript
// presentation/common/QueryState.ts
export type QueryState<T> =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'loaded'; data: T }
  | { status: 'error'; message: string };

export function isIdle<T>(state: QueryState<T>): state is { status: 'idle' } {
  return state.status === 'idle';
}

export function isLoading<T>(state: QueryState<T>): state is { status: 'loading' } {
  return state.status === 'loading';
}

export function isLoaded<T>(state: QueryState<T>): state is { status: 'loaded'; data: T } {
  return state.status === 'loaded';
}

export function isError<T>(state: QueryState<T>): state is { status: 'error'; message: string } {
  return state.status === 'error';
}

export function getDataOrNull<T>(state: QueryState<T>): T | null {
  return isLoaded(state) ? state.data : null;
}
```

## ViewModel Hook <!-- 91 -->

The ViewModel pattern is implemented as a custom React hook. No class inheritance — just a hook that orchestrates use cases, manages state, and handles navigation.

```typescript
// presentation/features/employee-list/useEmployeeListViewModel.ts
'use client';

import { useRouter } from 'next/navigation';
import { useState, useCallback } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Employee } from '@/domain/entities/Employee';
import { GetEmployeesUseCase } from '@/domain/use-cases/employee/GetEmployeesUseCase';
import { DeleteEmployeeUseCase } from '@/domain/use-cases/employee/DeleteEmployeeUseCase';
import { ROUTES } from '@/presentation/navigation/routes';

interface EmployeeListViewModelDeps {
  getEmployeesUseCase: GetEmployeesUseCase;
  deleteEmployeeUseCase: DeleteEmployeeUseCase;
}

export function useEmployeeListViewModel({
  getEmployeesUseCase,
  deleteEmployeeUseCase,
}: EmployeeListViewModelDeps) {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [searchQuery, setSearchQuery] = useState('');
  const [currentPage, setCurrentPage] = useState(1);

  // Data fetching — TanStack Query handles loading/error/data states
  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['employees', currentPage, searchQuery],
    queryFn: () =>
      getEmployeesUseCase.execute({ page: currentPage, limit: 20, searchQuery }),
  });

  // Mutation — TanStack Query handles optimistic updates
  const deleteMutation = useMutation({
    mutationFn: (employee: Employee) =>
      deleteEmployeeUseCase.execute({ employeeId: employee.id }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['employees'] });
    },
  });

  // Navigation
  const handleEmployeeClick = useCallback(
    (employee: Employee) => {
      router.push(ROUTES.employeeDetail(employee.id));
    },
    [router]
  );

  const handleDeleteEmployee = useCallback(
    (employee: Employee) => {
      deleteMutation.mutate(employee);
    },
    [deleteMutation]
  );

  const handleSearchChange = useCallback((query: string) => {
    setSearchQuery(query);
    setCurrentPage(1);
  }, []);

  const handleRefresh = useCallback(() => {
    refetch();
  }, [refetch]);

  return {
    // State
    employees: data?.items ?? [],
    totalPages: data?.totalPages ?? 0,
    currentPage,
    searchQuery,
    isLoading,
    isError,
    errorMessage: error?.message ?? null,
    isDeleting: deleteMutation.isPending,

    // Actions
    handleEmployeeClick,
    handleDeleteEmployee,
    handleSearchChange,
    handleRefresh,
    handlePageChange: setCurrentPage,
  };
}
```

## ViewModel Hook with Service Integration <!-- 58 -->

When a ViewModel hook needs business decisions, it delegates to a Domain Service:

```typescript
// presentation/features/leave-request/useLeaveRequestViewModel.ts
'use client';

import { useState, useCallback } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { LeaveRequestValidator, LeaveRequestValidatorService } from '@/domain/services/LeaveRequestValidator';

interface LeaveRequestViewModelDeps {
  getEntitlementUseCase: GetLeaveEntitlementUseCase;
  submitLeaveUseCase: SubmitLeaveRequestUseCase;
  validator?: LeaveRequestValidator; // Domain Service (interface)
}

export function useLeaveRequestViewModel({
  getEntitlementUseCase,
  submitLeaveUseCase,
  validator = new LeaveRequestValidatorService(), // default injection
}: LeaveRequestViewModelDeps) {
  const [requestedDays, setRequestedDays] = useState(0);

  const { data: entitlement } = useQuery({
    queryKey: ['leaveEntitlement'],
    queryFn: () => getEntitlementUseCase.execute({}),
  });

  // Hook is a thin orchestrator — validation is delegated to Domain Service
  const validationResult = entitlement
    ? validator.validate(entitlement, requestedDays, new Date())
    : 'valid';

  const submitMutation = useMutation({
    mutationFn: (payload: SubmitLeaveRequestPayload) => {
      if (!entitlement) throw new Error('No entitlement loaded');
      return submitLeaveUseCase.execute({ entitlement, payload });
    },
  });

  const handleDaysChange = useCallback((days: number) => {
    setRequestedDays(days);
  }, []);

  return {
    entitlement,
    validationResult,
    requestedDays,
    isSubmitting: submitMutation.isPending,
    submitError: submitMutation.error?.message ?? null,
    handleDaysChange,
    handleSubmit: submitMutation.mutate,
  };
}
```

## React Component (View) <!-- 65 -->

Components are dumb renderers. They receive state and callbacks from the ViewModel hook and render UI.

```typescript
// presentation/features/employee-list/EmployeeListView.tsx
'use client';

import { useEmployeeListViewModel } from './useEmployeeListViewModel';
import { useDI } from '@/di/DIContext';
import { EmployeeRow } from './components/EmployeeRow';
import { LoadingView } from '@/presentation/common/LoadingView';
import { ErrorView } from '@/presentation/common/ErrorView';
import { PaginatedResult } from '@/domain/entities/PaginatedResult';
import { Employee } from '@/domain/entities/Employee';

interface Props {
  // Optional: pre-fetched by the Server Component page — seeds TanStack Query cache
  initialData?: PaginatedResult<Employee>;
}

export function EmployeeListView({ initialData }: Props) {
  const { getEmployeesUseCase, deleteEmployeeUseCase } = useDI();

  const {
    employees,
    isLoading,
    isError,
    errorMessage,
    searchQuery,
    handleEmployeeClick,
    handleDeleteEmployee,
    handleSearchChange,
    handleRefresh,
  } = useEmployeeListViewModel({ getEmployeesUseCase, deleteEmployeeUseCase, initialData });

  if (isLoading) return <LoadingView />;
  if (isError) return <ErrorView message={errorMessage ?? 'Something went wrong'} onRetry={handleRefresh} />;

  return (
    <div className="flex flex-col gap-4">
      <input
        type="search"
        value={searchQuery}
        onChange={(e) => handleSearchChange(e.target.value)}
        placeholder="Search employees..."
        className="input input-bordered w-full"
      />
      <ul className="divide-y divide-base-200">
        {employees.map((employee) => (
          <EmployeeRow
            key={employee.id}
            employee={employee}
            onClick={() => handleEmployeeClick(employee)}
            onDelete={() => handleDeleteEmployee(employee)}
          />
        ))}
      </ul>
    </div>
  );
}
```

---

## Atomic Design within the Presentation Layer <!-- 19 -->

Clean Architecture owns the **vertical** slice (domain → data → presentation).
Atomic Design owns the **horizontal** slice (how components are structured *within* presentation).

| Atomic Level | Location | Description | Example |
|---|---|---|---|
| Atoms | `shared/presentation/common/atoms/` | Indivisible elements. No business logic, primitive props only | `ErrorBanner`, `ProgressBar`, `Badge` |
| Molecules | `shared/presentation/common/molecules/` | Small groups of atoms forming a meaningful unit | `PageHeader`, `PageShell` |
| Organisms | `features/{name}/presentation/organisms/` | Complex, feature-aware sections. May accept domain entities as props | `TransactionListItem`, `CategoryItemEditor` |
| Views (Pages) | `features/{name}/presentation/` | Connects ViewModel hook to organisms. No direct API calls | `TransactionsView`, `DashboardView` |

**Rules:**
1. Atoms and molecules accept only primitive props (`string`, `number`, `boolean`, `ReactNode`). No domain entities, no use case hooks.
2. Organisms may accept domain entities as props — they render, but do not fetch.
3. Only Views call `useDI()` and ViewModel hooks — they pass data down to organisms.
4. Shared atoms/molecules live in `src/shared/presentation/common/`. Feature-specific organisms live inside their own feature slice.
5. A component that is used in ≥2 features must be promoted to `shared/presentation/common/`.

## View Data Transformer Pattern <!-- 53 -->

Domain objects return structured, semantic data. The presentation layer is responsible for converting that data into display-ready values like CSS class strings, labels, and icons. **Never put Tailwind class strings or locale-formatted display strings inside domain services or use cases.**

**Pattern: status enum → display config map**

When a domain service communicates visual severity (progress state, health status), it returns a typed status string. The organism (or a shared presentation util if used in ≥2 places) defines a lookup map from that status to CSS classes.

```typescript
// domain/services/BudgetProgressService.ts — domain returns semantic status
export type BudgetStatus = 'on-track' | 'at-risk' | 'over';

export interface BudgetProgressData {
  readonly percent: number;
  readonly remaining: number;
  readonly isOverrun: boolean;
  readonly status: BudgetStatus;   // semantic, not visual
}
```

```typescript
// presentation/organisms/CategoryBreakdownSection.tsx — presentation maps to CSS
import type { BudgetStatus } from '@/features/dashboard/domain/services/BudgetProgressService';

const STATUS_COLOR: Record<BudgetStatus, string> = {
  'on-track': 'bg-emerald-400',
  'at-risk':  'bg-yellow-400',
  'over':     'bg-red-400',
};

const STATUS_TEXT: Record<BudgetStatus, string> = {
  'on-track': 'text-emerald-600 dark:text-emerald-300',
  'at-risk':  'text-yellow-600 dark:text-yellow-300',
  'over':     'text-red-600 dark:text-red-300',
};

// Usage in JSX:
<div className={STATUS_COLOR[progress.status]} />
<span className={STATUS_TEXT[progress.status]} />
```

**Placement rule:** If the same config map is needed in ≥2 organisms, extract it to `src/shared/presentation/common/utils/[feature]StatusConfig.ts`.

**Domain vs presentation boundary:**

| Concern | Layer | Example |
|---------|-------|---------|
| Severity classification | Domain | `status: 'over' \| 'at-risk' \| 'on-track'` |
| CSS class strings | Presentation | `'bg-red-400'`, `'text-red-600 dark:text-red-300'` |
| Locale-formatted numbers | Presentation | `'Rp 1.2jt'` via `formatCompactCurrency` |
| Raw numbers / booleans | Domain | `remaining: number`, `isOverrun: boolean` |
| User-facing message strings | Presentation | `'The requested resource was not found.'` |

## Server-Side ViewModel (Pure Function) <!-- 87 -->

When a page is a **Server Component** (`async page.tsx`), data is fetched server-side and there are no React hooks. The ViewModel is a **pure function** instead of a hook.

**Naming:** `build[Feature]ViewModel` — the `build*` prefix signals "not a hook, not stateful"
**Location:** `src/presentation/features/[feature]/build[Feature]ViewModel.ts`
**Runtime:** Isomorphic — runs on server at request time; trivially testable as a pure function

```typescript
// presentation/features/career-page/buildCareerPageViewModel.ts
import type { Company } from '@/domain/entities/Company';
import type { Job } from '@/domain/entities/Job';

export interface CareerPageViewModelInput {
  company: Company;
  jobs: Job[];
}

export interface CareerPageViewModel {
  company: Company;
  jobs: Job[];
  isHiring: boolean;
  featuredJobs: Job[];
}

export function buildCareerPageViewModel(input: CareerPageViewModelInput): CareerPageViewModel {
  return {
    company: input.company,
    jobs: input.jobs,
    isHiring: input.company.siteStatus === 'active',
    featuredJobs: input.jobs.filter((j) => j.isFeatured),
  };
}
```

**Call site — `async` Server Component page:**

```typescript
// app/careers/[slug]/page.tsx
import { getCompanyUseCase, getJobsUseCase } from '@/di/container.server';
import { buildCareerPageViewModel } from '@/presentation/features/career-page/buildCareerPageViewModel';
import { CareerPageView } from '@/presentation/features/career-page/CareerPageView';

export default async function CareerPage({ params }: { params: { slug: string } }) {
  const [company, jobs] = await Promise.all([
    getCompanyUseCase().execute({ slug: params.slug }),
    getJobsUseCase().execute({ companySlug: params.slug }),
  ]);
  const viewModel = buildCareerPageViewModel({ company, jobs });
  return <CareerPageView viewModel={viewModel} />;
}
```

**View receives the pre-built ViewModel as a prop:**

```typescript
// presentation/features/career-page/CareerPageView.tsx
// Add 'use client' only if interactivity is needed
import type { CareerPageViewModel } from './buildCareerPageViewModel';

export function CareerPageView({ viewModel }: { viewModel: CareerPageViewModel }) {
  const { company, isHiring, featuredJobs } = viewModel;
  return ( /* render */ );
}
```

**Pattern selection guide:**

| Scenario | Pattern |
|----------|---------|
| Server Component, read-only | `build*ViewModel` pure function |
| Client Component, live data / caching | `use*ViewModel` hook + TanStack Query |
| Client Component, mutations (full-stack) | `use*ViewModel` hook + Server Actions |
| RSC page + client interactivity | `build*ViewModel` → pass as `initialData` to `use*ViewModel` hook |

**Rules:**
- `build*ViewModel` is a **pure function** — no hooks, no async, no side effects
- Input: domain entities only
- Output: a plain serializable object (safe to cross the Server → Client boundary)
- Derived fields (computed from entities) belong here, not inside the component
- No display formatting (CSS classes, locale strings) — those stay in the component or organism

---


---

## Shared Component Paths <!-- 11 -->

When running a Component Reuse Check, search these locations for existing reusable components:

| Atomic level | Path | File pattern |
|---|---|---|
| Atoms (primitive, no business logic) | `shared/presentation/common/atoms/` | `*.tsx` |
| Molecules (small groups of atoms) | `shared/presentation/common/molecules/` | `*.tsx` |
| Organisms (feature-aware, accepts domain entities) | `features/*/presentation/organisms/` | `*.tsx` |

**Search strategy:** Grep for the component concept (e.g. `"Card"`, `"Banner"`, `"Avatar"`, `"EmptyState"`) across atoms and molecules first — these are cross-feature safe. Only search organisms within the same feature. A component found at atom or molecule level should always be preferred over creating a new one.
