const styles = {
  success: "border-success/15 bg-success-soft text-success",
  warning: "border-warning/20 bg-warning-soft text-warning",
  error: "border-error/15 bg-error-soft text-error",
  info: "border-secondary/10 bg-secondary-soft text-secondary",
};

function Badge({ variant = "info", children }) {
  return (
    <span
      className={`inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-semibold ${styles[variant]}`}
    >
      {children}
    </span>
  );
}

export default Badge;
