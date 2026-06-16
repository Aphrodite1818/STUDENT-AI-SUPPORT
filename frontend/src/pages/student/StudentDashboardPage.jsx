import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { BarChart3, CalendarDays, ClipboardList, FileText, Link2, UserRound } from "lucide-react";
import DashboardLayout from "../../components/layout/DashboardLayout";
import Card from "../../components/ui/Card";
import Badge from "../../components/ui/Badge";
import EmptyState from "../../components/shared/EmptyState";
import LoadingState from "../../components/shared/LoadingState";
import StatCard from "../../components/shared/StatCard";
import { authSession, getErrorMessage } from "../../services/api";
import { studentService } from "../../services/studentService";

const links = [
  { label: "Timetable", to: "/student/timetable", icon: CalendarDays },
  { label: "Assignments", to: "/student/assignments", icon: ClipboardList },
  { label: "Results", to: "/student/results", icon: BarChart3 },
  { label: "Notices", to: "/student/notices", icon: FileText },
];

function StudentDashboardPage() {
  const [student, setStudent] = useState(null);
  const [parentLinks, setParentLinks] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [loadError, setLoadError] = useState(null);
  const user = authSession.getUser();
  const firstName = user?.firstname || "Student";

  useEffect(() => {
    let mounted = true;

    async function loadDashboard() {
      setIsLoading(true);
      setLoadError(null);

      try {
        const [studentProfile, linksResponse] = await Promise.all([
          studentService.getMyStudent(),
          studentService.getMyParentLinks(),
        ]);

        if (!mounted) return;

        setStudent(studentProfile);
        setParentLinks(linksResponse?.items || []);
      } catch (error) {
        if (mounted) setLoadError(getErrorMessage(error, "Failed to load student dashboard."));
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
      <DashboardLayout role="student" title={`${firstName}'s Portal`}>
        <LoadingState label="Loading student dashboard..." />
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout
      role="student"
      title={`${firstName}'s Portal`}
      description="Your academic overview, timetable, and assignments."
    >
      {loadError && (
        <div className="rounded-2xl border border-error/30 bg-error-soft px-4 py-3 text-sm font-medium text-error">
          {loadError}
        </div>
      )}

      {!loadError && student && (
        <section className="stat-grid">
          <StatCard
            label="Profile"
            value={student.profile_status === "complete" ? "Complete" : "Incomplete"}
            description="academic record"
            icon={UserRound}
            tone={student.profile_status === "complete" ? "success" : "warning"}
            compact
          />
          <StatCard
            label="Parent Links"
            value={parentLinks.length}
            description="approved contacts"
            icon={Link2}
            tone={parentLinks.length > 0 ? "primary" : "warning"}
            compact
          />
        </section>
      )}

      <section className="dashboard-grid lg:grid-cols-[minmax(0,1fr)_min(100%,360px)]">
        <Card className="p-4 sm:p-5 md:p-6">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <h2 className="section-title">Learning Overview</h2>
            {student?.status && <Badge variant="info">{student.status}</Badge>}
          </div>

          {student ? (
            <div className="mt-4 grid gap-3 text-sm text-text-soft sm:grid-cols-2">
              <div className="rounded-2xl border border-border bg-surface px-4 py-3">
                <p className="text-xs font-semibold uppercase tracking-wide text-text-muted">Admission number</p>
                <p className="mt-1 font-semibold text-text">{student.admission_number || "Not assigned"}</p>
              </div>
              <div className="rounded-2xl border border-border bg-surface px-4 py-3">
                <p className="text-xs font-semibold uppercase tracking-wide text-text-muted">Class</p>
                <p className="mt-1 font-semibold text-text">{student.class_id ? `Class ${student.class_id}` : "Not assigned"}</p>
              </div>
              <div className="rounded-2xl border border-border bg-surface px-4 py-3">
                <p className="text-xs font-semibold uppercase tracking-wide text-text-muted">Parent contacts</p>
                <p className="mt-1 font-semibold text-text">
                  {parentLinks.length > 0 ? `${parentLinks.length} linked` : "No linked parent yet"}
                </p>
              </div>
              <div className="rounded-2xl border border-border bg-surface px-4 py-3">
                <p className="text-xs font-semibold uppercase tracking-wide text-text-muted">Profile status</p>
                <p className="mt-1 font-semibold text-text">{student.profile_status}</p>
              </div>
            </div>
          ) : (
            <EmptyState
              title="No student profile found"
              description="Your account exists, but the school has not created your student academic profile yet."
            />
          )}
        </Card>

        <Card className="p-4 sm:p-5 md:p-6">
          <h2 className="section-title">Student Modules</h2>
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

export default StudentDashboardPage;
