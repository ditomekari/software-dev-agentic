# Web — Testing

> Concepts and invariants: `reference/code-architecture/testing-theory.md`. This file covers TypeScript syntax and web-specific patterns.

## Test Pyramid <!-- 24 -->

```
         ┌──────────────────┐
         │   E2E Tests      │  (Playwright — few, critical paths)
         │   Playwright     │
         └────────┬─────────┘
                  │
         ┌────────▼─────────┐
         │ Integration Tests │  (React Testing Library — component + hook tests)
         │ React Test Lib   │
         └────────┬─────────┘
                  │
    ┌─────────────▼────────────────┐
    │       Unit Tests              │  (Vitest — Services, Mappers, UseCases, hooks)
    │  Services / Mappers / Repos  │
    └──────────────────────────────┘
```

**Mocking strategy:**
- **MSW (Mock Service Worker)** for HTTP mocking in integration tests
- **Manual mocks** for repositories and use cases in unit tests
- **`vi.fn()`** for simple dependency mocking

## Service Tests <!-- 55 -->

Highest priority. Pure input → output, no mocks needed.

```typescript
// __tests__/domain/services/LeaveBalanceCalculator.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { LeaveBalanceCalculatorService } from '@/domain/services/LeaveBalanceCalculator';

describe('LeaveBalanceCalculatorService', () => {
  let sut: LeaveBalanceCalculatorService;

  beforeEach(() => {
    sut = new LeaveBalanceCalculatorService();
  });

  it('returns correct remaining balance with no pending requests', () => {
    const entitlement = { annualDays: 12, usedDays: 5, pendingRequests: [] };
    expect(sut.remainingBalance(entitlement)).toBe(7);
  });

  it('caps remaining balance at zero when over-committed', () => {
    const entitlement = {
      annualDays: 12,
      usedDays: 10,
      pendingRequests: Array(5).fill({ status: 'pending' }),
    };
    expect(sut.remainingBalance(entitlement)).toBe(0);
  });

  it('returns true when balance is sufficient', () => {
    const entitlement = { annualDays: 12, usedDays: 5, pendingRequests: [] };
    expect(sut.isSufficient(entitlement, 3)).toBe(true);
  });
});

describe('LeaveRequestValidatorService', () => {
  it('returns insufficientBalance when balance is too low', () => {
    const validator = new LeaveRequestValidatorService();
    const entitlement = { annualDays: 5, usedDays: 5, pendingRequests: [] };
    expect(
      validator.validate(entitlement, 3, new Date(Date.now() + 86400_000))
    ).toBe('insufficientBalance');
  });

  it('returns pastDateNotAllowed when date is in the past', () => {
    const validator = new LeaveRequestValidatorService();
    const entitlement = { annualDays: 12, usedDays: 0, pendingRequests: [] };
    expect(
      validator.validate(entitlement, 1, new Date(2000, 0, 1))
    ).toBe('pastDateNotAllowed');
  });
});
```

## Presenter Tests <!-- 52 -->

```typescript
// __tests__/presentation/hooks/useEmployeeListViewModel.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { useEmployeeListViewModel } from '@/presentation/features/employee-list/useEmployeeListViewModel';
import { createQueryClientWrapper } from '@/__tests__/utils/queryClientWrapper';

const mockGetEmployeesUseCase = {
  execute: vi.fn(),
};

const mockDeleteEmployeeUseCase = {
  execute: vi.fn(),
};

describe('useEmployeeListViewModel', () => {
  beforeEach(() => vi.clearAllMocks());

  it('loads employees on mount', async () => {
    const employees = [{ id: '1', name: 'John', email: 'john@example.com', department: { id: 'd1', name: 'Eng', headCount: 5 }, joinDate: new Date() }];
    mockGetEmployeesUseCase.execute.mockResolvedValue({ items: employees, totalCount: 1, currentPage: 1, totalPages: 1 });

    const { result } = renderHook(
      () => useEmployeeListViewModel({
        getEmployeesUseCase: mockGetEmployeesUseCase,
        deleteEmployeeUseCase: mockDeleteEmployeeUseCase,
      }),
      { wrapper: createQueryClientWrapper() }
    );

    await waitFor(() => {
      expect(result.current.employees).toEqual(employees);
    });
  });

  it('updates search query on handleSearchChange', () => {
    const { result } = renderHook(
      () => useEmployeeListViewModel({
        getEmployeesUseCase: mockGetEmployeesUseCase,
        deleteEmployeeUseCase: mockDeleteEmployeeUseCase,
      }),
      { wrapper: createQueryClientWrapper() }
    );

    result.current.handleSearchChange('John');
    expect(result.current.searchQuery).toBe('John');
  });
});
```

## Repository Tests <!-- 45 -->

With injectable mappers, you can isolate repository logic from mapping logic:

```typescript
// __tests__/data/repositories/EmployeeRepositoryImpl.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { EmployeeRepositoryImpl } from '@/data/repositories/EmployeeRepositoryImpl';

const mockRemoteDataSource = {
  fetchEmployee: vi.fn(),
  fetchEmployees: vi.fn(),
  updateEmployee: vi.fn(),
  deleteEmployee: vi.fn(),
};

const mockMapper = {
  toDomain: vi.fn(),
  toRequest: vi.fn(),
};

describe('EmployeeRepositoryImpl', () => {
  let sut: EmployeeRepositoryImpl;

  beforeEach(() => {
    vi.clearAllMocks();
    sut = new EmployeeRepositoryImpl(mockRemoteDataSource, mockMapper);
  });

  it('calls data source and mapper on getEmployee', async () => {
    const dto = { id: '1', full_name: 'John', email_address: 'john@example.com', department: { id: 'd1', name: 'Eng' }, joined_at: '2024-01-01T00:00:00Z' };
    const entity = { id: '1', name: 'John', email: 'john@example.com', department: { id: 'd1', name: 'Eng', headCount: 0 }, joinDate: new Date() };

    mockRemoteDataSource.fetchEmployee.mockResolvedValue(dto);
    mockMapper.toDomain.mockReturnValue(entity);

    const result = await sut.getEmployee('1');

    expect(mockRemoteDataSource.fetchEmployee).toHaveBeenCalledWith('1');
    expect(mockMapper.toDomain).toHaveBeenCalledWith(dto);
    expect(result).toEqual(entity);
  });
});
```

## Mapper Tests <!-- 53 -->

Pure input → output, no mocks needed:

```typescript
// __tests__/data/mappers/EmployeeMapper.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { EmployeeMapperImpl } from '@/data/mappers/EmployeeMapper';

describe('EmployeeMapperImpl', () => {
  let sut: EmployeeMapperImpl;

  beforeEach(() => {
    sut = new EmployeeMapperImpl();
  });

  it('maps all fields correctly', () => {
    const dto = {
      id: '1',
      full_name: 'John Doe',
      email_address: 'john@example.com',
      department: { id: 'd1', name: 'Engineering', head_count: 10 },
      joined_at: '2024-01-01T00:00:00Z',
    };

    const employee = sut.toDomain(dto);

    expect(employee.id).toBe('1');
    expect(employee.name).toBe('John Doe');
    expect(employee.email).toBe('john@example.com');
    expect(employee.department.id).toBe('d1');
    expect(employee.department.name).toBe('Engineering');
    expect(employee.department.headCount).toBe(10);
  });

  it('uses injected child mapper for department', () => {
    const mockDeptMapper = { toDomain: vi.fn().mockReturnValue({ id: 'mock', name: 'Mocked', headCount: 0 }) };
    const sut = new EmployeeMapperImpl(mockDeptMapper);

    const dto = {
      id: '1', full_name: 'John', email_address: 'john@test.com',
      department: { id: 'd1', name: 'Eng', head_count: 5 },
      joined_at: '2024-01-01T00:00:00Z',
    };

    const employee = sut.toDomain(dto);
    expect(employee.department.name).toBe('Mocked'); // proves child mapper was used
    expect(mockDeptMapper.toDomain).toHaveBeenCalledTimes(1);
  });
});
```

---
