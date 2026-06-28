import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { BarChart3, BookOpen, CalendarDays, ClipboardList, FileText, Link2, UserRound } from "lucide-react";
import DashboardLayout from "../../components/layout/DashboardLayout";
import Card from "../../components/ui/Card";
import Badge from "../../components/ui/Badge";
import Button from "../../components/ui/Button";
import AnalyticsBarChart from "../../components/charts/AnalyticsBarChart";
import AnalyticsDonutChart from "../../components/charts/AnalyticsDonutChart";
import EmptyState from "../../components/shared/EmptyState";
import LoadingState from "../../components/shared/LoadingState";
import StatCard from "../../components/shared/StatCard";
import { authSession, getErrorMessage } from "../../services/api";
import { dashboardService } from "../../services/dashboard.service";
import { studentService } from "../../services/studentService";
import { academicService } from "../../services/academicService";
import { reportCardService } from "../../services/reportCardService";
import { displayName } from "../../utils/user";
import {
  averageScore,
  bestAndWeakestSubject,
  chartFromCounts,
  cleanText,
  reportCardStatusChart,
  subjectPerformanceChart,
} from "../../utils/academicDashboard";

const links = [
  { label: "Timetable", to: "/student/timetable", icon: CalendarDays },
  { label: "Assignments", to: "/student/assignments", icon: ClipboardList },
  { label: "Results", to: "/student/results", icon: BarChart3 },
  { label: "Notices", to: "/student/notices", icon: FileText },
];

function StudentDashboardPage() {
  const [student, setStudent] = useState(null);
  const [parentLinks, setParentLinks] = useState([]);
  const [parentLinkRequests, setParentLinkRequests] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [academicResults, setAcademicResults] = useState([]);
  const [reportCards, setReportCards] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [loadError, setLoadError] = useState(null);
  const [requestActionId, setRequestActionId] = useState(null);
  const user = authSession.getUser();
  const firstName = user?.first_name || user?.firstname || "Student";

  const loadDashboardData = async () => {
    const [
      studentProfile,
      linksResponse,
      requestsResponse,
      metricsResponse,
      resultResponse,
      reportCardResponse,
    ] = await Promise.all([
      studentService.getMyStudent(),
      studentService.getMyParentLinks(),
      studentService.getMyParentLinkRequests(),
      dashboardService.getStudentAnalytics(),
      academicService.listMyResults(),
      reportCardService.listMyReportCards(),
    ]);

    setStudent(studentProfile);
    setParentLinks(linksResponse?.items || []);
    setParentLinkRequests(requestsResponse?.items || []);
    setMetrics(metricsResponse);
    setAcademicResults(resultResponse?.items || []);
    setReportCards(reportCardResponse?.items || []);
  };

  useEffect(() => {
    let mounted = true;

    async function loadDashboard() {
      setIsLoading(true);
      setLoadError(null);

      try {
        await loadDashboardData();
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

  const handleRequestResponse = async (requestId, action) => {
    setRequestActionId(requestId);
    setLoadError(null);

    try {
      await studentService.respondToParentLinkRequest(requestId, { action });
      await loadDashboardData();
    } catch (error) {
      setLoadError(getErrorMessage(error, "Could not update parent link request."));
    } finally {
      setRequestActionId(null);
    }
  };

  const printReportCard = async (card) => {
    setLoadError(null);
    try {
      await reportCardService.printStudentReportCard(card.id);
    } catch (error) {
      setLoadError(getErrorMessage(error, "Could not open report card."));
    }
  };

  const charts = metrics?.charts || {};
  const currentAcademicLabel = useMemo(() => {
    const latestResult = academicResults[0];
    const latestCard = reportCards[0];
    const session = latestResult?.academic_session_name || latestCard?.academic_session_name;
    const term = latestResult?.academic_term_name || latestCard?.academic_term_name;
    return [session, cleanText(term, "")].filter(Boolean).join(" - ") || "-";
  }, [academicResults, reportCards]);

  if (isLoading) {
    return (
      <DashboardLayout role="student" title={`${firstName}'s Portal`}>
        <LoadingState label="Loading student dashboard..." />
      </DashboardLayout>
    );
  }

  const subjectHighlights = bestAndWeakestSubject(academicResults);
  const currentAverage = metrics?.stats?.current_average ?? averageScore(academicResults);

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
          <StatCard
            label="Current Average"
            value={currentAverage}
            description="published subjects"
            icon={BarChart3}
            tone={academicResults.length > 0 ? "success" : "warning"}
            compact
          />
          <StatCard
            label="Session / Term"
            value={currentAcademicLabel}
            description="latest academic context"
            icon={CalendarDays}
            tone={currentAcademicLabel !== "-" ? "primary" : "warning"}
            compact
          />
          <StatCard
            label="Best Subject"
            value={subjectHighlights.best?.label || "-"}
            description={subjectHighlights.best ? `${subjectHighlights.best.value} average score` : "awaiting results"}
            icon={BookOpen}
            tone={subjectHighlights.best ? "success" : "warning"}
            compact
          />
          <StatCard
            label="Needs Attention"
            value={subjectHighlights.weakest?.label || "-"}
            description={subjectHighlights.weakest ? `${subjectHighlights.weakest.value} average score` : "awaiting results"}
            icon={ClipboardList}
            tone={subjectHighlights.weakest ? "warning" : "primary"}
            compact
          />
        </section>
      )}

      {!loadError && student && (
        <section className="dashboard-grid xl:grid-cols-2">
          <AnalyticsBarChart
            title="Subject Comparison"
            description="Published scores by subject."
            data={charts.subject_comparison || subjectPerformanceChart(academicResults)}
            emptyMessage="No published result data available yet."
          />
          <AnalyticsDonutChart
            title="Grade Distribution"
            description="Published grade spread across subjects."
            data={charts.grade_distribution || chartFromCounts(academicResults, "grade", "ungraded")}
            emptyMessage="No grade distribution available yet."
          />
          <AnalyticsDonutChart
            title="Result Status"
            description="Availability state for your subject results."
            data={chartFromCounts(academicResults, "status", "not available")}
            emptyMessage="No result status data available yet."
          />
          <AnalyticsDonutChart
            title="Report Card Status"
            description="Generated and published report cards."
            data={reportCardStatusChart(reportCards)}
            emptyMessage="No report cards have been generated yet."
          />
        </section>
      )}

      {!loadError && (
        <section className="dashboard-grid xl:grid-cols-[minmax(0,1fr)_minmax(320px,420px)]">
          <Card className="p-4 sm:p-5 md:p-6">
            <h2 className="section-title">Subject Results</h2>
            <div className="mt-4 grid gap-3 md:grid-cols-2">
              {academicResults.length === 0 ? (
                <p className="text-sm font-medium text-text-muted">No result available yet.</p>
              ) : (
                academicResults.map((result) => (
                  <div key={result.id} className="rounded-2xl border border-border bg-surface px-4 py-3">
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <p className="font-semibold text-text">{result.subject_name || "Subject"}</p>
                        <p className="text-xs text-text-muted">{cleanText(result.subject_code)}</p>
                      </div>
                      <Badge variant={result.status === "published" || result.status === "locked" ? "success" : "warning"}>
                        {cleanText(result.status)}
                      </Badge>
                    </div>
                    <div className="mt-3 grid grid-cols-2 gap-2 text-sm text-text-soft">
                      <p>Teacher: {cleanText(result.teacher_name)}</p>
                      <p>Test: {cleanText(result.test_score)}</p>
                      <p>Assessment: {cleanText(result.assessment_score)}</p>
                      <p>Exam: {cleanText(result.exam_score)}</p>
                      <p>Total: {cleanText(result.total_score)}</p>
                      <p>Grade: {cleanText(result.grade)}</p>
                    </div>
                    <p className="mt-2 text-sm font-medium text-text">{cleanText(result.remark, "No result available yet.")}</p>
                  </div>
                ))
              )}
            </div>
          </Card>

          <Card className="p-4 sm:p-5 md:p-6">
            <h2 className="section-title">Report Cards</h2>
            <div className="mt-4 space-y-3">
              {reportCards.length === 0 ? (
                <p className="text-sm font-medium text-text-muted">No report card available yet.</p>
              ) : (
                reportCards.map((card) => (
                  <div key={card.id} className="rounded-2xl border border-border bg-surface px-4 py-3">
                    <p className="font-semibold text-text">
                      {cleanText(card.academic_session_name, "Session")} - {cleanText(card.academic_term_name, "Term")}
                    </p>
                    <p className="mt-1 text-sm text-text-muted">Average score: {cleanText(card.average_score)}</p>
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      className="mt-3"
                      onClick={() => printReportCard(card)}
                    >
                      Print or download
                    </Button>
                  </div>
                ))
              )}
            </div>
          </Card>
        </section>
      )}

      <section className="dashboard-grid lg:grid-cols-[minmax(0,1fr)_min(100%,360px)]">
        <Card className="p-4 sm:p-5 md:p-6">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <h2 className="section-title">Profile Overview</h2>
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
                <p className="mt-1 font-semibold text-text">{student.class_id ? "Assigned" : "Not assigned"}</p>
              </div>
              <div className="rounded-2xl border border-border bg-surface px-4 py-3">
                <p className="text-xs font-semibold uppercase tracking-wide text-text-muted">Parent contacts</p>
                <p className="mt-1 font-semibold text-text">
                  {parentLinks.length > 0 ? `${parentLinks.length} linked` : "No linked parent yet"}
                </p>
                {parentLinks.length > 0 && (
                  <p className="mt-2 text-xs text-text-muted">
                    {parentLinks.map((link) => displayName(link.parent)).join(", ")}
                  </p>
                )}
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
          <h2 className="section-title">Parent Link Requests</h2>
          <div className="mt-4 space-y-3">
            {parentLinkRequests.length === 0 ? (
              <p className="text-sm text-text-muted">
                No pending parent-link requests.
              </p>
            ) : (
              parentLinkRequests.map((request) => (
                <div key={request.id} className="rounded-2xl border border-border bg-surface px-4 py-3">
                  <p className="text-sm font-semibold text-text">{displayName(request.parent)}</p>
                  <p className="mt-1 text-xs text-text-muted">
                    {request.parent?.email || "No email provided"}
                  </p>
                  <div className="mt-3 grid gap-2 sm:grid-cols-2">
                    <Button
                      type="button"
                      onClick={() => handleRequestResponse(request.id, "approve")}
                      disabled={requestActionId === request.id}
                    >
                      {requestActionId === request.id ? "Saving..." : "Approve"}
                    </Button>
                    <Button
                      type="button"
                      variant="outline"
                      onClick={() => handleRequestResponse(request.id, "reject")}
                      disabled={requestActionId === request.id}
                    >
                      Reject
                    </Button>
                  </div>
                </div>
              ))
            )}
          </div>

          <div className="my-5 border-t border-border" />

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
