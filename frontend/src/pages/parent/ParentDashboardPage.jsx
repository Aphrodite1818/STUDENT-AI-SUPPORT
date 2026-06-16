import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { BarChart3, Bell, CreditCard, GraduationCap, Link2, MessageSquare, Users } from "lucide-react";
import DashboardLayout from "../../components/layout/DashboardLayout";
import Card from "../../components/ui/Card";
import Button from "../../components/ui/Button";
import Badge from "../../components/ui/Badge";
import EmptyState from "../../components/shared/EmptyState";
import LoadingState from "../../components/shared/LoadingState";
import StatCard from "../../components/shared/StatCard";
import { authSession, getErrorMessage } from "../../services/api";
import { parentService } from "../../services/parentService";
import { studentService } from "../../services/studentService";

const links = [
  { label: "Attendance", to: "/parent/attendance", icon: Bell },
  { label: "Results", to: "/parent/results", icon: BarChart3 },
  { label: "Notices", to: "/parent/notices", icon: MessageSquare },
  { label: "Fees", to: "/parent/fees", icon: CreditCard },
];

function ParentDashboardPage() {
  const [children, setChildren] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isLinking, setIsLinking] = useState(false);
  const [linkCode, setLinkCode] = useState("");
  const [loadError, setLoadError] = useState(null);
  const [linkError, setLinkError] = useState(null);
  const [linkSuccess, setLinkSuccess] = useState(null);
  const user = authSession.getUser();
  const firstName = user?.firstname || "Parent";

  const loadChildren = async () => {
    const response = await parentService.getMyStudents();
    setChildren(response?.items || []);
  };

  useEffect(() => {
    let mounted = true;

    async function loadDashboard() {
      setIsLoading(true);
      setLoadError(null);

      try {
        const response = await parentService.getMyStudents();
        if (mounted) setChildren(response?.items || []);
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
    const normalizedCode = linkCode.trim().toUpperCase();
    if (!normalizedCode) return;

    setIsLinking(true);
    setLinkError(null);
    setLinkSuccess(null);

    try {
      await studentService.redeemLinkCode({ code: normalizedCode });
      await loadChildren();
      setLinkCode("");
      setLinkSuccess("Student linked successfully.");
    } catch (error) {
      setLinkError(getErrorMessage(error, "Could not link student."));
    } finally {
      setIsLinking(false);
    }
  };

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
                        {[student.firstname, student.lastname].filter(Boolean).join(" ") || "Student"}
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
              description="Enter a student link code from the school to connect your parent account to a child profile."
            />
          )}
        </Card>

        <Card className="p-4 sm:p-5 md:p-6">
          <h2 className="section-title">Link Student</h2>
          <form onSubmit={handleLinkSubmit} className="mt-4 space-y-3">
            <label className="block">
              <span className="mb-1.5 block text-xs font-semibold uppercase tracking-wide text-text-muted">
                Student link code
              </span>
              <input
                value={linkCode}
                onChange={(event) => {
                  setLinkCode(event.target.value);
                  setLinkError(null);
                  setLinkSuccess(null);
                }}
                placeholder="STU..."
                className="min-h-11 w-full rounded-xl border border-border bg-surface px-3 text-sm font-medium text-text outline-none transition placeholder:text-text-faint focus:border-primary focus:ring-4 focus:ring-primary/10"
              />
            </label>
            {linkError && <p className="text-sm font-medium text-error">{linkError}</p>}
            {linkSuccess && <p className="text-sm font-medium text-success">{linkSuccess}</p>}
            <Button type="submit" className="w-full" disabled={isLinking || !linkCode.trim()}>
              <Link2 className="h-4 w-4" />
              {isLinking ? "Linking..." : "Link student"}
            </Button>
          </form>

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
