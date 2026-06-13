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
      description="Family information will appear here after parent/student backend endpoints are connected."
      actions={
        <Button variant="outline">
          <MessageSquare className="h-4 w-4" />
          Message school
        </Button>
      }
    >
      <section className="grid gap-5 lg:grid-cols-[minmax(0,1fr)_360px]">
        <Card className="p-5 sm:p-6">
          <h2 className="text-xl font-semibold">Family Overview</h2>
          <EmptyState
            title="No parent dashboard data yet"
            description="Children, attendance, results, fee status, and notices are hidden until they come from backend endpoints."
          />
        </Card>

        <Card className="p-5 sm:p-6">
          <h2 className="text-xl font-semibold">Parent Modules</h2>
          <div className="mt-5 grid gap-3">
            {links.map((item) => {
              const Icon = item.icon;
              return (
                <Link
                  key={item.to}
                  to={item.to}
                  className="flex items-center gap-3 rounded-2xl border border-border bg-surface px-4 py-3 font-semibold text-text-soft transition hover:border-primary/30 hover:bg-primary-subtle hover:text-primary"
                >
                  <Icon className="h-5 w-5" />
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
