const fieldClass =
  "h-[34px] min-h-[34px] w-full rounded-lg border border-border bg-background/60 px-3 text-[13px] font-medium text-text outline-none transition focus:border-primary focus:ring-4 focus:ring-primary/10";

export function SelectField({
  label,
  value,
  onChange,
  children,
  disabled = false,
  required = false,
  className = "",
}) {
  return (
    <label className={`block ${className}`}>
      <span className="mb-1.5 block text-[11.5px] font-medium text-text-muted">
        {label}
      </span>
      <select
        value={value}
        onChange={(event) => onChange(event.target.value)}
        disabled={disabled}
        required={required}
        className={fieldClass}
      >
        {children}
      </select>
    </label>
  );
}

export function TextField({
  label,
  value,
  onChange,
  type = "text",
  min,
  max,
  placeholder,
  required = false,
  className = "",
}) {
  return (
    <label className={`block ${className}`}>
      <span className="mb-1.5 block text-[11.5px] font-medium text-text-muted">
        {label}
      </span>
      <input
        type={type}
        min={min}
        max={max}
        value={value}
        placeholder={placeholder}
        required={required}
        onChange={(event) => onChange(event.target.value)}
        className={fieldClass}
      />
    </label>
  );
}

export function CheckboxField({ label, checked, onChange, helperText, className = "" }) {
  return (
    <label className={`block ${className}`}>
      <span className="flex h-[34px] min-h-[34px] items-center gap-3 rounded-lg border border-border bg-background/60 px-3 text-[13px] font-medium text-text-soft">
        <input
          type="checkbox"
          checked={checked}
          onChange={(event) => onChange(event.target.checked)}
          className="h-4 w-4 rounded border-border text-primary focus:ring-primary"
        />
        {label}
      </span>
      {helperText ? <span className="mt-1 block text-[10.5px] text-text-faint">{helperText}</span> : null}
    </label>
  );
}
