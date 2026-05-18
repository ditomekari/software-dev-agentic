# Web — Data Layer

> Concepts and invariants: `reference/code-architecture/data-theory.md`. This file covers TypeScript syntax and web-specific patterns.

Implements Domain interfaces. Handles all I/O: network, storage, caching.

## DTOs <!-- 43 -->

Network response models. Separate from domain entities.

```typescript
// data/dtos/DepartmentDTO.ts
export interface DepartmentDTO {
  id: string;
  name: string;
  head_count?: number;
}

// data/dtos/EmployeeDTO.ts
export interface EmployeeDTO {
  id: string;
  full_name: string;
  email_address: string;
  department: DepartmentDTO;  // nested DTO — mapped by DepartmentMapper
  joined_at: string;          // ISO 8601 string
}

// data/dtos/PaginatedDTO.ts
export interface PaginatedDTO<T> {
  items: T[];
  total_count: number;
  current_page: number;
  total_pages: number;
}

// data/dtos/APIResponse.ts
export interface APIResponse<T> {
  data: T;
  message?: string;
  success: boolean;
}
```

**Rules:**
- DTOs use snake_case to match API JSON keys (convert to camelCase in mappers)
- DTOs are plain interfaces — no methods, no classes
- DTOs never escape the Data layer
- Nested API objects get their own DTO + Mapper pair

## Mappers <!-- 99 -->

Transform DTOs to domain entities and vice versa. **Each DTO-Entity pair gets its own dedicated mapper.** Mappers are interface-based and injectable — this lets you mock them in repository tests and swap mapping strategies when needed.

```typescript
// data/mappers/DepartmentMapper.ts
import { Department } from '../../domain/entities/Department';
import { DepartmentDTO } from '../dtos/DepartmentDTO';

export interface DepartmentMapper {
  toDomain(dto: DepartmentDTO): Department;
}

export class DepartmentMapperImpl implements DepartmentMapper {
  toDomain(dto: DepartmentDTO): Department {
    return {
      id: dto.id,
      name: dto.name,
      headCount: dto.head_count ?? 0,
    };
  }
}
```

```typescript
// data/mappers/EmployeeMapper.ts
import { Employee } from '../../domain/entities/Employee';
import { EmployeeDTO } from '../dtos/EmployeeDTO';
import { DepartmentMapper, DepartmentMapperImpl } from './DepartmentMapper';

export interface UpdateEmployeeRequest {
  full_name: string;
  email_address: string;
  department_id: string;
}

export interface EmployeeMapper {
  toDomain(dto: EmployeeDTO): Employee;
  toRequest(employee: Employee): UpdateEmployeeRequest;
}

export class EmployeeMapperImpl implements EmployeeMapper {
  constructor(
    private readonly departmentMapper: DepartmentMapper = new DepartmentMapperImpl()
  ) {}

  toDomain(dto: EmployeeDTO): Employee {
    return {
      id: dto.id,
      name: dto.full_name,
      email: dto.email_address,
      department: this.departmentMapper.toDomain(dto.department), // delegates to child mapper
      joinDate: new Date(dto.joined_at),
    };
  }

  toRequest(employee: Employee): UpdateEmployeeRequest {
    return {
      full_name: employee.name,
      email_address: employee.email,
      department_id: employee.department.id,
    };
  }
}
```

```typescript
// data/mappers/ErrorMapper.ts
import { DomainError } from '../../domain/errors/DomainError';
import { NetworkError } from '../networking/NetworkError';

export interface ErrorMapper {
  toDomain(error: NetworkError): DomainError;
}

export class ErrorMapperImpl implements ErrorMapper {
  toDomain(error: NetworkError): DomainError {
    switch (error.type) {
      case 'httpError':
        if (error.statusCode === 401) return DomainError.unauthorized();
        if (error.statusCode === 404) return DomainError.notFound('Resource', '');
        if (error.statusCode >= 500) return DomainError.serverError(error.message ?? 'Server error');
        return new DomainError('unknown', { statusCode: error.statusCode });
      case 'noConnection':
      case 'timeout':
        return DomainError.networkUnavailable();
      default:
        return new DomainError('unknown', { message: error.message });
    }
  }
}
```

**Rules:**
- One mapper per DTO-Entity pair: `EmployeeMapper`, `DepartmentMapper`, `LeaveMapper`, etc.
- Interface-based: each mapper has a `[Name]Mapper` interface and a `[Name]MapperImpl` class
- Mappers compose via injection: `EmployeeMapperImpl` receives `DepartmentMapper` in its constructor
- Default parameter injection: `constructor(departmentMapper = new DepartmentMapperImpl())` — overridable in tests

## Data Sources <!-- 49 -->

Abstract the data origin (remote API, local storage, cache).

```typescript
// data/data-sources/remote/EmployeeRemoteDataSource.ts
import { EmployeeDTO } from '../../dtos/EmployeeDTO';
import { PaginatedDTO } from '../../dtos/PaginatedDTO';
import { UpdateEmployeeRequest } from '../../mappers/EmployeeMapper';

export interface EmployeeRemoteDataSource {
  fetchEmployee(id: string): Promise<EmployeeDTO>;
  fetchEmployees(page: number, limit: number): Promise<PaginatedDTO<EmployeeDTO>>;
  updateEmployee(id: string, request: UpdateEmployeeRequest): Promise<EmployeeDTO>;
  deleteEmployee(id: string): Promise<void>;
}

export class EmployeeRemoteDataSourceImpl implements EmployeeRemoteDataSource {
  constructor(private readonly client: HTTPClient) {}

  async fetchEmployee(id: string): Promise<EmployeeDTO> {
    const response = await this.client.get<APIResponse<EmployeeDTO>>(
      `/api/v1/employees/${id}`
    );
    return response.data;
  }

  async fetchEmployees(page: number, limit: number): Promise<PaginatedDTO<EmployeeDTO>> {
    const response = await this.client.get<APIResponse<PaginatedDTO<EmployeeDTO>>>(
      '/api/v1/employees',
      { params: { page, limit } }
    );
    return response.data;
  }

  async updateEmployee(id: string, request: UpdateEmployeeRequest): Promise<EmployeeDTO> {
    const response = await this.client.put<APIResponse<EmployeeDTO>>(
      `/api/v1/employees/${id}`,
      request
    );
    return response.data;
  }

  async deleteEmployee(id: string): Promise<void> {
    await this.client.delete(`/api/v1/employees/${id}`);
  }
}
```

## Repository Implementation <!-- 69 -->

Repositories receive mappers through injection — this lets you mock mappers in tests and isolate repository logic.

```typescript
// data/repositories/EmployeeRepositoryImpl.ts
import { EmployeeRepository } from '../../domain/repositories/EmployeeRepository';
import { Employee } from '../../domain/entities/Employee';
import { PaginatedResult } from '../../domain/entities/PaginatedResult';
import { EmployeeRemoteDataSource } from '../data-sources/remote/EmployeeRemoteDataSource';
import { EmployeeMapper, EmployeeMapperImpl } from '../mappers/EmployeeMapper';
import { ErrorMapper, ErrorMapperImpl } from '../mappers/ErrorMapper';
import { NetworkError } from '../networking/NetworkError';

export class EmployeeRepositoryImpl implements EmployeeRepository {
  constructor(
    private readonly remoteDataSource: EmployeeRemoteDataSource,
    private readonly mapper: EmployeeMapper = new EmployeeMapperImpl(),
    private readonly errorMapper: ErrorMapper = new ErrorMapperImpl()
  ) {}

  async getEmployee(id: string): Promise<Employee> {
    try {
      const dto = await this.remoteDataSource.fetchEmployee(id);
      return this.mapper.toDomain(dto);
    } catch (error) {
      throw this.errorMapper.toDomain(error as NetworkError);
    }
  }

  async getEmployees(params: {
    page: number;
    limit: number;
    departmentId?: string;
    searchQuery?: string;
  }): Promise<PaginatedResult<Employee>> {
    try {
      const dto = await this.remoteDataSource.fetchEmployees(params.page, params.limit);
      return {
        items: dto.items.map((item) => this.mapper.toDomain(item)),
        totalCount: dto.total_count,
        currentPage: dto.current_page,
        totalPages: dto.total_pages,
      };
    } catch (error) {
      throw this.errorMapper.toDomain(error as NetworkError);
    }
  }

  async updateEmployee(employee: Employee): Promise<Employee> {
    try {
      const request = this.mapper.toRequest(employee);
      const dto = await this.remoteDataSource.updateEmployee(employee.id, request);
      return this.mapper.toDomain(dto);
    } catch (error) {
      throw this.errorMapper.toDomain(error as NetworkError);
    }
  }

  async deleteEmployee(id: string): Promise<void> {
    try {
      await this.remoteDataSource.deleteEmployee(id);
    } catch (error) {
      throw this.errorMapper.toDomain(error as NetworkError);
    }
  }
}
```

## HTTP Client <!-- 264 -->

Uses **Axios** with **axios-retry**. The `HTTPClient` interface keeps the Data layer decoupled from Axios internals — swap the implementation without touching repositories or data sources.

```typescript
// data/networking/HTTPClient.ts
export interface RequestOptions {
  params?: Record<string, unknown>;
  headers?: Record<string, string>;
  signal?: AbortSignal;
}

export interface HTTPClient {
  get<T>(path: string, options?: RequestOptions): Promise<T>;
  post<T>(path: string, body: unknown, options?: RequestOptions): Promise<T>;
  put<T>(path: string, body: unknown, options?: RequestOptions): Promise<T>;
  patch<T>(path: string, body: unknown, options?: RequestOptions): Promise<T>;
  delete<T>(path: string, options?: RequestOptions): Promise<T>;
}

// data/networking/NetworkError.ts
export type NetworkErrorType =
  | 'httpError'
  | 'noConnection'
  | 'timeout'
  | 'parseError'
  | 'unknown';

export class NetworkError extends Error {
  readonly type: NetworkErrorType;
  readonly statusCode?: number;

  constructor(type: NetworkErrorType, message?: string, statusCode?: number) {
    super(message ?? type);
    this.name = 'NetworkError';
    this.type = type;
    this.statusCode = statusCode;
  }
}
```

### Token Provider & Refresher Interfaces

```typescript
// data/networking/TokenProvider.ts
export interface TokenProvider {
  getAccessToken(): string | null;
}

export interface TokenRefresher {
  refreshToken(): Promise<void>;
}

export interface TokenStorage extends TokenProvider {
  getRefreshToken(): string | null;
  saveAccessToken(token: string): void;
  saveRefreshToken(token: string): void;
  getTokenExpiration(): Date | null;
}
```

### Axios HTTP Client (with Auth Interceptor & Retry)

Axios interceptors replace the manual `AuthInterceptor` and `RetryPolicy` classes entirely. `axios-retry` handles exponential backoff in a single configuration call.

```typescript
// data/networking/AxiosHTTPClient.ts
import axios, {
  AxiosInstance,
  AxiosError,
  InternalAxiosRequestConfig,
} from 'axios';
import axiosRetry from 'axios-retry';

export function createHTTPClient(
  baseURL: string,
  tokenProvider: TokenProvider,
  tokenRefresher: TokenRefresher
): HTTPClient {
  const instance: AxiosInstance = axios.create({
    baseURL,
    headers: { 'Content-Type': 'application/json' },
  });

  // --- Auth: attach Bearer token to every request ---
  instance.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
      const token = tokenProvider.getAccessToken();
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    }
  );

  // --- Auth: refresh token on 401 and retry once ---
  instance.interceptors.response.use(
    (response) => response,
    async (error: AxiosError) => {
      const config = error.config as InternalAxiosRequestConfig & { _retried?: boolean };

      if (error.response?.status === 401 && !config._retried) {
        config._retried = true;
        await tokenRefresher.refreshToken();
        return instance.request(config);
      }

      throw mapAxiosError(error);
    }
  );

  // --- Retry: exponential backoff for network errors and 5xx ---
  axiosRetry(instance, {
    retries: 3,
    retryDelay: axiosRetry.exponentialDelay,   // 1s, 2s, 4s
    retryCondition: (error) =>
      axiosRetry.isNetworkError(error) || axiosRetry.isRetryableError(error),
    onRetry: (retryCount, error) => {
      if (process.env.NODE_ENV === 'development') {
        console.warn(`⚠️ Retry attempt ${retryCount} for ${error.config?.url}`);
      }
    },
  });

  // --- Development logger ---
  if (process.env.NODE_ENV === 'development') {
    instance.interceptors.request.use((config) => {
      console.log(`➡️ ${config.method?.toUpperCase()} ${config.url}`);
      return config;
    });
    instance.interceptors.response.use((response) => {
      console.log(`⬅️ ${response.status} ${response.config.url}`);
      return response;
    });
  }

  return {
    get: (path, options) =>
      instance.get(path, { params: options?.params, headers: options?.headers, signal: options?.signal })
        .then((r) => r.data),
    post: (path, body, options) =>
      instance.post(path, body, { headers: options?.headers, signal: options?.signal })
        .then((r) => r.data),
    put: (path, body, options) =>
      instance.put(path, body, { headers: options?.headers, signal: options?.signal })
        .then((r) => r.data),
    patch: (path, body, options) =>
      instance.patch(path, body, { headers: options?.headers, signal: options?.signal })
        .then((r) => r.data),
    delete: (path, options) =>
      instance.delete(path, { headers: options?.headers, signal: options?.signal })
        .then((r) => r.data),
  };
}

// Also export an unauthenticated client factory (used for token refresh calls)
export function createUnauthenticatedHTTPClient(baseURL: string): HTTPClient {
  const instance: AxiosInstance = axios.create({
    baseURL,
    headers: { 'Content-Type': 'application/json' },
  });

  axiosRetry(instance, {
    retries: 3,
    retryDelay: axiosRetry.exponentialDelay,
    retryCondition: (error) => axiosRetry.isNetworkError(error),
  });

  return {
    get: (path, options) => instance.get(path, { params: options?.params }).then((r) => r.data),
    post: (path, body) => instance.post(path, body).then((r) => r.data),
    put: (path, body) => instance.put(path, body).then((r) => r.data),
    patch: (path, body) => instance.patch(path, body).then((r) => r.data),
    delete: (path) => instance.delete(path).then((r) => r.data),
  };
}

function mapAxiosError(error: AxiosError): NetworkError {
  if (error.response) {
    return new NetworkError(
      'httpError',
      `HTTP ${error.response.status}`,
      error.response.status
    );
  }
  if (error.code === 'ECONNABORTED' || error.code === 'ERR_CANCELED') {
    return new NetworkError('timeout', error.message);
  }
  if (error.code === 'ERR_NETWORK') {
    return new NetworkError('noConnection', error.message);
  }
  return new NetworkError('unknown', error.message);
}
```

### Token Refresh Service

```typescript
// data/networking/TokenRefreshService.ts
interface TokenRefreshResponse {
  access_token: string;
  refresh_token: string;
  expires_in: number;
}

export class TokenRefreshService implements TokenRefresher {
  private refreshPromise: Promise<void> | null = null;

  constructor(
    private readonly httpClient: HTTPClient,   // unauthenticated client
    private readonly tokenStorage: TokenStorage
  ) {}

  async refreshToken(): Promise<void> {
    // Serialize concurrent refresh calls — all callers await the same promise
    if (this.refreshPromise) {
      return this.refreshPromise;
    }

    this.refreshPromise = this.doRefresh().finally(() => {
      this.refreshPromise = null;
    });

    return this.refreshPromise;
  }

  private async doRefresh(): Promise<void> {
    if (!this.isTokenExpired()) return;

    const refreshToken = this.tokenStorage.getRefreshToken();
    if (!refreshToken) {
      throw new NetworkError('httpError', 'No refresh token available', 401);
    }

    const response = await this.httpClient.post<TokenRefreshResponse>(
      '/auth/refresh',
      { refresh_token: refreshToken }
    );

    this.tokenStorage.saveAccessToken(response.access_token);
    this.tokenStorage.saveRefreshToken(response.refresh_token);
  }

  private isTokenExpired(): boolean {
    const expiration = this.tokenStorage.getTokenExpiration();
    if (!expiration) return true;
    const bufferMs = 30_000; // 30 seconds buffer
    return Date.now() >= expiration.getTime() - bufferMs;
  }
}
```

**What's included:**

| Feature | Implementation |
|---------|----------------|
| **Auth Interceptor** | `axios.interceptors.request` — attaches Bearer token |
| **401 Refresh & Retry** | `axios.interceptors.response` — refreshes and retries once |
| **Retry Policy** | `axios-retry` — exponential backoff for network errors & 5xx |
| **Request Logger** | `axios.interceptors` (dev only) — logs method + URL |
| **Error Normalization** | `mapAxiosError()` — maps `AxiosError` to `NetworkError` |
| **Token Refresh** | `TokenRefreshService` — serialized with a shared Promise |

---
