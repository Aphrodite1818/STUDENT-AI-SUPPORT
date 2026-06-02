function Input({ label, error, className = "", ...props }) {
  return (
    <div className="w-full">
      {label && (
        <label className="mb-1.5 block text-sm font-medium text-text-soft">
          {label}
        </label>
      )}
      <input className={`input-base ${className}`} {...props} />
      {error && <p className="mt-1 text-sm text-error">{error}</p>}
    </div>
  );
}

export default Input;
