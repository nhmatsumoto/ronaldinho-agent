# Task: Frontend Authentication Integration

## Specialist: Frontend

## Priority: High

## Dependencies: sec_foundation.md

### Objective

Replace the current mocked login behavior in the frontend with a real JWT-based authentication flow connected to the backend API.

### Scope

1. **Service Layer**: Create `AuthService.ts` to handle `POST /graphql` (Mutation: login). (Done)
2. **Context Update**: Update `KetteiContext` to handle JWT storage and automatically attach headers. (Done in `ApiClient.ts` and `KetteiContext.tsx`)
3. **Login Component**: Update the login form to call `AuthService` and handle states. (Done in `LoginForm.tsx`)
4. **Route Protection**: Implement a simple guard. (Done in `App.tsx`)

### Acceptance Criteria

- [x] User can login with `admin@Kettei.com` / `Admin123!`.
- [x] JWT is stored and used in subsequent GraphQL/REST calls.
- [x] App redirects to Dashboard on success.
- [x] Logout clears the token and returns user to Login.
