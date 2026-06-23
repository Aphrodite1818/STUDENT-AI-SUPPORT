import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { BookOpen, CheckSquare, ClipboardList, ShieldCheck, Users } from "lucide-react";
import DashboardLayout from "../../components/layout/DashboardLayout";
import Card from "../../components/ui/Card";
import Button from "../../components/ui/Button";
import AnalyticsBarChart from "../../components/charts/AnalyticsBarChart";
import AnalyticsDonutChart from "../../components/charts/AnalyticsDonutChart";
import LoadingState from "../../components/shared/LoadingState";
import StatCard from "../../components/shared/StatCard";
import { authSession, getErrorMessage } from "../../services/api";
import { teacherService } from "../../services/teacherService";

const shortcuts = [
  { label: "My classes", to: "/teacher/classes", icon: Users },
  { label: "Students", to: "/teacher/students", icon: Users },
  { label: "Subjects", to: "/teacher/subjects", icon: BookOpen },
  { label: "Attendance", to: "/teacher/attendance", icon: CheckSquare },
  { label: "Results", to: "/teacher/results", icon: ClipboardList },
];

function TeacherDashboardPage() {
  const [teacher, setTeacher] = useState(null);
  const [subjects, setSubjects] = useState([]);
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
        const [teacherProfile, subjectResponse] = await Promise.all([
          teacherService.getMyTeacher(),
          teacherService.getMySubjects(),
        ]);

        if (!mounted) return;

        setTeacher(teacherProfile);
        setSubjects(subjectResponse?.items || []);
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
  const inactiveSubjects = Math.max(subjects.length - activeSubjects, 0);
  const readinessChecksComplete = [
    teacher?.profile_completed,
    teacher?.is_verified,
    teacher?.is_active,
  ].filter(Boolean).length;

  const workloadChartData = [
    { label: "assigned_subjects", value: subjects.length },
    { label: "active_subjects", value: activeSubjects },
    { label: "inactive_subjects", value: inactiveSubjects },
  ];

  const readinessChartData = [
    { label: "ready_checks", value: readinessChecksComplete },
    { label: "attention_needed", value: Math.max(3 - readinessChecksComplete, 0) },
  ];

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
            label="Assigned Subjects"
            value={subjects.length}
            description="current teaching load"
            icon={BookOpen}
            tone={subjects.length > 0 ? "primary" : "warning"}
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
            label="Readiness Checks"
            value={`${readinessChecksComplete}/3`}
            description="profile, verification, activity"
            icon={ShieldCheck}
            tone={readinessChecksComplete === 3 ? "success" : "warning"}
            compact
          />
        </section>
      )}

      {!loadError && (
        <section className="dashboard-grid xl:grid-cols-2">
          <AnalyticsBarChart
            title="Teaching Workload"
            description="Subject allocation split across active and inactive assignments."
            data={workloadChartData}
          />
          <AnalyticsDonutChart
            title="Account Readiness"
            description="Shows whether your teacher account is fully ready for day-to-day work."
            data={readinessChartData}
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
