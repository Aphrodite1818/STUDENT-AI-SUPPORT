import { useEffect, useState } from "react";
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
import { displayName } from "../../utils/user";

const links = [
  { label: "Attendance", to: "/parent/attendance", icon: Bell },
  { label: "Results", to: "/parent/results", icon: BarChart3 },
  { label: "Notices", to: "/parent/notices", icon: MessageSquare },
  { label: "Fees", to: "/parent/fees", icon: CreditCard },
];

function ParentDashboardPage() {
  const [children, setChildren] = useState([]);
  const [requests, setRequests] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isLinking, setIsLinking] = useState(false);
  const [admissionNumber, setAdmissionNumber] = useState("");
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

  const pendingRequests = requests.filter((item) => item.status === "pending");
  const approvedRequests = requests.filter((item) => item.status === "approved").length;
  const rejectedRequests = requests.filter((item) => item.status === "rejected").length;
  const completeProfiles = children.filter((item) => item?.student?.profile_status === "complete").length;
  const incompleteProfiles = Math.max(children.length - completeProfiles, 0);
  const familySnapshotData = [
    { label: "linked_students", value: children.length },
    { label: "pending_requests", value: pendingRequests.length },
    { label: "primary_contacts", value: children.filter((item) => item.link?.is_primary_contact).length },
  ];
  const requestStatusData = [
    { label: "approved", value: approvedRequests },
    { label: "pending", value: pendingRequests.length },
    { label: "rejected", value: rejectedRequests },
    { label: "profiles_complete", value: completeProfiles },
    { label: "profiles_incomplete", value: incompleteProfiles },
  ];

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
        <section className="stat-grid">
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
            label="Pending Requests"
            value={pendingRequests.length}
            description="awaiting student approval"
            icon={GraduationCap}
            tone={pendingRequests.length > 0 ? "warning" : "primary"}
            compact
          />
        </section>
      )}

      {!loadError && (
        <section className="dashboard-grid xl:grid-cols-2">
          <AnalyticsBarChart
            title="Family Snapshot"
            description="Live counts for linked students, pending approvals, and primary-contact coverage."
            data={familySnapshotData}
          />
          <AnalyticsDonutChart
            title="Requests And Profile Status"
            description="Combines link-request outcomes with linked-student profile completion."
            data={requestStatusData}
          />
        </section>
      )}

      <section className="dashboard-grid lg:grid-cols-[minmax(0,1fr)_min(100%,360px)]">
        <Card className="p-4 sm:p-5 md:p-6">
          <h2 className="section-title">Family Overview</h2>
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
                        {student.admission_number || "No admission number"} - {student.profile_status}
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
