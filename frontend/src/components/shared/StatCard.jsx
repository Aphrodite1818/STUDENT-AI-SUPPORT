import { ArrowDownRight, ArrowUpRight } from "lucide-react";
import Card from "../ui/Card";
import Badge from "../ui/Badge";
import { cn } from "../../utils/cn";

const toneClasses = {
  primary: "bg-primary-soft text-primary",
  success: "bg-success-soft text-emerald-700",
  warning: "bg-warning-soft text-amber-700",
  error: "bg-error-soft text-rose-700",
  accent: "bg-accent-soft text-accent",
};

function StatCard({
  label,
  value,
  change,
  trend = "up",
  icon: Icon,
  tone = "primary",
  description,
  className = "",
}) {
  const TrendIcon = trend === "down" ? ArrowDownRight : ArrowUpRight;

  return (
    <Card className={cn("min-h-[148px] p-4 sm:p-5 md:p-6 bg-surface shadow-sm border-border/40", className)}>
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0">
          <p className="text-[13px] font-medium tracking-wide text-text-muted uppercase">{label}</p>
          <p className="mt-2 truncate text-2xl font-semibold tracking-tight text-text sm:text-3xl md:text-4xl">{value}</p>
        </div>
        {Icon && (
          <span className={cn("flex h-10 w-10 shrink-0 items-center justify-center rounded-[14px] sm:h-12 sm:w-12", toneClasses[tone] || toneClasses.primary)}>
            <Icon className="h-5 w-5 sm:h-6 sm:w-6" />
          </span>
        )}
      </div>
      <div className="mt-5 flex flex-wrap items-center gap-2">
        {change && (
          <Badge variant={trend === "down" ? "error" : "success"}>
            <TrendIcon className="h-3.5 w-3.5" />
            {change}
          </Badge>
        )}
        {description && <span className="text-xs font-medium text-text-muted">{description}</span>}
      </div>
    </Card>
  );
}

export default StatCard;
