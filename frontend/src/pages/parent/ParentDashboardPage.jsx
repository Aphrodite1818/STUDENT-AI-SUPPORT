import { Link } from "react-router-dom";
import { BarChart3, Bell, CreditCard, MessageSquare } from "lucide-react";
import DashboardLayout from "../../components/layout/DashboardLayout";
import Card from "../../components/ui/Card";
import Button from "../../components/ui/Button";
import EmptyState from "../../components/shared/EmptyState";
import { authSession } from "../../services/api";

const links = [
  { label: "Attendance", to: "/parent/attendance", icon: Bell },
  { label: "Results", to: "/parent/results", icon: BarChart3 },
  { label: "Notices", to: "/parent/notices", icon: MessageSquare },
  { label: "Fees", to: "/parent/fees", icon: CreditCard },
];

function ParentDashboardPage() {
  const user = authSession.getUser();
  const firstName = user?.firstname || "Parent";

  return (
    <DashboardLayout
      role="parent"
      title={`${firstName}'s Portal`}
      description="Track your children's attendance, results, and school notices."
      actions={
        <Button variant="outline" className="w-full sm:w-auto">
          <MessageSquare className="h-4 w-4" />
          Message school
        </Button>
      }
    >
      <section className="dashboard-grid lg:grid-cols-[minmax(0,1fr)_min(100%,360px)]">
        <Card className="p-4 sm:p-5 md:p-6">
          <h2 className="section-title">Family Overview</h2>
          <EmptyState
            title="No parent dashboard data yet"
            description="Children, attendance, results, and fee status will appear when backend endpoints are available."
          />
        </Card>

        <Card className="p-4 sm:p-5 md:p-6">
          <h2 className="section-title">Parent Modules</h2>
          <div className="mt-4 grid gap-2 sm:mt-5 sm:gap-3">
            {links.map((item) => {
              const Icon = item.icon;
              return (
                <Link
                  key={item.to}
                  to={item.to}
                  className="flex min-h-11 items-center gap-3 rounded-2xl border border-border bg-surface px-4 py-3 text-sm font-semibold text-text-soft transition hover:border-primary/30 hover:bg-primary-subtle hover:text-primary sm:text-base"
                >
                  <Icon className="h-5 w-5 shrink-0" />
                  {item.label}
                </Link>
              );
            })}
          </div>
        </Card>
      </section>
    </DashboardLayout>
  );
}

export default ParentDashboardPage;
