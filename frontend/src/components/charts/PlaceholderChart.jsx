function PlaceholderChart({ title, description = "Coming Soon" }) {
  return (
    <div className="min-w-0 rounded-3xl border border-dashed border-border bg-surface p-4 sm:p-5">
      <div>
        <h3 className="text-base font-semibold text-text">{title}</h3>
        <p className="mt-1 text-sm text-text-muted">{description}</p>
      </div>
      <div className="mt-5 flex h-72 items-center justify-center rounded-2xl bg-surface-muted/40">
        <span className="rounded-full border border-border bg-surface px-4 py-2 text-sm font-semibold text-text-muted">
          Coming Soon
        </span>
      </div>
    </div>
  );
}

export default PlaceholderChart;
