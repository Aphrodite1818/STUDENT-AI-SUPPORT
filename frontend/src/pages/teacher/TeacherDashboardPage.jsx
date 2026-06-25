import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { BookOpen, CheckSquare, ClipboardList, Users } from "lucide-react";
import DashboardLayout from "../../components/layout/DashboardLayout";
import Card from "../../components/ui/Card";
import Button from "../../components/ui/Button";
import AnalyticsBarChart from "../../components/charts/AnalyticsBarChart";
import AnalyticsDonutChart from "../../components/charts/AnalyticsDonutChart";
import LoadingState from "../../components/shared/LoadingState";
import StatCard from "../../components/shared/StatCard";
import { authSession, getErrorMessage } from "../../services/api";
import { dashboardService } from "../../services/dashboard.service";
import { teacherService } from "../../services/teacherService";

const shortcuts = [
  { label: "My classes", to: "/teacher/classes", icon: Users },
  { label: "Students", to: "/teacher/students", icon: Users },
  { label: "Subjects", to: "/teacher/subjects", icon: BookOpen },
  { label: "Attendance", to: "/teacher/attendance", icon: CheckSquare },
  { label: "Notices", to: "/teacher/announcements", icon: ClipboardList },
  { label: "Results", to: "/teacher/results", icon: ClipboardList },
];

function TeacherDashboardPage() {
  const [teacher, setTeacher] = useState(null);
  const [subjects, setSubjects] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [loadError, setLoadError] = useState(null);
  const user = authSession.getUser();
  const firstName = user?.first_name || user?.firstname || "Teacher";

  useEffect(() => {
    let mounted = true;

    async function loadDashboard() {
      setIsLoading(true);
      setLoadError(null);

      try {
        const [teacherProfile, subjectResponse, metricsResponse] = await Promise.all([
          teacherService.getMyTeacher(),
          teacherService.getMySubjects(),
          dashboardService.getTeacherAnalytics(),
        ]);

        if (!mounted) return;

        setTeacher(teacherProfile);
        setSubjects(subjectResponse?.items || []);
        setMetrics(metricsResponse);
      } catch (error) {
        if (mounted) {
          setLoadError(getErrorMessage(error, "Failed to load teacher dashboard."));
        }
      } finally {
        if (mounted) setIsLoading(false);
      }
    }

    loadDashboard();

    return () => {
      mounted = false;
    };
  }, []);

  if (isLoading) {
    return (
      <DashboardLayout role="teacher" title={`${firstName}'s Workspace`}>
        <LoadingState label="Loading teacher dashboard..." />
      </DashboardLayout>
    );
  }

  const activeSubjects = subjects.filter((subject) => subject?.is_active !== false).length;
  const charts = metrics?.charts || {};

  return (
    <DashboardLayout
      role="teacher"
      title={`${firstName}'s Workspace`}
      description="Access your classes, attendance, and teaching tools."
    >
      {loadError && (
        <div className="rounded-2xl border border-error/30 bg-error-soft px-4 py-3 text-sm font-medium text-error">
          {loadError}
        </div>
      )}

      {!loadError && (
        <section className="stat-grid">
          <StatCard
            label="Assigned Classes"
            value={metrics?.stats?.total_classes ?? 0}
            description="classes you teach"
            icon={Users}
            tone={(metrics?.stats?.total_classes ?? 0) > 0 ? "primary" : "warning"}
            compact
          />
          <StatCard
            label="Active Subjects"
            value={activeSubjects}
            description="currently enabled"
            icon={ClipboardList}
            tone="success"
            compact
          />
          <StatCard
            label="Announcements"
            value={metrics?.stats?.total_announcements ?? 0}
            description="created by you"
            icon={ClipboardList}
            tone="primary"
            compact
          />
        </section>
      )}

      {!loadError && (
        <section className="dashboard-grid xl:grid-cols-2">
          <AnalyticsBarChart
            title="Class Sizes"
            description="Number of students in each class assigned to you."
            data={charts.class_sizes || []}
            emptyMessage="No class size data available yet."
          />
          <AnalyticsDonutChart
            title="Announcement Read Vs Acknowledged"
            description="Engagement on announcements you created."
            data={charts.announcement_read_vs_acknowledged || []}
            emptyMessage="No announcement engagement data available yet."
          />
          <AnalyticsDonutChart
            title="Announcement Category Breakdown"
            description="Types of announcements you have posted."
            data={charts.announcement_category_breakdown || []}
            emptyMessage="No announcement categories available yet."
          />
        </section>
      )}

      <section className="dashboard-grid lg:grid-cols-[minmax(0,1fr)_min(100%,380px)]">
        <Card className="p-4 sm:p-5 md:p-6">
          <h2 className="section-title">Teaching Overview</h2>
          <div className="mt-4 grid gap-3 text-sm text-text-soft sm:grid-cols-2">
            <div className="rounded-2xl border border-border bg-surface px-4 py-3">
              <p className="text-xs font-semibold uppercase tracking-wide text-text-muted">Profile status</p>
              <p className="mt-1 font-semibold text-text">
                {teacher?.profile_completed ? "Complete" : "Needs attention"}
              </p>
            </div>
            <div className="rounded-2xl border border-border bg-surface px-4 py-3">
              <p className="text-xs font-semibold uppercase tracking-wide text-text-muted">Verification</p>
              <p className="mt-1 font-semibold text-text">
                {teacher?.is_verified ? "Verified" : "Pending verification"}
              </p>
            </div>
            <div className="rounded-2xl border border-border bg-surface px-4 py-3">
              <p className="text-xs font-semibold uppercase tracking-wide text-text-muted">Specialization</p>
              <p className="mt-1 font-semibold text-text">
                {teacher?.specialization || "Not provided"}
              </p>
            </div>
            <div className="rounded-2xl border border-border bg-surface px-4 py-3">
              <p className="text-xs font-semibold uppercase tracking-wide text-text-muted">Staff ID</p>
              <p className="mt-1 font-semibold text-text">
                {teacher?.staff_id || "Not assigned"}
              </p>
            </div>
          </div>
        </Card>

        <Card className="p-4 sm:p-5 md:p-6">
          <h2 className="section-title">Quick Actions</h2>
          <div className="mt-4 grid gap-2 sm:mt-5 sm:gap-3">
            {shortcuts.map((shortcut) => {
              const Icon = shortcut.icon;
              return (
                <Link
                  key={shortcut.to}
                  to={shortcut.to}
                  className="flex min-h-11 items-center gap-3 rounded-2xl border border-border bg-surface px-4 py-3 text-sm font-semibold text-text-soft transition hover:border-primary/30 hover:bg-primary-subtle hover:text-primary sm:text-base"
                >
                  <Icon className="h-5 w-5 shrink-0" />
                  {shortcut.label}
                </Link>
              );
            })}
          </div>
          <Link to="/teacher/attendance" className="mt-4 block sm:mt-5">
            <Button className="w-full">
              <CheckSquare className="h-4 w-4" />
              Open attendance
            </Button>
          </Link>
        </Card>
      </section>
    </DashboardLayout>
  );
}

export default TeacherDashboardPage;
