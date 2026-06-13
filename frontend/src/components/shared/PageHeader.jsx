function PageHeader({ eyebrow, title, description, actions }) {
  return (
    <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
      <div>
        {eyebrow && (
          <p className="text-xs font-bold uppercase tracking-wide text-primary">
            {eyebrow}
          </p>
        )}
        <h1 className="dashboard-title">
          {title}
        </h1>
        {description && (
          <p className="dashboard-subtitle">
            {description}
          </p>
        )}
      </div>
      {actions && <div className="flex flex-wrap gap-2">{actions}</div>}
    </div>
  );
}

export default PageHeader;
