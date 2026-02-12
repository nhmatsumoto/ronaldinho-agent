# Task: Frontend Dashboard Data Integration

## Specialist: Frontend

## Priority: Medium

## Dependencies: frontend_auth.md

### Objective

Connect the Dashboard and Punch Clock components to real data from the backend.

### Scope

1. **Dashboard Shell**: Use the `GetMe` GraphQL query to populate the sidebar and profile info (User Name, Role, Sector).
2. **Punch History**: Use `GetTodayPunches` to populate the "Histórico de Hoje" list.
3. **Punch Actions**: Connect the "Entrada 1", "Saída 1", etc. buttons to the `RecordPunch` mutation.
4. **Geolocation**: Ensure the frontend captures `navigator.geolocation` when punching and sends it to the backend.
5. **Offline Support**: (Optional) Add basic error handling if the API is unreachable.

### Acceptance Criteria

- [x] User profile shows real data from DB.
- [x] Clicking a punch button records a punch in the database.
- [x] The history list updates immediately after a punch (use cache invalidation or refetch).
- [ ] Geolocation coordinates are correctly sent in the API payload (Logic implemented, needs browser testing).
