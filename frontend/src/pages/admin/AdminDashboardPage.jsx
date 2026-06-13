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
      description="Overview of users, teachers, and subjects in your school."
    >
      {overview.stats.length > 0 ? (
        <section className="stat-grid">
          {overview.stats.map((stat, index) => (
            <StatCard key={stat.label} {...stat} icon={statIcons[index]} compact />
          ))}
        </section>
      ) : (
        <EmptyState
          title="No dashboard metrics available"
          description="Metrics will appear here after the backend exposes dashboard summary endpoints."
        />
      )}

      <section className="dashboard-grid xl:grid-cols-2">
        <Card className="p-4 sm:p-5 md:p-6">
          <h2 className="section-title">Operational Snapshot</h2>
          <EmptyState
            title="No live operational feed"
            description="Timetable, attendance, performance, and notices will appear when backend data is available."
          />
        </Card>

        <Card className="hidden p-4 sm:p-5 md:block md:p-6">
          <h2 className="section-title">Activity Summary</h2>
          <div className="mt-4 space-y-3 text-sm leading-relaxed text-text-soft md:text-base md:leading-7">
            <p>Enrollment trends, attendance rates, and finance summaries require dedicated dashboard endpoints.</p>
          </div>
        </Card>
      </section>
    </DashboardLayout>
  );
}

export default AdminDashboardPage;
