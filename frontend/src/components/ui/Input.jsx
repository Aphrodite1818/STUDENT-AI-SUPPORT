function Input({ label, error, className = "", ...props }) {
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
      <input className={`input-base ${className}`} {...props} />
      {errorMessage && <p className="mt-1 text-sm text-error">{errorMessage}</p>}
    </div>
  );
}

export default Input;
