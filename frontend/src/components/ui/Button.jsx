const variantStyles = {
  primary: "bg-primary text-text hover:bg-primary-hover hover:text-text-inverse",
  secondary:
    "border border-border bg-surface text-text-soft hover:bg-surface-muted hover:text-text",
  accent: "bg-secondary text-text-inverse hover:bg-secondary-hover",
  outline:
    "border border-border bg-white text-text-soft hover:border-primary hover:bg-primary-soft hover:text-text",
  danger: "bg-error text-text-inverse hover:bg-error/90",
};

const sizeStyles = {
  sm: "px-3.5 py-1.5 text-xs",
  small: "px-3.5 py-1.5 text-xs",
  medium: "px-5 py-2",
  large: "px-6 py-3 text-base",
};

function Button({
  children,
  variant = "primary",
  size = "medium",
  className = "",
  ...props
}) {
  return (
    <button
      className={`btn-base ${variantStyles[variant] || variantStyles.primary} ${sizeStyles[size] || sizeStyles.medium} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}

export default Button;
