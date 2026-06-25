````md
# Tenant Schema Documentation

This file contains the schemas used to validate and return tenant-related data.

These schemas control:

- data sent into tenant endpoints
- data used when creating tenants
- data used when updating tenants
- data returned from tenant endpoints

---

# Imports

The schema file imports these enums from the Tenant model:

- `SubscriptionPlan`
- `TenantStatus`
- `TenantVerificationStatus`

It also imports:

- `generate_slug`

`generate_slug` is used to create a clean tenant slug from the school name.

Example:

```text
De Bright School
↓
de-bright-school
````

---

# Base Schema Setup

## InputBase

Base schema used for incoming data.

Used by schemas that receive data from users, admins, or API requests.

---

## OutputBase

Base schema used for outgoing data.

Used by schemas that return data from the backend to the frontend.

---

# Major Tenant Schemas

## TenantBase

Base schema for tenant management.

It contains the common tenant fields that can be reused by other tenant schemas.

---

## TenantRegisterRequest

Public schema used when a new school registers on the platform.

This should only contain the fields needed for normal tenant signup.

Example use:

```text
A school signs up from the public registration page.
```

---

## TenantCreate

Private schema used by the platform superadmin to create a tenant manually.

This schema can expose more options than `TenantRegisterRequest`.

Example use:

```text
A superadmin creates a tenant and sets custom limits, plan, or status.
```

---

## TenantUpdate

Shared schema used to update a tenant profile.

It can be used by:

* tenant admin
* platform superadmin

Example use:

```text
A tenant updates school name, phone number, address, logo, timezone, or language.
```

Important:

Sensitive fields like subscription limits, feature access, or account status should not be freely editable by tenant admins unless the service layer allows it.

---

## TenantOnboardingUpdate

schema for first-time tenant onboarding completion
can only be used by tenant_admin


Example use:
```
A new tenant signsup and tenant_admin uses this schema to update tenant 
```

## TenantStatusUpdate

Schema used to update the account status of a tenant.

This should be used by the platform superadmin only.

Example use:

```text
A superadmin changes a tenant from TRIAL to ACTIVE.
```

---

## TenantPublicResponse

Public response schema for tenant data.

It returns safe tenant information that can be exposed publicly or to normal frontend views.

Example fields:

* school name
* slug
* logo URL
* city
* state
* country

---

## TenantManagementResponse

Extended response schema based on `TenantPublicResponse`.

It returns extra tenant information for authorized users.

Can be used by:

* platform superadmin
* tenant admin

Example extra fields:
* is_deleted
* status
* verification status
* max students
* max teachers
* feature flags
* onboarding status

---

## TenantContext

Small response schema that returns only the most important tenant details.

It should avoid unnecessary tenant data.

Example use:

```text
Frontend needs basic tenant info after login.
```

Example fields:

* tenant id
* school name
* slug
* logo URL
* plan
* status
* onboarding completed




## TenantOnboardingStatusResponse

schema response returned after tenant completes onboarding 

```
```
