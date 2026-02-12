# Architecture Overview

## Data Flow
1. **Request**: Browser calls `http://localhost:8080/graphql`.
2. **Identification**: `TenantService` extracts `X-Tenant-Id` from headers.
3. **Filtering**: `KetteiDbContext` applies a Global Query Filter `e.TenantId == CurrentTenantId` to all subsequent queries.
4. **Processing**: MediatR Dispatcher sends request to the corresponding `IRequestHandler` in the `Application` layer.
5. **Persistence**: `SaveChangesAsync` in `KetteiDbContext` automatically populates `TenantId`, `CreatedAt`, and `CreatedBy` for new entities.

## Entity Relationships
- **Employee**: Belongs to a **Department** and a **Worksite**.
- **Punch**: Linked to an **Employee** and optionally a **Worksite**.
- **WorkRequest**: Linked to an **Employee** (represents Yukyu/Férias, Kesseki/Falta).
- **PayrollRecord**: Monthly snapshots for historical reporting (separate from the real-time estimate).

## Multi-Tenancy Design
- **Isolation**: TenantId is a `Guid` present in every relevant entity.
- **Header**: `X-Tenant-Id` is strictly required for authenticated requests.
- **Login Exception**: `LoginCommand` uses `.IgnoreQueryFilters()` to find the user across tenants before establishing the session.
