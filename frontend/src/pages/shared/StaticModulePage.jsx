import { CalendarDays, CheckCircle2, FileText, Plus, Settings, Sparkles } from "lucide-react";
import DashboardLayout from "../../components/layout/DashboardLayout";
import Card from "../../components/ui/Card";
import Button from "../../components/ui/Button";
import Badge from "../../components/ui/Badge";

const iconMap = {
  timetable: CalendarDays,
  settings: Settings,
  ai: Sparkles,
  notices: FileText,
  default: CheckCircle2,
};

function StaticModulePage({
  role = "admin",
  title,
  description,
  type = "default",
}) {
  const Icon = iconMap[type] || iconMap.default;

  return (
    <DashboardLayout
      role={role}
      title={title}
      description={description}
      actions={
        <Button>
          <Plus className="h-4 w-4" />
          New item
        </Button>
      }
    >
      <section className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_360px]">
        <Card className="p-5">
          <div className="flex items-start gap-4">
            <span className="flex h-12 w-12 items-center justify-center rounded-2xl bg-primary-soft text-primary">
              <Icon className="h-5 w-5" />
            </span>
            <div>
              <h2 className="text-lg font-semibold">{title}</h2>
              <p className="mt-1 text-sm leading-6 text-text-muted">
                This module is ready for real endpoint integration. The current screen provides realistic structure and interaction patterns so the app remains demoable.
              </p>
            </div>
          </div>

          <div className="mt-6 grid gap-4 md:grid-cols-2">
            {[
              ["Workflow status", "Ready for API connection", "success"],
              ["Responsive layout", "Desktop and mobile friendly", "primary"],
              ["Role scope", `${role} workspace`, "accent"],
              ["Next action", "Connect module endpoint", "warning"],
            ].map(([label, value, tone]) => (
              <div key={label} className="rounded-2xl border border-border bg-surface-muted/40 p-4">
                <p className="text-xs font-bold uppercase tracking-wide text-text-muted">{label}</p>
                <div className="mt-3 flex items-center justify-between gap-3">
                  <p className="font-semibold">{value}</p>
                  <Badge variant={tone}>{tone}</Badge>
                </div>
              </div>
            ))}
          </div>
        </Card>

        <Card className="p-5">
          <h2 className="text-lg font-semibold">Recent Activity</h2>
          <div className="mt-4 space-y-3">
            {["Screen layout prepared", "Service boundary preserved", "Mobile stacking verified by structure"].map((item) => (
              <div key={item} className="rounded-2xl bg-surface-muted/50 p-4">
                <p className="font-semibold">{item}</p>
                <p className="mt-1 text-sm text-text-muted">Demo-ready placeholder</p>
              </div>
            ))}
          </div>
        </Card>
      </section>
    </DashboardLayout>
  );
}

export default StaticModulePage;
