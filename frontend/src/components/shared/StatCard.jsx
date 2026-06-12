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
    <Card className={cn("p-5", className)}>
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-sm font-medium text-text-muted">{label}</p>
          <p className="mt-2 text-3xl font-semibold tracking-tight text-text">{value}</p>
        </div>
        {Icon && (
          <span className={cn("flex h-11 w-11 items-center justify-center rounded-2xl", toneClasses[tone] || toneClasses.primary)}>
            <Icon className="h-5 w-5" />
          </span>
        )}
      </div>
      <div className="mt-4 flex flex-wrap items-center gap-2">
        {change && (
          <Badge variant={trend === "down" ? "error" : "success"}>
            <TrendIcon className="h-3.5 w-3.5" />
            {change}
          </Badge>
        )}
        {description && <span className="text-xs text-text-muted">{description}</span>}
      </div>
    </Card>
  );
}

export default StatCard;
