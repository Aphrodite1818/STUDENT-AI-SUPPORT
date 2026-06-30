import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { BarChart3, Bell, CreditCard, GraduationCap, Link2, MessageSquare, Users } from "lucide-react";
import DashboardLayout from "../../components/layout/DashboardLayout";
import Card from "../../components/ui/Card";
import Button from "../../components/ui/Button";
import Badge from "../../components/ui/Badge";
import AnalyticsBarChart from "../../components/charts/AnalyticsBarChart";
import AnalyticsDonutChart from "../../components/charts/AnalyticsDonutChart";
import EmptyState from "../../components/shared/EmptyState";
import LoadingState from "../../components/shared/LoadingState";
import StatCard from "../../components/shared/StatCard";
import { authSession, getErrorMessage } from "../../services/api";
import { parentService } from "../../services/parentService";
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
  { label: "Attendance", to: "/parent/attendance", icon: Bell },
  { label: "Results", to: "/parent/results", icon: BarChart3 },
  { label: "Notices", to: "/parent/notices", icon: MessageSquare },
  { label: "Fees", to: "/parent/fees", icon: CreditCard },
];

function ParentDashboardPage() {
  const [children, setChildren] = useState([]);
  const [requests, setRequests] = useState([]);
  const [selectedChildId, setSelectedChildId] = useState("");
  const [childResults, setChildResults] = useState([]);
  const [childReportCards, setChildReportCards] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isLinking, setIsLinking] = useState(false);
  const [admissionNumber, setAdmissionNumber] = useState("");
  const [relationshipType, setRelationshipType] = useState("guardian");
  const [loadError, setLoadError] = useState(null);
  const [linkError, setLinkError] = useState(null);
  const [linkSuccess, setLinkSuccess] = useState(null);
  const user = authSession.getUser();
  const firstName = user?.first_name || user?.firstname || "Parent";

  const loadDashboardData = async () => {
    const [studentsResponse, requestsResponse] = await Promise.all([
      parentService.getMyStudents(),
      parentService.getMyStudentLinkRequests(),
    ]);
    setChildren(studentsResponse?.items || []);
    setRequests(requestsResponse?.items || []);
    if (!selectedChildId && studentsResponse?.items?.[0]?.student?.id) {
      setSelectedChildId(studentsResponse.items[0].student.id);
    }
  };

  useEffect(() => {
    let mounted = true;

    async function loadDashboard() {
      setIsLoading(true);
      setLoadError(null);

      try {
        await loadDashboardData();
      } catch (error) {
        if (mounted) setLoadError(getErrorMessage(error, "Failed to load linked students."));
      } finally {
        if (mounted) setIsLoading(false);
      }
    }

    loadDashboard();

    return () => {
      mounted = false;
    };
  }, []);

  const handleLinkSubmit = async (event) => {
    event.preventDefault();
    const normalizedAdmissionNumber = admissionNumber.trim().toUpperCase();
    if (!normalizedAdmissionNumber) return;

    setIsLinking(true);
    setLinkError(null);
    setLinkSuccess(null);

    try {
      await parentService.createStudentLinkRequest({
        admission_number: normalizedAdmissionNumber,
        relationship_type: relationshipType,
      });
      await loadDashboardData();
      setAdmissionNumber("");
      setLinkSuccess("Link request submitted. The student must approve it before you can view their dashboard.");
    } catch (error) {
      setLinkError(getErrorMessage(error, "Could not submit link request."));
    } finally {
      setIsLinking(false);
    }
  };

  const printReportCard = async (card) => {
    setLoadError(null);
    try {
      await reportCardService.printParentReportCard(selectedChildId, card.id);
    } catch (error) {
      setLoadError(getErrorMessage(error, "Could not open report card."));
    }
  };

  const selectedChild = children.find((item) => item.student?.id === selectedChildId);
  const childAverage = averageScore(childResults);
  const subjectHighlights = bestAndWeakestSubject(childResults);
  const selectedChildAcademicLabel = useMemo(() => {
    const latestResult = childResults[0];
    const latestCard = childReportCards[0];
    const session = latestResult?.academic_session_name || latestCard?.academic_session_name;
    const term = latestResult?.academic_term_name || latestCard?.academic_term_name;
    return [session, cleanText(term, "")].filter(Boolean).join(" - ") || "-";
  }, [childResults, childReportCards]);

  useEffect(() => {
    let mounted = true;
    async function loadChildAcademics() {
      if (!selectedChildId) {
        setChildResults([]);
        setChildReportCards([]);
        return;
      }
      try {
        const [resultResponse, reportCardResponse] = await Promise.all([
          academicService.listChildResults(selectedChildId),
          reportCardService.listChildReportCards(selectedChildId),
        ]);
        if (!mounted) return;
        setChildResults(resultResponse?.items || []);
        setChildReportCards(reportCardResponse?.items || []);
      } catch {
        if (!mounted) return;
        setChildResults([]);
        setChildReportCards([]);
      }
    }
    loadChildAcademics();
    return () => {
      mounted = false;
    };
  }, [selectedChildId]);

  if (isLoading) {
    return (
      <DashboardLayout role="parent" title={`${firstName}'s Portal`}>
        <LoadingState label="Loading parent dashboard..." />
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout
      role="parent"
      title={`${firstName}'s Portal`}
      description="Track your children's attendance, results, and school notices."
      actions={
        <Button variant="outline" className="w-full sm:w-auto">
          <MessageSquare className="h-4 w-4" />
          Message school
        </Button>
      }
    >
      {loadError && (
        <div className="rounded-2xl border border-error/30 bg-error-soft px-4 py-3 text-sm font-medium text-error">
          {loadError}
        </div>
      )}

      {!loadError && (
        <section className="stat-grid stat-grid-five">
          <StatCard
            label="Linked Students"
            value={children.length}
            description="visible profiles"
            icon={Users}
            tone={children.length > 0 ? "primary" : "warning"}
            compact
          />
          <StatCard
            label="Primary Contacts"
            value={children.filter((item) => item.link?.is_primary_contact).length}
            description="marked primary"
            icon={Link2}
            tone="success"
            compact
          />
          <StatCard
            label="Average Score"
            value={childAverage}
            description="selected child"
            icon={BarChart3}
            tone={childResults.length > 0 ? "success" : "warning"}
            compact
          />
          <StatCard
            label="Academic Context"
            value={selectedChildAcademicLabel}
            description="selected child latest term"
            icon={GraduationCap}
            tone={selectedChildAcademicLabel !== "-" ? "primary" : "warning"}
            compact
          />
          <StatCard
            label="Best Subject"
            value={subjectHighlights.best?.label || "-"}
            description={subjectHighlights.best ? `${subjectHighlights.best.value} score` : "awaiting results"}
            icon={BarChart3}
            tone={subjectHighlights.best ? "success" : "warning"}
            compact
          />
        </section>
      )}

      {!loadError && (
        <section className="dashboard-grid xl:grid-cols-2">
          <AnalyticsBarChart
            title="Subject Performance"
            description="Published scores for the selected child."
            data={subjectPerformanceChart(childResults)}
            emptyMessage="No published subject results for the selected child yet."
          />
          <AnalyticsDonutChart
            title="Grade Distribution"
            description="Grade spread for the selected child."
            data={chartFromCounts(childResults, "grade", "ungraded")}
            emptyMessage="No grade distribution available yet."
          />
          <AnalyticsDonutChart
            title="Result Status"
            description="Availability state for the selected child's results."
            data={chartFromCounts(childResults, "status", "not available")}
            emptyMessage="No result status data available yet."
          />
          <AnalyticsDonutChart
            title="Report Card Status"
            description="Report-card generation and publishing state."
            data={reportCardStatusChart(childReportCards)}
            emptyMessage="No report card status data available yet."
          />
        </section>
      )}

      <section className="dashboard-grid lg:grid-cols-[minmax(0,1fr)_min(100%,360px)]">
        <Card className="p-4 sm:p-5 md:p-6">
          <h2 className="section-title">Family Overview</h2>
          {children.length > 0 && (
            <label className="mt-4 block">
              <span className="mb-1.5 block text-xs font-semibold uppercase tracking-wide text-text-muted">
                Selected child
              </span>
              <select
                value={selectedChildId}
                onChange={(event) => setSelectedChildId(event.target.value)}
                className="min-h-11 w-full rounded-xl border border-border bg-surface px-3 text-sm font-medium text-text outline-none"
              >
                {children.map(({ student }) => (
                  <option key={student.id} value={student.id}>
                    {displayName(student)} - {student.admission_number}
                  </option>
                ))}
              </select>
            </label>
          )}
          {children.length > 0 ? (
            <div className="mt-4 grid gap-3">
              {children.map(({ student, link }) => (
                <div key={link.id} className="rounded-2xl border border-border bg-surface px-4 py-3">
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div className="min-w-0">
                      <p className="truncate text-sm font-semibold text-text">
                        {displayName(student)}
                      </p>
                      <p className="mt-1 text-xs font-medium text-text-muted">
                          {cleanText(student.admission_number)} - {cleanText(student.profile_status)}
                      </p>
                    </div>
                    <Badge variant={link.is_primary_contact ? "success" : "default"}>
                      {link.relationship_type}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState
              icon={GraduationCap}
              title="No linked students yet"
              description="Submit a student admission number to request access. The student must approve it before the link becomes active."
            />
          )}

          {selectedChild && (
            <div className="mt-5 border-t border-border pt-5">
              <h3 className="text-sm font-semibold text-text">Academic summary for {displayName(selectedChild.student)}</h3>
              <div className="mt-3 grid gap-3">
                {childResults.length === 0 ? (
                  <p className="text-sm text-text-muted">No result available yet.</p>
                ) : (
                  childResults.map((result) => (
                    <div key={result.id} className="rounded-2xl border border-border bg-surface px-4 py-3">
                      <div className="flex items-start justify-between gap-3">
                        <div>
                          <p className="font-semibold text-text">{result.subject_name || "Subject"}</p>
                          <p className="text-xs text-text-muted">
                            {cleanText(result.subject_code)} | Total {cleanText(result.total_score)}
                          </p>
                        </div>
                        <Badge variant="success">{cleanText(result.grade)}</Badge>
                      </div>
                      <div className="mt-3 grid grid-cols-2 gap-2 text-sm text-text-soft">
                        <p>Teacher: {cleanText(result.teacher_name)}</p>
                        <p>Test: {cleanText(result.test_score)}</p>
                        <p>Assessment: {cleanText(result.assessment_score)}</p>
                        <p>Exam: {cleanText(result.exam_score)}</p>
                      </div>
                      <p className="mt-2 text-sm font-medium text-text">{cleanText(result.remark, "No result available yet.")}</p>
                    </div>
                  ))
                )}
              </div>
              <h3 className="mt-5 text-sm font-semibold text-text">Report cards</h3>
              <div className="mt-3 space-y-3">
                {childReportCards.length === 0 ? (
                  <p className="text-sm text-text-muted">No report card available yet.</p>
                ) : (
                  childReportCards.map((card) => (
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
            </div>
          )}
        </Card>

        <Card className="p-4 sm:p-5 md:p-6">
          <h2 className="section-title">Link Student</h2>
          <form onSubmit={handleLinkSubmit} className="mt-4 space-y-3">
            <label className="block">
              <span className="mb-1.5 block text-xs font-semibold uppercase tracking-wide text-text-muted">
                Admission number
              </span>
              <input
                value={admissionNumber}
                onChange={(event) => {
                  setAdmissionNumber(event.target.value);
                  setLinkError(null);
                  setLinkSuccess(null);
                }}
                placeholder="NHS-2026-12345"
                className="min-h-11 w-full rounded-xl border border-border bg-surface px-3 text-sm font-medium text-text outline-none transition placeholder:text-text-faint focus:border-primary focus:ring-4 focus:ring-primary/10"
              />
            </label>
            <label className="block">
              <span className="mb-1.5 block text-xs font-semibold uppercase tracking-wide text-text-muted">
                Relationship
              </span>
              <select
                value={relationshipType}
                onChange={(event) => setRelationshipType(event.target.value)}
                className="min-h-11 w-full rounded-xl border border-border bg-surface px-3 text-sm font-medium text-text outline-none transition focus:border-primary focus:ring-4 focus:ring-primary/10"
              >
                <option value="father">Father</option>
                <option value="mother">Mother</option>
                <option value="guardian">Guardian</option>
                <option value="sponsor">Sponsor</option>
                <option value="other">Other</option>
              </select>
            </label>
            {linkError && <p className="text-sm font-medium text-error">{linkError}</p>}
            {linkSuccess && <p className="text-sm font-medium text-success">{linkSuccess}</p>}
            <Button type="submit" className="w-full" disabled={isLinking || !admissionNumber.trim()}>
              <Link2 className="h-4 w-4" />
              {isLinking ? "Submitting..." : "Request student link"}
            </Button>
          </form>

          <div className="my-5 border-t border-border" />

          <h2 className="section-title">Request Status</h2>
          <div className="mt-4 space-y-3">
            {requests.length === 0 ? (
              <p className="text-sm text-text-muted">
                No parent-student link requests yet.
              </p>
            ) : (
              requests.map((request) => (
                <div key={request.id} className="rounded-2xl border border-border bg-surface px-4 py-3">
                  <div className="flex items-start justify-between gap-3">
                    <div className="min-w-0">
                      <p className="truncate text-sm font-semibold text-text">
                        {displayName(request.student)}
                      </p>
                      <p className="mt-1 text-xs text-text-muted">
                        {request.admission_number_snapshot || request.student?.admission_number || "No admission number"}
                      </p>
                    </div>
                    <Badge variant={request.status === "approved" ? "success" : request.status === "rejected" ? "error" : "warning"}>
                      {request.status}
                    </Badge>
                  </div>
                </div>
              ))
            )}
          </div>

          <div className="my-5 border-t border-border" />

          <h2 className="section-title">Parent Modules</h2>
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

export default ParentDashboardPage;
