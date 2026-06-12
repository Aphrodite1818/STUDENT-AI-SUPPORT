import { useEffect, useState } from "react";
import { Bell, CreditCard, GraduationCap, MessageSquare } from "lucide-react";
import DashboardLayout from "../../components/layout/DashboardLayout";
import Card from "../../components/ui/Card";
import Badge from "../../components/ui/Badge";
import Button from "../../components/ui/Button";
import StatCard from "../../components/shared/StatCard";
import LoadingState from "../../components/shared/LoadingState";
import { dashboardService } from "../../services/dashboard.service";

function ParentDashboardPage() {
  const [overview, setOverview] = useState(null);

  useEffect(() => {
    let mounted = true;
    dashboardService.getParentOverview().then((data) => {
      if (mounted) setOverview(data);
    });
    return () => {
      mounted = false;
    };
  }, []);

  if (!overview) {
    return (
      <DashboardLayout role="parent" title="Parent Dashboard">
        <LoadingState label="Loading parent portal..." />
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout
      role="parent"
      title="Parent Portal"
      description="Track attendance, results, fee status, and school communication for your children."
      actions={<Button variant="outline"><MessageSquare className="h-4 w-4" /> Message school</Button>}
    >
      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {overview.stats.map((stat, index) => {
          const icons = [GraduationCap, Bell, CreditCard, MessageSquare];
          const Icon = icons[index];
          return <StatCard key={stat.label} {...stat} icon={Icon} />;
        })}
      </section>

      <section className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_380px]">
        <Card className="p-5">
          <h2 className="text-lg font-semibold">Children Overview</h2>
          <div className="mt-5 grid gap-4 md:grid-cols-2">
            {[
              ["Maya Cole", "Grade 8 - A", "92% attendance", "A average"],
              ["Tunde Adebayo", "Grade 7 - B", "89% attendance", "B average"],
            ].map(([name, className, attendance, grade]) => (
              <div key={name} className="rounded-2xl border border-border bg-surface p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-semibold">{name}</p>
                    <p className="text-sm text-text-muted">{className}</p>
                  </div>
                  <Badge variant="success">Active</Badge>
                </div>
                <div className="mt-4 grid gap-3 sm:grid-cols-2">
                  <div className="rounded-xl bg-surface-muted p-3 text-sm font-semibold">{attendance}</div>
                  <div className="rounded-xl bg-surface-muted p-3 text-sm font-semibold">{grade}</div>
                </div>
              </div>
            ))}
          </div>
        </Card>

        <div className="space-y-6">
          <Card className="p-5">
            <h2 className="text-lg font-semibold">Fee Status</h2>
            <p className="mt-3 text-3xl font-semibold">NGN 42k</p>
            <p className="mt-1 text-sm text-text-muted">Outstanding this term</p>
            <Button className="mt-5 w-full">View payment details</Button>
          </Card>

          <Card className="p-5">
            <h2 className="text-lg font-semibold">Latest Notice</h2>
            <p className="mt-3 font-semibold">Parent-Teacher Meeting</p>
            <p className="mt-1 text-sm leading-6 text-text-muted">
              PTM for Grades 6-10 will be held on May 18, 2025.
            </p>
          </Card>
        </div>
      </section>
    </DashboardLayout>
  );
}

export default ParentDashboardPage;
