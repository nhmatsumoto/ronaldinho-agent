# Task: Database Impl - Foundation Phase

## 1. Entity Definition
Update `Kettei.Domain` with the following entities. Use `BaseEntity` (Id, CreatedAt, UpdatedAt) for all.

### `Department.cs`
- Properties: `Name` (string), `ManagerId` (Guid?).
- Navigation: `ICollection<Employee> Employees`.

### `Worksite.cs`
- Properties: `Name` (string), `Address` (string).
- Navigation: `ICollection<Employee> Employees`.

### `Employee.cs` (Update)
- Add Foreign Keys: `DepartmentId`, `WorksiteId`.
- Add Properties: `SystemRole` (Enum/String), `YukyuBalance` (decimal).
- Remove implicit "Role" string, replace with `JobTitle` (optional for now, or keep as string for MVP).

## 2. Infrastructure
- Update `KetteiDbContext` to include `DbSet<Department>` and `DbSet<Worksite>`.
- Configure Relationships (EF Core Fluent API) in `OnModelCreating`.
- Ensure migrations are created (we will run `dotnet ef migrations add` manually later).
