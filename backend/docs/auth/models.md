# MODEL

This file contains the database table definition for the authentication system.

The authentication module is responsible for storing temporary authentication values used throughout the platform, such as:

* Account verification
* Password reset
* Tenant activation
* User invitations

It does **not** store user passwords. Passwords are stored in the User table.

---

# IMPORTS

## BaseModel

`BaseModel` provides common fields inherited by all tables, including:

* `id` (UUID primary key)
* `tenant_id` (foreign key to Tenant table)
* Timestamp fields (`created_at`, `updated_at`)

---

# ENUMS

## AuthPurpose

This enum defines the purpose of an authentication record.

Possible values include:

### VERIFICATION

Used when verifying a newly created account through OTP.

### PASSWORD_RESET

Used when a user requests to reset their password.

### TENANT_ACTIVATION

Used when activating a tenant account.

### INVITATION

Used when inviting a user to join a tenant.

The purpose field allows the system to know how a stored authentication value should be processed.

---

# MODEL FIELDS

## email

Stores the email address associated with the authentication record.

This is the email that will receive the OTP, reset token, activation code, or invitation.

---

## hashed_value

Stores a hashed version of the authentication value.

Examples:

* OTP code
* Password reset token
* Invitation token
* Activation token

The raw value is never stored directly in the database for security reasons.

---

## purpose

Stores the authentication purpose using the `AuthPurpose` enum.

This tells the system what the authentication value is being used for.

Examples:

```txt
VERIFICATION
PASSWORD_RESET
INVITATION
TENANT_ACTIVATION
```

---

## expires_at

Stores the date and time when the authentication value becomes invalid.

After this time, the value can no longer be used.

---

## is_used

Tracks whether the authentication value has already been consumed.

### False

The value is still valid and can be used.

### True

The value has already been used and should no longer be accepted.

This prevents OTPs, reset tokens, and invitation tokens from being reused.
