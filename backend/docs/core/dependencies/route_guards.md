# ROUTE GUARDS / AUTH DEPENDENCIES

This file protects backend routes by checking who is making the request and whether that person is allowed to access the endpoint.

It handles both:

* Tenant users
* Superadmins

It does not create JWT tokens.
It only reads and validates tokens sent with requests.

---

# IMPORTANT IDEA

Login creates the token.

Protected routes consume the token.

```txt
Login endpoint
↓
Creates JWT
↓
Frontend stores JWT
↓
Frontend sends JWT in Authorization header
↓
Route guard reads JWT
↓
Route guard checks who the user is
↓
Route either continues or gets blocked
```

---

# IMPORTS

## uuid

Used to convert the `sub` value from the JWT into a UUID.

The `sub` usually stores the ID of the logged-in actor.

---

## Callable, Coroutine

Used for type hints.

They describe a function that can be called and returns an async result.

This is mainly used by `require_tenant_role`.

---

## Annotated

Used to combine a type with a FastAPI dependency.

Example:

```python
TokenDependency = Annotated[str, Depends(oauth2_scheme)]
```

This means:

```txt
Give me a string token, but get it using oauth2_scheme.
```

---

## Depends

FastAPI dependency injection tool.

It allows one function to automatically receive values from another function.

---

## OAuth2PasswordBearer

Reads the JWT token from the request `Authorization` header.

Example request:

```http
Authorization: Bearer jwt_token_here
```

It extracts only:

```txt
jwt_token_here
```

Important:

`OAuth2PasswordBearer` does not login the user.
It does not decode the JWT.
It does not fetch the user from the database.

It only extracts the bearer token from the header.

---

## jwt, JWTError

Used to decode and validate JWT tokens.

`jwt.decode()` checks:

* The token signature
* The secret key
* The algorithm
* The token expiry

If the token is invalid, `JWTError` is raised.

---

## Repositories

The file uses repositories to fetch real account records after decoding the JWT:

* `SuperAdminRepository`
* `UserRepository`
* `TenantRepository`

This is important because the JWT only contains claims.
The database contains the actual latest account state.

---

# GLOBAL DEPENDENCIES

## `oauth2_scheme`

```python
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
```

This tells FastAPI:

```txt
Protected endpoints expect a Bearer token.
The token can be obtained from /api/v1/auth/login.
```

The `tokenUrl` is mainly used for Swagger documentation.

At runtime, `OAuth2PasswordBearer` reads the token from:

```http
Authorization: Bearer <token>
```

It does not call `/login`.

---

## `TokenDependency`

```python
TokenDependency = Annotated[str, Depends(oauth2_scheme)]
```

Shortcut meaning:

```txt
This parameter should be a string token extracted from the Authorization header.
```

---

## `DbDependency`

```python
DbDependency = Annotated[AsyncSession, Depends(get_db)]
```

Shortcut meaning:

```txt
This parameter should be an async database session.
```

---

# MAJOR FUNCTIONS

## `get_current_actor`

This function identifies who is currently making the request.

It can return either:

* `User`
* `SuperAdmin`

Flow:

```txt
Receive token from OAuth2PasswordBearer
↓
Decode JWT using SECRET_KEY and ALGORITHM
↓
Extract sub from payload
↓
Extract account_type from payload
↓
Convert sub to UUID
↓
If account_type is superadmin:
    fetch SuperAdmin from database
↓
Else:
    fetch tenant User from database
↓
Return actor
```

### What `sub` means

`sub` means subject.

In this app, it stores the logged-in actor's ID.

Example:

```json
{
  "sub": "550e8400-e29b-41d4-a716-446655440000",
  "account_type": "superadmin"
}
```

The backend uses `sub` to fetch the real account from the database.

---

### Why the database is checked after decoding JWT

Because the token may say:

```txt
User is admin
```

But the database may now say:

```txt
User has been disabled
Tenant has been deleted
Role has changed
```

So the token is not trusted alone.

The backend still fetches the latest actor record.

---

## `get_current_tenant_user`

This function ensures the current actor is a valid tenant user.

It blocks superadmins from routes that require tenant users.

Flow:

```txt
Get current actor
↓
If actor is SuperAdmin:
    block request
↓
Check user account is ACTIVE
↓
Fetch user's tenant
↓
Check tenant exists
↓
Check tenant is not deleted
↓
Check tenant is verified
↓
Check tenant status is ACTIVE or TRIAL
↓
Return tenant user
```

This protects normal school routes like:

* Students
* Teachers
* Subjects
* Attendance
* Results

---

## `get_current_superadmin`

This function ensures the current actor is a valid superadmin.

Flow:

```txt
Get current actor
↓
If actor is normal User:
    block request
↓
Check superadmin is active
↓
Return superadmin
```

This protects platform-level routes that only superadmins should access.

---

## `require_superadmin`

This is a small wrapper dependency.

It simply requires `get_current_superadmin` to pass.

If it passes, it returns the current superadmin.

Used for routes like:

```txt
Create tenant manually
Approve tenant
Manage platform admins
View platform-wide data
```

---

## `require_tenant_role`

This function creates a role-checking dependency.

It receives a list of allowed roles.

Example:

```python
Depends(require_tenant_role([UserRole.ADMIN, UserRole.TEACHER]))
```

Meaning:

```txt
Only ADMIN or TEACHER users can access this route.
```

Flow:

```txt
Get current tenant user
↓
Check user's role
↓
If role is not allowed:
    raise ForbiddenException
↓
Return current user
```

This protects routes based on role.

Example:

```txt
Admin can create teachers.
Teacher can mark attendance.
Parent can view child progress.
Student can view assignments.
```

---

## `require_tenant_ownership`

This function ensures the current user belongs to the tenant they are trying to access.

Flow:

```txt
Receive tenant_id from route
↓
Get current tenant user
↓
Compare current_user.tenant_id with route tenant_id
↓
If they do not match:
    block request
↓
Return current user
```

This prevents one school from accessing another school's data.

Example:

```txt
User belongs to Tenant A
↓
User tries to access Tenant B resources
↓
Request is blocked
```

---

# FULL FLOW EXAMPLE

## User logs in

```txt
POST /api/v1/auth/login
↓
Backend returns JWT
```

Example JWT payload:

```json
{
  "sub": "user-id",
  "email": "admin@school.com",
  "role": "admin",
  "account_type": "tenant_user",
  "tenant_id": "tenant-id",
  "exp": 1781941676
}
```

---

## User calls protected endpoint

```http
GET /api/v1/students

Authorization: Bearer jwt_token_here
```

---

## Backend route guard runs

```txt
OAuth2PasswordBearer extracts token
↓
get_current_actor decodes token
↓
Database fetches user
↓
get_current_tenant_user checks account + tenant status
↓
require_tenant_role checks role
↓
Endpoint is allowed to run
```

---

# SIMPLE MENTAL MODEL

```txt
OAuth2PasswordBearer
    gets token from header

get_current_actor
    decodes token and finds the user/superadmin

get_current_tenant_user
    confirms actor is a valid tenant user

get_current_superadmin
    confirms actor is a valid superadmin

require_tenant_role
    checks tenant user role

require_tenant_ownership
    checks tenant isolation
```

---

# WHAT CAN BREAK

## 1. Missing Authorization header

If the frontend does not send:

```http
Authorization: Bearer <token>
```

the route will fail before reaching your endpoint.

---

## 2. Expired JWT

If `exp` has passed, `jwt.decode()` fails and raises an auth error.

---

## 3. Wrong secret key or algorithm

If the token was signed with a different secret or algorithm, decoding fails.

---

## 4. Invalid `sub`

If `sub` is missing or not a valid UUID, the request is rejected.

---

## 5. Deleted or inactive account

Even if the JWT is valid, the database check can still block the user.

---

## 6. Tenant is inactive/deleted/unverified

A valid user under a bad tenant should still be blocked.

---

## 7. Wrong role

If the route requires ADMIN and the current user is TEACHER, request is blocked.

---

## 8. Wrong tenant

If the user tries to access another tenant's resources, request is blocked.
