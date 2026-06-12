import { cn } from "../../utils/cn";

const variantStyles = {
  primary: "bg-primary text-text-inverse shadow-sm shadow-primary/20 hover:bg-primary-hover",
  secondary: "bg-secondary text-text-inverse hover:bg-secondary-hover",
  accent: "bg-accent text-text-inverse shadow-sm shadow-accent/20 hover:bg-accent-hover",
  outline: "border border-border bg-surface text-text-soft hover:border-primary/40 hover:bg-primary-subtle hover:text-primary",
  ghost: "bg-transparent text-text-soft hover:bg-surface-muted hover:text-text",
  danger: "bg-error text-text-inverse hover:bg-error-hover",
  success: "bg-success text-text-inverse hover:bg-success-hover",
};

const sizeStyles = {
  xs: "min-h-8 rounded-lg px-2.5 py-1.5 text-xs",
  sm: "min-h-9 rounded-lg px-3 py-1.5 text-xs",
  small: "min-h-9 rounded-lg px-3 py-1.5 text-xs",
  medium: "min-h-10 px-4 py-2 text-sm",
  large: "min-h-12 rounded-2xl px-5 py-3 text-base",
  icon: "h-10 w-10 rounded-xl !p-0",
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
      className={cn(
        "btn-base",
        variantStyles[variant] || variantStyles.primary,
        sizeStyles[size] || sizeStyles.medium,
        className
      )}
      {...props}
    >
      {children}
    </button>
  );
}

export default Button;
