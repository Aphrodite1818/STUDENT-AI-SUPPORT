import { useEffect, useState } from "react";
import { BookOpen, GraduationCap, Users } from "lucide-react";
import DashboardLayout from "../../components/layout/DashboardLayout";
import Card from "../../components/ui/Card";
import StatCard from "../../components/shared/StatCard";
import LoadingState from "../../components/shared/LoadingState";
import EmptyState from "../../components/shared/EmptyState";
import { dashboardService } from "../../services/dashboard.service";
import { authSession } from "../../services/api";

const statIcons = [Users, GraduationCap, BookOpen];

function AdminDashboardPage() {
  const [overview, setOverview] = useState(null);
  const user = authSession.getUser();
  const firstName = user?.firstname || "Admin";

  useEffect(() => {
    let mounted = true;
    dashboardService.getAdminOverview().then((data) => {
      if (mounted) setOverview(data);
    });
    return () => {
      mounted = false;
    };
  }, []);

  if (!overview) {
    return (
      <DashboardLayout role="admin" title="Dashboard">
        <LoadingState label="Loading dashboard..." />
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout
      role="admin"
      title={`${firstName}'s Dashboard`}
      description="Live tenant overview from currently available backend endpoints."
    >
      {overview.stats.length > 0 ? (
        <section className="grid gap-5 sm:grid-cols-2 xl:grid-cols-3">
          {overview.stats.map((stat, index) => (
            <StatCard key={stat.label} {...stat} icon={statIcons[index]} />
          ))}
        </section>
      ) : (
        <EmptyState
          title="No dashboard metrics available"
          description="Metrics will appear here after the backend exposes dashboard summary endpoints."
        />
      )}

      <section className="grid gap-5 xl:grid-cols-2">
        <Card className="p-5 sm:p-6">
          <h2 className="text-xl font-semibold">Operational Snapshot</h2>
          <EmptyState
            title="No live operational feed"
            description="Timetable, attendance, performance, and notices are hidden until real backend data is available."
          />
        </Card>

        <Card className="p-5 sm:p-6">
          <h2 className="text-xl font-semibold">Next Backend Work</h2>
          <div className="mt-4 space-y-3 text-base leading-7 text-text-soft">
            <p>Connect dashboard summary endpoints for attendance, enrollment trends, announcements, and finance.</p>
            <p>Once those APIs exist, the dashboard can safely show charts and activity widgets without fabricated values.</p>
          </div>
        </Card>
      </section>
    </DashboardLayout>
  );
}

export default AdminDashboardPage;
