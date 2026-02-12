# Task: NativeAOT & Performance Audit

## Specialist: Performance
## Priority: Medium
## Dependencies: None

### Objective
Ensure the backend API is compatible with `NativeAOT` and optimized for high-throughput/low-allocation in hot-paths (Punches).

### Scope
1.  **Serialization**: Replace any reflection-based `System.Text.Json` usage with `JsonSerializerContext` (Source Generators).
2.  **DTO Audit**: Ensure all DTOs used in GraphQL/REST are AOT-friendly.
3.  **EF Core**: Implement `CompiledQueries` for the most frequent read operations (e.g., fetching today's punches).
4.  **Logging**: Use `LoggerMessage` (source-generated) instead of standard interpolation in `Kettei.Infrastructure`.
5.  **Benchmarks**: Create a basic `BenchmarkDotNet` project to measure current `Login` and `RecordPunch` performance.

### Acceptance Criteria
- [ ] No `Trimming` warnings during build with `<PublishAot>true</PublishAot>`.
- [ ] `Source Generators` used for all JSON serialization.
- [ ] Benchmark baseline established.
- [ ] Minimal allocations in the `RecordPunch` request pipeline.
