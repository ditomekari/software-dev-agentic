# Web — Domain Layer

> Concepts and invariants: `reference/code-architecture/domain-theory.md`. This file covers TypeScript syntax and web-specific patterns.

## Dependency Rule <!-- 14 -->

Domain is the innermost layer — it imports nothing from outer layers.

**Allowed:** TypeScript built-in types (`string`, `number`, `boolean`, `Date`, `Record`, `Promise`), pure utility types defined within the domain layer itself.

**Forbidden:**
- `import axios` / `import fetch` — HTTP clients belong in data
- `import React` / `import { useXxx } from 'react'` or any Next.js import — UI belongs in presentation
- Any data-layer type — no DTO, DataSource, or repository implementation import
- `import { useState } from 'react'` or any hook — domain must be framework-free TypeScript

---

## Entities <!-- 34 -->

```typescript
// domain/entities/Employee.ts
export interface Employee {
  readonly id: string;
  readonly name: string;
  readonly email: string;
  readonly department: Department;
  readonly joinDate: Date;
}

// domain/entities/Department.ts
export interface Department {
  readonly id: string;
  readonly name: string;
  readonly headCount: number;
}

// domain/entities/PaginatedResult.ts
export interface PaginatedResult<T> {
  readonly items: T[];
  readonly totalCount: number;
  readonly currentPage: number;
  readonly totalPages: number;
}
```

**Rules:**
- No framework imports (`react`, `next`, etc.)
- Readonly properties — entities are immutable value objects
- Plain TypeScript interfaces — no class inheritance, no decorators
- Represent business concepts, not API shapes

## Repository Interfaces <!-- 22 -->

```typescript
// domain/repositories/EmployeeRepository.ts
export interface EmployeeRepository {
  getEmployee(id: string): Promise<Employee>;
  getEmployees(params: {
    page: number;
    limit: number;
    departmentId?: string;
    searchQuery?: string;
  }): Promise<PaginatedResult<Employee>>;
  updateEmployee(employee: Employee): Promise<Employee>;
  deleteEmployee(id: string): Promise<void>;
}
```

**Rules:**
- Always return `Promise<T>` — async by default
- Return domain entities, never DTOs
- Interface must be in the Domain layer — implementations go in Data

## Use Cases <!-- 92 -->

Each UseCase has a **Params** type that bundles all input parameters:

```typescript
// domain/use-cases/employee/GetEmployeeUseCase.ts
export interface GetEmployeeUseCaseParams {
  employeeId: string;
}

export interface GetEmployeeUseCase {
  execute(params: GetEmployeeUseCaseParams): Promise<Employee>;
}

export class GetEmployeeUseCaseImpl implements GetEmployeeUseCase {
  constructor(private readonly repository: EmployeeRepository) {}

  async execute(params: GetEmployeeUseCaseParams): Promise<Employee> {
    return this.repository.getEmployee(params.employeeId);
  }
}
```

```typescript
// domain/use-cases/employee/GetEmployeesUseCase.ts
export interface GetEmployeesUseCaseParams {
  page: number;
  limit: number;
  departmentId?: string;
  searchQuery?: string;
}

export interface GetEmployeesUseCase {
  execute(params: GetEmployeesUseCaseParams): Promise<PaginatedResult<Employee>>;
}

export class GetEmployeesUseCaseImpl implements GetEmployeesUseCase {
  constructor(private readonly repository: EmployeeRepository) {}

  async execute(params: GetEmployeesUseCaseParams): Promise<PaginatedResult<Employee>> {
    return this.repository.getEmployees(params);
  }
}
```

For **write operations** (POST/PUT), the Params type separates identifiers from the payload:

```typescript
// domain/use-cases/employee/UpdateEmployeeUseCase.ts
export interface UpdateEmployeeUseCasePayload {
  name: string;
  email: string;
  departmentId: string;
}

export interface UpdateEmployeeUseCaseParams {
  employeeId: string;   // path identifier
  payload: UpdateEmployeeUseCasePayload; // request body
}

export interface UpdateEmployeeUseCase {
  execute(params: UpdateEmployeeUseCaseParams): Promise<Employee>;
}

export class UpdateEmployeeUseCaseImpl implements UpdateEmployeeUseCase {
  constructor(private readonly repository: EmployeeRepository) {}

  async execute(params: UpdateEmployeeUseCaseParams): Promise<Employee> {
    const updated: Employee = {
      id: params.employeeId,
      name: params.payload.name,
      email: params.payload.email,
      department: { id: params.payload.departmentId, name: '', headCount: 0 },
      joinDate: new Date(),
    };
    return this.repository.updateEmployee(updated);
  }
}
```

**Params pattern summary:**

| Operation | Params structure |
|-----------|-----------------|
| GET (single) | `{ id }` |
| GET (list) | `{ page, limit, filters... }` |
| POST | `{ payload: { fields... } }` |
| PUT | `{ id, payload: { fields... } }` |
| DELETE | `{ id }` |

**Naming convention:** `[Verb][Feature]UseCase` — e.g., `GetEmployeeUseCase`, `SubmitAttendanceUseCase`, `CalculateLeaveBalanceUseCase`

## Domain Services <!-- 137 -->

Pure business decisions — no I/O, no side effects, no async. See extraction rules in `reference/code-architecture/domain-theory.md`.

```typescript
// domain/services/LeaveBalanceCalculator.ts
import { LeaveEntitlement } from '../entities/LeaveEntitlement';

export interface LeaveBalanceCalculator {
  remainingBalance(entitlement: LeaveEntitlement): number;
  isSufficient(entitlement: LeaveEntitlement, requestedDays: number): boolean;
}

export class LeaveBalanceCalculatorService implements LeaveBalanceCalculator {
  remainingBalance(entitlement: LeaveEntitlement): number {
    const pendingDays = entitlement.pendingRequests.filter(
      (r) => r.status === 'pending'
    ).length;
    return Math.max(0, entitlement.annualDays - entitlement.usedDays - pendingDays);
  }

  isSufficient(entitlement: LeaveEntitlement, requestedDays: number): boolean {
    return this.remainingBalance(entitlement) >= requestedDays;
  }
}
```

```typescript
// domain/services/LeaveRequestValidator.ts
import { LeaveEntitlement } from '../entities/LeaveEntitlement';
import { LeaveBalanceCalculator, LeaveBalanceCalculatorService } from './LeaveBalanceCalculator';

export type LeaveValidationResult =
  | 'valid'
  | 'insufficientBalance'
  | 'pastDateNotAllowed';

export interface LeaveRequestValidator {
  validate(
    entitlement: LeaveEntitlement,
    requestedDays: number,
    requestDate: Date
  ): LeaveValidationResult;
}

export class LeaveRequestValidatorService implements LeaveRequestValidator {
  constructor(
    private readonly balanceCalculator: LeaveBalanceCalculator = new LeaveBalanceCalculatorService()
  ) {}

  validate(
    entitlement: LeaveEntitlement,
    requestedDays: number,
    requestDate: Date
  ): LeaveValidationResult {
    if (!this.balanceCalculator.isSufficient(entitlement, requestedDays)) {
      return 'insufficientBalance';
    }
    if (requestDate <= new Date()) {
      return 'pastDateNotAllowed';
    }
    return 'valid';
  }
}
```

**UseCase calling a Service:**

```typescript
// domain/use-cases/leave/SubmitLeaveRequestUseCase.ts
export interface SubmitLeaveRequestPayload {
  leaveTypeId: string;
  startDate: Date;
  endDate: Date;
  days: number;
  reason?: string;
}

export interface SubmitLeaveRequestParams {
  entitlement: LeaveEntitlement; // context for validation
  payload: SubmitLeaveRequestPayload;
}

export class SubmitLeaveRequestUseCaseImpl {
  constructor(
    private readonly repository: LeaveRepository,
    private readonly validator: LeaveRequestValidator = new LeaveRequestValidatorService()
  ) {}

  async execute(params: SubmitLeaveRequestParams): Promise<Leave> {
    const result = this.validator.validate(
      params.entitlement,
      params.payload.days,
      params.payload.startDate
    );

    if (result !== 'valid') {
      throw new DomainError('validationFailed', { field: 'leave', reason: result });
    }

    return this.repository.submitLeaveRequest(params.payload);
  }
}
```

**What a Service must NOT return:**

| ❌ Violation | ✅ Correct alternative |
|---|---|
| `compactLabel: "71.8K left"` (formatted string) | `remaining: number` + `isOverrun: boolean` |
| `colorClass: "bg-red-400"` (CSS class name from outside domain) | `status: 'on-track' \| 'at-risk' \| 'over'` |
| `displayText: "Over by 71000"` via a locale formatter import | `remaining: number` (let presentation format it) |

Domain services return **structured data**. The presentation layer converts that data into display strings, CSS classes, and formatted labels. If your service imports anything from `shared/core/utils/format*`, it has crossed the boundary.

**When to use a Service vs keeping logic inline:**

| Scenario | Approach |
|----------|----------|
| Simple condition (1-3 lines) | Keep inline in UseCase |
| Complex multi-step validation | Extract to Service |
| Reused across multiple UseCases | Extract to Service |
| Needs independent unit testing | Extract to Service |

**Where to place it:**

| Scenario | Path |
|----------|------|
| Logic belongs to one feature's concept | `src/features/[feature]/domain/services/` |
| Used by ≥2 features | `src/shared/domain/services/` |

Place the service in the feature that *owns the concept*, not the feature that consumes it.
A service consumed only by `dashboard` but computing `budget` math belongs in `budget-settings`.
A service computing only dashboard display logic belongs in `dashboard`.

**Naming convention:** `[Feature][Noun]` interface + `[Feature][Noun]Service` class — e.g., `LeaveBalanceCalculator` / `LeaveBalanceCalculatorService`

## Domain Errors <!-- 47 -->

```typescript
// domain/errors/DomainError.ts
export type DomainErrorCode =
  | 'notFound'
  | 'validationFailed'
  | 'unauthorized'
  | 'networkUnavailable'
  | 'serverError'
  | 'unknown';

export class DomainError extends Error {
  readonly code: DomainErrorCode;
  readonly context?: Record<string, unknown>;

  constructor(code: DomainErrorCode, context?: Record<string, unknown>) {
    super(code);
    this.name = 'DomainError';
    this.code = code;
    this.context = context;
  }

  static notFound(resource: string, id: string): DomainError {
    return new DomainError('notFound', { resource, id });
  }

  static validationFailed(field: string, reason: string): DomainError {
    return new DomainError('validationFailed', { field, reason });
  }

  static unauthorized(): DomainError {
    return new DomainError('unauthorized');
  }

  static networkUnavailable(): DomainError {
    return new DomainError('networkUnavailable');
  }

  static serverError(message: string): DomainError {
    return new DomainError('serverError', { message });
  }
}
```

---

## Creation Order <!-- 14 -->

When building a new feature's domain layer, create files in this sequence:

```
1. domain/entities/[Feature].ts                              ← Entity (readonly interface)
2. domain/repositories/[Feature]Repository.ts               ← Repository interface
3. domain/use-cases/[feature]/Get[Feature]UseCase.ts
   domain/use-cases/[feature]/Update[Feature]UseCase.ts
   ...                                                       ← Use Case(s) (interface + impl)
4. domain/services/[Feature][Noun].ts                       ← Domain Service (only if needed)
```

Never create a use case before the repository interface it depends on.
