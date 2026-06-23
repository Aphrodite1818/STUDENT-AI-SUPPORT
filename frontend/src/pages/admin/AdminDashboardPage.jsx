import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  BookOpen,
  GraduationCap,
  PlusCircle,
  Shapes,
  UserCheck,
  Users,
} from "lucide-react";
import DashboardLayout from "../../components/layout/DashboardLayout";
import Card from "../../components/ui/Card";
import Button from "../../components/ui/Button";
import StatCard from "../../components/shared/StatCard";
import LoadingState from "../../components/shared/LoadingState";
import EmptyState from "../../components/shared/EmptyState";
import AnalyticsBarChart from "../../components/charts/AnalyticsBarChart";
import AnalyticsDonutChart from "../../components/charts/AnalyticsDonutChart";
import { dashboardService } from "../../services/dashboard.service";
import { authSession, getErrorMessage } from "../../services/api";

const statItems = [
  { key: "total_students", label: "Students", description: "registered learners", icon: GraduationCap, tone: "primary" },
  { key: "total_teachers", label: "Teachers", description: "teacher accounts", icon: Users, tone: "success" },
  { key: "total_parents", label: "Parents", description: "parent accounts", icon: UserCheck, tone: "accent" },
  { key: "total_classes", label: "Classes", description: "academic groups", icon: Shapes, tone: "warning" },
  { key: "total_subjects", label: "Subjects", description: "active catalog items", icon: BookOpen, tone: "primary" },
  { key: "pending_parent_link_requests", label: "Pending Links", description: "awaiting student approval", icon: UserCheck, tone: "warning" },
];

function AdminDashboardPage() {
  const [analytics, setAnalytics] = useState(null);
  const [error, setError] = useState(null);
  const user = authSession.getUser();
  const firstName = user?.first_name || user?.firstname || "Admin";

  useEffect(() => {
    let mounted = true;

    async function loadDashboard() {
      try {
        const data = await dashboardService.getTenantAdminAnalytics();
        if (mounted) setAnalytics(data);
      } catch (err) {
        if (mounted) setError(getErrorMessage(err, "Failed to load dashboard analytics."));
      }
    }

    loadDashboard();

    return () => {
      mounted = false;
    };
  }, []);

  if (!analytics && !error) {
    return (
      <DashboardLayout role="admin" title="Dashboard">
        <LoadingState label="Loading dashboard..." />
      </DashboardLayout>
    );
  }

  const stats = analytics?.stats || {};

  return (
    <DashboardLayout
      role="admin"
      title={`${firstName}'s Dashboard`}
      description="Live tenant analytics for students, staff, classes, onboarding, and parent-link workflows."
      actions={
        <Link to="/admin/create-user">
          <Button>
            <PlusCircle className="h-4 w-4" />
            Create user
          </Button>
        </Link>
      }
    >
      {error && (
        <div className="rounded-2xl border border-error/30 bg-error-soft px-4 py-3 text-sm font-medium text-error">
          {error}
        </div>
      )}

      {!error && (
        <>
          <section className="stat-grid">
            {statItems.map((item) => (
              <StatCard
                key={item.key}
                label={item.label}
                value={stats[item.key] ?? 0}
                description={item.description}
                icon={item.icon}
                tone={item.tone}
                compact
              />
            ))}
          </section>

          <section className="dashboard-grid xl:grid-cols-2">
            <AnalyticsBarChart
              title="School Population"
              description="Real counts pulled from tenant-scoped analytics."
              data={analytics?.charts?.population_breakdown || []}
            />
            <AnalyticsDonutChart
              title="Student Profile Completion"
              description="Shows how many student profiles are complete versus still missing required fields."
              data={analytics?.charts?.profile_completion || []}
            />
          </section>

          <section className="dashboard-grid xl:grid-cols-[minmax(0,1fr)_minmax(0,360px)]">
            <AnalyticsBarChart
              title="Pending Workflows"
              description="Invite and link-request work waiting on people to finish the loop."
              data={analytics?.charts?.pending_workflows || []}
              emptyMessage="No pending workflow items right now."
            />
            <Card className="p-4 sm:p-5 md:p-6">
              <h2 className="section-title">Operational Snapshot</h2>
              {analytics ? (
                <div className="mt-4 space-y-3 text-sm text-text-soft">
                  <p>Student profiles complete: {stats.student_profiles_complete ?? 0}</p>
                  <p>Student profiles incomplete: {stats.student_profiles_incomplete ?? 0}</p>
                  <p>Pending invites: {stats.pending_user_invites ?? 0}</p>
                  <p>Pending parent-student approvals: {stats.pending_parent_link_requests ?? 0}</p>
                </div>
              ) : (
                <EmptyState
                  title="No analytics available"
                  description="Tenant analytics will appear here once the backend responds."
                />
              )}
            </Card>
          </section>
        </>
      )}
    </DashboardLayout>
  );
}

export default AdminDashboardPage;
