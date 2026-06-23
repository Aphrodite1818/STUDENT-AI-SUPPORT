import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

const DEFAULT_COLORS = ["#0f766e", "#0ea5e9", "#f59e0b", "#ef4444", "#8b5cf6"];
const normalizeItems = (data, valueKey) =>
  Array.isArray(data)
    ? data.filter((item) => Number.isFinite(Number(item?.[valueKey])) && Number(item?.[valueKey]) >= 0)
    : [];
const formatLabel = (value) => String(value || "Unknown").replace(/_/g, " ");

function AnalyticsDonutChart({
  data = [],
  title,
  description,
  emptyMessage = "No chart data available yet.",
  labelKey = "label",
  valueKey = "value",
}) {
  const items = normalizeItems(data, valueKey);
  const total = items.reduce((sum, item) => sum + Number(item?.[valueKey] || 0), 0);

  return (
    <div className="min-w-0 rounded-3xl border border-border bg-surface p-4 sm:p-5">
      <div>
        <h3 className="text-base font-semibold text-text">{title}</h3>
        {description && <p className="mt-1 text-sm text-text-muted">{description}</p>}
      </div>

      {items.length === 0 ? (
        <div className="mt-5 rounded-2xl border border-dashed border-border bg-surface-muted/40 px-4 py-10 text-center text-sm text-text-muted">
          {emptyMessage}
        </div>
      ) : (
        <div className="mt-5 grid gap-4 lg:grid-cols-[minmax(0,220px)_minmax(0,1fr)] lg:items-center">
          <div className="mx-auto h-56 w-full max-w-[240px]">
            {total > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={items}
                    dataKey={valueKey}
                    nameKey={labelKey}
                    cx="50%"
                    cy="50%"
                    innerRadius={58}
                    outerRadius={88}
                    paddingAngle={2}
                  >
                    {items.map((item, index) => (
                      <Cell key={`${item?.[labelKey]}-${index}`} fill={DEFAULT_COLORS[index % DEFAULT_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex h-full items-center justify-center">
                <div className="flex h-44 w-44 flex-col items-center justify-center rounded-full border-[18px] border-surface-subtle bg-background text-center">
                  <span className="text-3xl font-semibold text-text">0</span>
                  <span className="mt-1 max-w-20 text-xs font-medium uppercase tracking-wide text-text-muted">
                    Awaiting data
                  </span>
                </div>
              </div>
            )}
          </div>

          <div className="space-y-3">
            {items.map((item, index) => (
              <div key={`${item?.[labelKey]}-${index}`} className="flex items-center justify-between gap-3 rounded-2xl border border-border bg-surface-muted/40 px-3 py-3">
                <div className="flex items-center gap-3">
                  <span
                    className="h-3 w-3 rounded-full"
                    style={{ backgroundColor: DEFAULT_COLORS[index % DEFAULT_COLORS.length] }}
                  />
                  <span className="text-sm font-medium text-text">
                    {formatLabel(item?.[labelKey])}
                  </span>
                </div>
                <span className="text-sm font-semibold text-text">{item?.[valueKey] ?? 0}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default AnalyticsDonutChart;
