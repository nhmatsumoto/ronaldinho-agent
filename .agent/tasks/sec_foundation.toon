# Task: Security Impl - Foundation Phase

## 1. Hashing Service
- Install `BCrypt.Net-Next` in `Kettei.Infrastructure`.
- Interface `IPasswordHasher`:
    - `string Hash(string password)`
    - `bool Verify(string password, string hash)`
- Implementation `BCryptPasswordHasher`.

## 2. Auth Handler Update
- Update `LoginHandler` in `Kettei.Application`.
- Inject `IPasswordHasher`.
- Replace `user.EncryptedPassword != request.Password` with `!_hasher.Verify(request.Password, user.EncryptedPassword)`.

## 3. Seed Data
- Create a Seeder that inserts a default Admin user with a **Hashed** password.
