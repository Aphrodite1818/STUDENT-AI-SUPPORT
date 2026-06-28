import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { BarChart3, BookOpen, CheckSquare, ClipboardList, Send, Users } from "lucide-react";
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
import { academicService } from "../../services/academicService";
import {
  averageBy,
  chartFromCounts,
  cleanText,
  completionPercent,
} from "../../utils/academicDashboard";

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
  const [assignments, setAssignments] = useState([]);
  const [results, setResults] = useState([]);
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
        const [teacherProfile, subjectResponse, assignmentResponse, resultResponse, metricsResponse] = await Promise.all([
          teacherService.getMyTeacher(),
          teacherService.getMySubjects(),
          academicService.listTeacherAssignments(),
          academicService.listTeacherResults(),
          dashboardService.getTeacherAnalytics(),
        ]);

        if (!mounted) return;

        setTeacher(teacherProfile);
        setSubjects(subjectResponse?.items || []);
        setAssignments(assignmentResponse?.items || []);
        setResults(resultResponse?.items || []);
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

  const charts = metrics?.charts || {};
  const classSizeByLabel = useMemo(
    () => Object.fromEntries((charts.class_sizes || []).map((item) => [cleanText(item.label), Number(item.value || 0)])),
    [charts.class_sizes]
  );
  const assignedClassLabels = useMemo(
    () =>
      [...new Set(assignments.map((item) => cleanText([item.class_name, item.class_arm].filter(Boolean).join(" "), "")))].filter(Boolean),
    [assignments]
  );

  if (isLoading) {
    return (
      <DashboardLayout role="teacher" title={`${firstName}'s Workspace`}>
        <LoadingState label="Loading teacher dashboard..." />
      </DashboardLayout>
    );
  }

  const activeSubjects = subjects.filter((subject) => subject?.is_active !== false).length;
  const expectedSubmissions = assignments.reduce((sum, item) => {
    const label = cleanText([item.class_name, item.class_arm].filter(Boolean).join(" "), "");
    return sum + Number(classSizeByLabel[label] || 0);
  }, 0);
  const submittedResults = results.filter((item) => ["submitted", "published", "locked"].includes(item.status)).length;
  const pendingSubmissions = Math.max(expectedSubmissions - submittedResults, 0);
  const resultCompletion = completionPercent(submittedResults, expectedSubmissions);
  const pendingByClass = assignedClassLabels.map((label) => {
    const expected = assignments
      .filter((item) => cleanText([item.class_name, item.class_arm].filter(Boolean).join(" "), "") === label)
      .reduce((sum) => sum + Number(classSizeByLabel[label] || 0), 0);
    const submitted = results.filter((item) => cleanText([item.class_name, item.class_arm].filter(Boolean).join(" "), "") === label && ["submitted", "published", "locked"].includes(item.status)).length;
    return { label, value: Math.max(expected - submitted, 0) };
  });

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
            value={assignedClassLabels.length || metrics?.stats?.total_classes || 0}
            description="classes you teach"
            icon={Users}
            tone={(metrics?.stats?.total_classes ?? 0) > 0 ? "primary" : "warning"}
            compact
          />
          <StatCard
            label="Active Subjects"
            value={assignments.length || activeSubjects}
            description="assigned class-subjects"
            icon={ClipboardList}
            tone="success"
            compact
          />
          <StatCard
            label="Students Taught"
            value={(charts.class_sizes || []).reduce((sum, item) => sum + Number(item.value || 0), 0)}
            description="across assigned classes"
            icon={Users}
            tone="primary"
            compact
          />
          <StatCard
            label="Pending Submissions"
            value={pendingSubmissions}
            description={`${resultCompletion}% complete`}
            icon={BarChart3}
            tone={pendingSubmissions > 0 ? "warning" : "success"}
            compact
          />
          <StatCard
            label="Submitted Results"
            value={submittedResults}
            description="sent for review or publishing"
            icon={Send}
            tone="success"
            compact
          />
          <StatCard
            label="Published Results"
            value={metrics?.stats?.results_published ?? results.filter((item) => ["published", "locked"].includes(item.status)).length}
            description="visible to students"
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
            title="Result Status Breakdown"
            description="Draft, submitted, published, and locked scores you have entered."
            data={chartFromCounts(results, "status", "draft")}
            emptyMessage="No result status data available yet."
          />
          <AnalyticsDonutChart
            title="Grade Distribution"
            description="Grade spread for students in your assigned subjects."
            data={charts.grade_distribution || chartFromCounts(results, "grade", "ungraded")}
            emptyMessage="No grade distribution available yet."
          />
          <AnalyticsBarChart
            title="Class Average By Subject"
            description="Average score for each assigned class-subject."
            data={averageBy(results, (item) => `${item.subject_code || item.subject_name || "Subject"} - ${[item.class_name, item.class_arm].filter(Boolean).join(" ") || "Class"}`)}
            emptyMessage="No class-subject performance data available yet."
          />
          <AnalyticsBarChart
            title="Pending Submissions By Class"
            description="Estimated pending rows from assigned classes and submitted results."
            data={pendingByClass}
            emptyMessage="No pending submission data available yet."
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
          <Link to="/teacher/results" className="mt-3 block">
            <Button variant="success" className="w-full">
              <Send className="h-4 w-4" />
              Enter scores
            </Button>
          </Link>
        </Card>
      </section>
    </DashboardLayout>
  );
}

export default TeacherDashboardPage;
