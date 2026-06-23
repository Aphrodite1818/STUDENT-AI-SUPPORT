import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { BarChart3, CalendarDays, ClipboardList, FileText, Link2, UserRound } from "lucide-react";
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
import { studentService } from "../../services/studentService";
import { displayName } from "../../utils/user";

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
  const [isLoading, setIsLoading] = useState(true);
  const [loadError, setLoadError] = useState(null);
  const [requestActionId, setRequestActionId] = useState(null);
  const user = authSession.getUser();
  const firstName = user?.first_name || user?.firstname || "Student";
  const requiredProfileFields = ["first_name", "last_name", "date_of_birth", "gender"];

  const loadDashboardData = async () => {
    const [studentProfile, linksResponse, requestsResponse] = await Promise.all([
      studentService.getMyStudent(),
      studentService.getMyParentLinks(),
      studentService.getMyParentLinkRequests(),
    ]);

    setStudent(studentProfile);
    setParentLinks(linksResponse?.items || []);
    setParentLinkRequests(requestsResponse?.items || []);
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

  if (isLoading) {
    return (
      <DashboardLayout role="student" title={`${firstName}'s Portal`}>
        <LoadingState label="Loading student dashboard..." />
      </DashboardLayout>
    );
  }

  const completedProfileFields = requiredProfileFields.filter((field) => Boolean(student?.[field])).length;
  const missingProfileFields = Math.max(requiredProfileFields.length - completedProfileFields, 0);
  const requestBreakdownData = [
    { label: "approved_links", value: parentLinks.length },
    { label: "pending_requests", value: parentLinkRequests.length },
    { label: "missing_profile_fields", value: missingProfileFields },
  ];
  const profileProgressData = [
    { label: "completed_fields", value: completedProfileFields },
    { label: "remaining_fields", value: missingProfileFields },
  ];

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
            label="Pending Requests"
            value={parentLinkRequests.length}
            description="awaiting your decision"
            icon={Link2}
            tone={parentLinkRequests.length > 0 ? "warning" : "success"}
            compact
          />
        </section>
      )}

      {!loadError && student && (
        <section className="dashboard-grid xl:grid-cols-2">
          <AnalyticsBarChart
            title="Student Snapshot"
            description="Profile readiness and parent-link progress based on your current account data."
            data={requestBreakdownData}
          />
          <AnalyticsDonutChart
            title="Profile Completion Progress"
            description="Required profile fields completed versus still missing."
            data={profileProgressData}
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
