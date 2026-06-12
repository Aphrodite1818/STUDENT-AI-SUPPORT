import { cn } from "../../utils/cn";

function Input({ label, error, className = "", hint, ...props }) {
  const errorMessage =
    typeof error === "string"
      ? error
      : error?.message || (error ? JSON.stringify(error) : "");

  return (
    <div className="w-full">
      {label && (
        <label className="mb-1.5 block text-sm font-medium text-text-soft">
          {label}
        </label>
      )}
      <input className={cn("input-base", className)} {...props} />
      {hint && !errorMessage && (
        <p className="mt-1.5 text-xs text-text-muted">{hint}</p>
      )}
      {errorMessage && (
        <p className="mt-1.5 text-xs font-medium text-error">{errorMessage}</p>
      )}
    </div>
  );
}

export default Input;
