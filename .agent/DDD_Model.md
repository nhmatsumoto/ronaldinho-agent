# Domain-Driven Design Model: Kettei Platform

## 1. Domain Overview
**Core Domain**: **Attendance & Workforce Management** (Time tracking, Shift implementation, Real-time status).
**Supporting Subdomains**: 
- **Organization Structure** (Departments, Hierarchy, Worksites).
- **Workflow Automation** (Approvals for leaves, overtime).
**Generic Subdomains**:
- **Identity & Access Management** (Authentication, RBAC).

## 2. Bounded Contexts & Ubiquitous Language

### A. Identity & Access Context (IAM)
Responsible for user authentication and authorization.

**Ubiquitous Language**:
- **User**: A system user with login credentials.
- **SystemRole**: Implementation-level permission set (`SysAdmin`, `President`, `Admin`, `Leader`, `SubLeader`, `Employee`).
- **Tenant**: The company instance (Multi-tenancy support).

**Entities**:
- `User` (Aggregate Root): Id, Email, PasswordHash, SystemRole, TenantId.
- `Permission`: Granular capabilities.

### B. Organization Context
Manages the company structure and employee assignments.

**Ubiquitous Language**:
- **Employee**: A worker with a contract.
- **Department (Setor)**: Functional division (e.g., "Produção A", "Logística").
- **JobTitle (Cargo)**: A specific role with a base salary range (e.g., "Operador", "Líder de Linha").
- **Worksite (Genba/Cost Center)**: Physical location or project code where work happens.
- **Hierarchy**: The reporting line (Employee -> Sub-Leader -> Leader -> Manager).

**Entities**:
- `Employee` (Aggregate Root): Combines Profile, Contract Details (BaseRate, YukyuBalance), and Assignments.
- `Department`: Id, Name, ManagerId.
- `JobTitle`: Id, Title, BaseHourlyRate.
- `Worksite`: Id, Name, Address.

### C. Attendance Context (Core)
Handles time tracking, status, and calculations.

**Ubiquitous Language**:
- **Punch (Ponto)**: A timestamped event (Entry, Exit, Break Start/End).
- **Timesheet (Folha)**: Daily record aggregating punches and calculating total hours.
- **Status**: Real-time state (Present, Absent, Late, Early Leave).
- **ConsolidatedTime**: Calculated WorkTime, Overtime, NightShiftTime.

**Entities**:
- `Punch` (Immutable Event): EmployeeId, Timestamp, Type, WorksiteId, DeviceInfo.
- `Timesheet` (Aggregate Root): Date, EmployeeId, List<Punch>, DailyStats.

### D. Request & Workflow Context
Handles deviations from the standard schedule that require approval.

**Ubiquitous Language**:
- **WorkRequest**: A formal request for Paid Leave (Yukyu), Absence (Kesseki), or Overtime.
- **Approval**: The act of a Leader/Admin validating the request.

**Entities**:
- `Request` (Aggregate Root): Id, Type, RequesterId, ApproverId, Status (Pending, Approved, Rejected), Reason.

## 3. Data Flow & Integration (Frontend Requirements)

The Frontend (`KetteiContext.tsx`) expects a rich `Employee` object:
```typescript
interface Employee {
    id: string;
    systemRole: string; // IAM
    sector: string; // Organization (Department Name)
    hierarchy: string; // Organization
    baseRate: number; // Organization (Contract)
    costCenter: string; // Organization (Worksite Name)
    yukyuBalance: number; // Attendance/Leave Balance
    healthStatus: string; // Health Context (New)
}
```

**Mapping Strategy**:
The Backend API `Projections` (DTOs) must aggregate data from these contexts.
- `GetEmployeesQuery`: Joins `User` (IAM), `Employee` (Org), `Department` (Org).

## 4. Engineering Action Items

1.  **Refactor `Employee`**: Split into `User` (Auth) and `EmployeeProfile` (Org).
2.  **Create Org Entities**: `Department`, `Worksite`, `JobTitle`.
3.  **Implement Relationships**: 
    - Department 1:N Employees
    - Worksite 1:N Employees (Current Assignment)
4.  **Secure Auth**: Implement JWT with proper Hashing (BCrypt).
