import { useEffect, useMemo, useRef, useState } from "react";
import Button from "../ui/Button";
import Input from "../ui/Input";
import { authSession, parseApiError } from "../../services/api";
import { tenantService } from "../../services/tenant.service";
import { userService } from "../../services/user.service";
import {
  evaluateOnboardingState,
  getRoleProfileConfig,
  loadRoleProfileContext,
} from "../../config/roleProfileConfig";

const titleCase = (value) =>
  String(value || "")
    .replace(/_/g, " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());

const EMPTY_CONTEXT = {
  tenant: null,
  roleProfile: null,
};

function buildInitialFormData(user, config, context) {
  return config.sections.reduce((formData, section) => {
    for (const field of section.fields) {
      const sourceData =
        field.source === "user"
          ? user
          : field.source === "tenant"
            ? context.tenant
            : context.roleProfile;
      formData[field.name] = sourceData?.[field.name] ?? "";
    }
    return formData;
  }, {});
}

function getFieldValueForSave(field, value) {
  if (field.readOnly) return undefined;
  return value === "" ? null : value;
}

function groupFieldsBySource(fields) {
  return fields.reduce((grouped, field) => {
    if (!grouped[field.source]) grouped[field.source] = [];
    grouped[field.source].push(field);
    return grouped;
  }, {});
}

function ReadOnlyField({ field, value }) {
  return (
    <div>
      <label className="mb-1.5 block text-sm font-medium text-text-soft">
        {field.label}
      </label>
      <div className="min-h-11 rounded-xl border border-border bg-surface-muted px-3 py-3 text-sm text-text-soft">
        {value || field.emptyLabel || "Not available"}
      </div>
    </div>
  );
}

function EditableField({ field, value, error, onChange }) {
  if (field.type === "select") {
    return (
      <div>
        <label className="mb-1.5 block text-sm font-medium text-text-soft">
          {field.label}
        </label>
        <select
          name={field.name}
          value={value ?? ""}
          onChange={onChange}
          className="input-base"
          required={field.required}
        >
          <option value="">Select an option</option>
          {(field.options || []).map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
        {field.helperText && <p className="mt-1.5 text-xs text-text-muted">{field.helperText}</p>}
        {error && <p className="mt-1.5 text-xs font-medium text-error">{error}</p>}
      </div>
    );
  }

  if (field.type === "textarea") {
    return (
      <div>
        <label className="mb-1.5 block text-sm font-medium text-text-soft">
          {field.label}
        </label>
        <textarea
          name={field.name}
          value={value ?? ""}
          onChange={onChange}
          className="input-base min-h-24"
          required={field.required}
          placeholder={field.placeholder}
        />
        {field.helperText && <p className="mt-1.5 text-xs text-text-muted">{field.helperText}</p>}
        {error && <p className="mt-1.5 text-xs font-medium text-error">{error}</p>}
      </div>
    );
  }

  return (
    <div>
      <Input
        label={field.label}
        name={field.name}
        type={field.type || "text"}
        value={value ?? ""}
        onChange={onChange}
        error={error}
        required={field.required}
        placeholder={field.placeholder}
      />
      {field.helperText && <p className="mt-1.5 text-xs text-text-muted">{field.helperText}</p>}
    </div>
  );
}

function ProfileCompletionForm({
  user,
  role,
  submitLabel = "Save profile",
  onSaved,
  onProfileStateResolved,
  initialContext = EMPTY_CONTEXT,
}) {
  const roleConfig = useMemo(() => getRoleProfileConfig(role), [role]);
  const allFields = useMemo(
    () => roleConfig.sections.flatMap((section) => section.fields),
    [roleConfig.sections]
  );
  const fieldsBySource = useMemo(() => groupFieldsBySource(allFields), [allFields]);
  const callbacksRef = useRef({ onSaved, onProfileStateResolved });
  const hasInitialContextData = Boolean(initialContext?.tenant || initialContext?.roleProfile);
  const [context, setContext] = useState(() => (hasInitialContextData ? initialContext : EMPTY_CONTEXT));
  const [formData, setFormData] = useState(() =>
    buildInitialFormData(user, roleConfig, hasInitialContextData ? initialContext : EMPTY_CONTEXT)
  );
  const [fieldErrors, setFieldErrors] = useState({});
  const [submitError, setSubmitError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isLoadingContext, setIsLoadingContext] = useState(!hasInitialContextData);

  useEffect(() => {
    callbacksRef.current = { onSaved, onProfileStateResolved };
  }, [onSaved, onProfileStateResolved]);

  useEffect(() => {
    let mounted = true;

    async function loadContext() {
      if (hasInitialContextData) {
        setContext(initialContext);
        setFormData(buildInitialFormData(user, roleConfig, initialContext));
        callbacksRef.current.onProfileStateResolved?.(
          evaluateOnboardingState(role, user, initialContext)
        );
        setIsLoadingContext(false);
        return;
      }

      setIsLoadingContext(true);

      try {
        const nextContext = await loadRoleProfileContext(role, user);
        if (!mounted) return;

        setContext(nextContext);
        setFormData(buildInitialFormData(user, roleConfig, nextContext));

        callbacksRef.current.onProfileStateResolved?.(
          evaluateOnboardingState(role, user, nextContext)
        );
      } catch {
        if (!mounted) return;
        setContext(EMPTY_CONTEXT);
        setFormData(buildInitialFormData(user, roleConfig, EMPTY_CONTEXT));
        callbacksRef.current.onProfileStateResolved?.(
          evaluateOnboardingState(role, user, EMPTY_CONTEXT)
        );
      } finally {
        if (mounted) setIsLoadingContext(false);
      }
    }

    loadContext();

    return () => {
      mounted = false;
    };
  }, [hasInitialContextData, initialContext, role, roleConfig, user]);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormData((current) => ({ ...current, [name]: value }));
    setFieldErrors((current) => ({ ...current, [name]: undefined }));
    setSubmitError(null);
    setSuccessMessage(null);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!user?.id) return;

    setIsSubmitting(true);
    setFieldErrors({});
    setSubmitError(null);
    setSuccessMessage(null);

    try {
      let updatedUser = null;
      let updatedTenant = context.tenant;
      let updatedRoleProfile = context.roleProfile;

      const userFields = fieldsBySource.user || [];
      if (userFields.length > 0) {
        const userPayload = userFields.reduce((payload, field) => {
          const nextValue = getFieldValueForSave(field, formData[field.name]);
          if (nextValue !== undefined) payload[field.name] = nextValue;
          return payload;
        }, {});
        updatedUser = await userService.updateProfile(user.id, userPayload);
      }

      const tenantFields = fieldsBySource.tenant || [];
      if (tenantFields.length > 0 && user?.tenant_id) {
        const tenantPayload = tenantFields.reduce((payload, field) => {
          const nextValue = getFieldValueForSave(field, formData[field.name]);
          if (nextValue !== undefined) payload[field.name] = nextValue;
          return payload;
        }, {});
        updatedTenant = await tenantService.updateTenant(user.tenant_id, tenantPayload);
      }

      const roleFields = (fieldsBySource.roleProfile || []).filter((field) => !field.readOnly);
      if (roleFields.length > 0 && typeof roleConfig.saveRoleProfile === "function") {
        const rolePayload = roleFields.reduce((payload, field) => {
          const nextValue = getFieldValueForSave(field, formData[field.name]);
          if (nextValue !== undefined) payload[field.name] = nextValue;
          return payload;
        }, {});
        updatedRoleProfile = await roleConfig.saveRoleProfile(rolePayload);
      } else if (typeof roleConfig.saveRoleProfile === "function") {
        updatedRoleProfile = context.roleProfile;
      }

      const nextUser = {
        ...user,
        ...(updatedUser || {}),
        tenant: updatedTenant || null,
      };

      authSession.setUser(nextUser);
      setContext({
        tenant: updatedTenant || null,
        roleProfile: updatedRoleProfile || null,
      });
      setSuccessMessage("Profile updated successfully.");
      callbacksRef.current.onProfileStateResolved?.(
        evaluateOnboardingState(role, nextUser, {
          tenant: updatedTenant || null,
          roleProfile: updatedRoleProfile || null,
        })
      );
      callbacksRef.current.onSaved?.(nextUser);
    } catch (error) {
      const parsed = parseApiError(error, "Failed to update your profile.");
      setFieldErrors(parsed.fieldErrors || {});
      setSubmitError(parsed.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      {submitError && (
        <div className="rounded-2xl border border-error/30 bg-error-soft px-4 py-3 text-sm font-medium text-error">
          {submitError}
        </div>
      )}
      {successMessage && (
        <div className="rounded-2xl border border-success/30 bg-success-soft px-4 py-3 text-sm font-medium text-emerald-700">
          {successMessage}
        </div>
      )}

      {roleConfig.sections.map((section) => (
        <div key={section.key} className="space-y-4 rounded-2xl border border-border bg-surface-muted/40 p-4">
          <div>
            <h3 className="text-sm font-semibold text-text">
              {section.title || `${titleCase(role)} profile details`}
            </h3>
            {section.description && (
              <p className="mt-1 text-xs text-text-muted">{section.description}</p>
            )}
          </div>

          {isLoadingContext ? (
            <p className="text-sm text-text-muted">Loading profile details...</p>
          ) : (
            section.fields.map((field) =>
              field.readOnly ? (
                <ReadOnlyField key={`${section.key}-${field.name}`} field={field} value={formData[field.name]} />
              ) : (
                <EditableField
                  key={`${section.key}-${field.name}`}
                  field={field}
                  value={formData[field.name]}
                  error={fieldErrors[field.name]}
                  onChange={handleChange}
                />
              )
            )
          )}
        </div>
      ))}

      <Button type="submit" className="w-full sm:w-auto" disabled={isSubmitting || isLoadingContext}>
        {isSubmitting ? "Saving..." : submitLabel}
      </Button>
    </form>
  );
}

ProfileCompletionForm.getRoleProfileConfig = getRoleProfileConfig;

export { getRoleProfileConfig };
export default ProfileCompletionForm;
