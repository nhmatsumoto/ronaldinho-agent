# Task: Attendance Workflow & Leave Entities

## Specialist: Database
## Priority: Medium
## Dependencies: db_foundation.md

### Objective
Expand the database schema to support time adjustment requests, overtime requests, and paid leave (Yukyu) management.

### Scope
1.  **WorkRequest Entity**: Create `WorkRequest.cs` in `Kettei.Domain`.
    - Fields: `EmployeeId`, `Type` (Adjustment, Overtime, Absence), `Status` (Pending, Approved, Rejected), `Reason`, `Date`, `TargetPunchId (optional)`, `ApproverId`.
2.  **PaidLeaveBalance Entity**: (Optional or part of Employee) Ensure `YukyuBalance` tracking logic is solid.
3.  **DbContext Update**: Add `WorkRequests` DbSet to `IApplicationDbContext` and `KetteiDbContext`.
4.  **Relationships**: Configure `Employee -> WorkRequests` (1:N) and `WorkRequest -> Approver` (Employee).
5.  **Audit Logs**: Ensure all status changes are captured by the `AuditLog` system.

### Acceptance Criteria
- [ ] New entities created and configured.
- [ ] EF Core Migration generated and applied.
- [ ] Logic for updating `YukyuBalance` on request approval defined (can be a TODO for Application Layer).
- [ ] Unit tests for relationship mapping pass.
