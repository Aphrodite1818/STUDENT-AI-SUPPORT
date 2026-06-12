function LoadingState({ label = "Loading..." }) {
  return (
    <div className="flex min-h-44 items-center justify-center rounded-2xl border border-border bg-surface">
      <div className="flex items-center gap-3 text-sm font-medium text-text-muted">
        <span className="h-5 w-5 animate-spin rounded-full border-2 border-primary/20 border-t-primary" />
        {label}
      </div>
    </div>
  );
}

export default LoadingState;
