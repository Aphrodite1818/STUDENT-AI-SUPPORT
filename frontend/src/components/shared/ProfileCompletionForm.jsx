import { useEffect, useRef, useState } from "react";
import Button from "../ui/Button";
import Input from "../ui/Input";
import { authSession, parseApiError } from "../../services/api";
import { userService } from "../../services/user.service";

const EMPTY_FORM_DATA = {
  user: {},
  tenant: {},
  role_profile: {},
};

const toFormData = (schemaData) => ({
  user: { ...(schemaData?.values?.user || {}) },
  tenant: { ...(schemaData?.values?.tenant || {}) },
  role_profile: { ...(schemaData?.values?.role_profile || {}) },
});

const toFieldKey = (field) => `${field.source}.${field.name}`;

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
          value={value ?? ""}
          onChange={(event) => onChange(field, event.target.value)}
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
          value={value ?? ""}
          onChange={(event) => onChange(field, event.target.value)}
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
        type={field.type || "text"}
        value={value ?? ""}
        onChange={(event) => onChange(field, event.target.value)}
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
  submitLabel = "Save profile",
  onSaved,
  onProfileStateResolved,
  initialSchemaData = null,
}) {
  const callbacksRef = useRef({ onSaved, onProfileStateResolved });
  const [schemaData, setSchemaData] = useState(initialSchemaData);
  const [formData, setFormData] = useState(() => toFormData(initialSchemaData));
  const [fieldErrors, setFieldErrors] = useState({});
  const [submitError, setSubmitError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isLoadingSchema, setIsLoadingSchema] = useState(!initialSchemaData);

  useEffect(() => {
    callbacksRef.current = { onSaved, onProfileStateResolved };
  }, [onSaved, onProfileStateResolved]);

  useEffect(() => {
    if (!initialSchemaData) return;

    setSchemaData(initialSchemaData);
    setFormData(toFormData(initialSchemaData));
    callbacksRef.current.onProfileStateResolved?.({
      completed: Boolean(initialSchemaData.profile_completed),
    });
    setIsLoadingSchema(false);
  }, [initialSchemaData]);

  useEffect(() => {
    let mounted = true;

    async function loadSchema() {
      if (initialSchemaData || !user?.id) {
        if (!initialSchemaData) {
          setSchemaData(null);
          setFormData(EMPTY_FORM_DATA);
          setIsLoadingSchema(false);
        }
        return;
      }

      setIsLoadingSchema(true);

      try {
        const nextSchema = await userService.getProfileCompletionSchema();
        if (!mounted) return;

        setSchemaData(nextSchema);
        setFormData(toFormData(nextSchema));
        callbacksRef.current.onProfileStateResolved?.({
          completed: Boolean(nextSchema.profile_completed),
        });
      } catch (error) {
        if (!mounted) return;
        const parsed = parseApiError(error, "Failed to load your profile form.");
        setSubmitError(parsed.message);
      } finally {
        if (mounted) setIsLoadingSchema(false);
      }
    }

    loadSchema();

    return () => {
      mounted = false;
    };
  }, [initialSchemaData, user?.id]);

  const handleChange = (field, value) => {
    setFormData((current) => ({
      ...current,
      [field.source]: {
        ...(current[field.source] || {}),
        [field.name]: value,
      },
    }));
    setFieldErrors((current) => ({
      ...current,
      [toFieldKey(field)]: undefined,
    }));
    setSubmitError(null);
    setSuccessMessage(null);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!schemaData) return;

    setIsSubmitting(true);
    setFieldErrors({});
    setSubmitError(null);
    setSuccessMessage(null);

    try {
      const payload = {};

      for (const section of schemaData.sections || []) {
        for (const field of section.fields || []) {
          if (field.read_only) continue;

          if (!payload[field.source]) payload[field.source] = {};
          const rawValue = formData?.[field.source]?.[field.name];
          payload[field.source][field.name] = rawValue === "" ? null : rawValue;
        }
      }

      const response = await userService.submitProfileCompletion(payload);
      authSession.setUser(response.user);
      setSchemaData(response);
      setFormData(toFormData(response));
      setSuccessMessage("Profile updated successfully.");
      callbacksRef.current.onProfileStateResolved?.({
        completed: Boolean(response.profile_completed),
      });
      callbacksRef.current.onSaved?.(response.user, response);
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

      {(schemaData?.sections || []).map((section) => (
        <div key={section.key} className="space-y-4 rounded-2xl border border-border bg-surface-muted/40 p-4">
          <div>
            <h3 className="text-sm font-semibold text-text">{section.title}</h3>
            {section.description && (
              <p className="mt-1 text-xs text-text-muted">{section.description}</p>
            )}
          </div>

          {isLoadingSchema ? (
            <p className="text-sm text-text-muted">Loading profile details...</p>
          ) : (
            section.fields.map((field) => {
              const value = formData?.[field.source]?.[field.name] ?? "";
              const errorKey = `${field.source}.${field.name}`;

              return field.read_only ? (
                <ReadOnlyField
                  key={`${section.key}-${field.source}-${field.name}`}
                  field={field}
                  value={value}
                />
              ) : (
                <EditableField
                  key={`${section.key}-${field.source}-${field.name}`}
                  field={field}
                  value={value}
                  error={fieldErrors[errorKey]}
                  onChange={handleChange}
                />
              );
            })
          )}
        </div>
      ))}

      <Button type="submit" className="w-full sm:w-auto" disabled={isSubmitting || isLoadingSchema || !schemaData}>
        {isSubmitting ? "Saving..." : submitLabel}
      </Button>
    </form>
  );
}

export default ProfileCompletionForm;
