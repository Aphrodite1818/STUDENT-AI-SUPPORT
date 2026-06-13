import { CalendarDays, CheckCircle2, FileText, Settings } from "lucide-react";
import DashboardLayout from "../../components/layout/DashboardLayout";
import Card from "../../components/ui/Card";
import EmptyState from "../../components/shared/EmptyState";

const iconMap = {
  timetable: CalendarDays,
  settings: Settings,
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
    <DashboardLayout role={role} title={title} description={description}>
      <Card className="p-5 sm:p-6">
        <EmptyState
          icon={Icon}
          title={`${title} is not connected yet`}
          description="This screen is intentionally empty until a real backend endpoint is available. No placeholder activity or fabricated records are shown."
        />
      </Card>
    </DashboardLayout>
  );
}

export default StaticModulePage;
