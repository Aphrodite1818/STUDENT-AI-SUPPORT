import { Link } from "react-router-dom";
import { BookOpen, CheckSquare, ClipboardList, Users } from "lucide-react";
import DashboardLayout from "../../components/layout/DashboardLayout";
import Card from "../../components/ui/Card";
import Button from "../../components/ui/Button";
import EmptyState from "../../components/shared/EmptyState";
import { authSession } from "../../services/api";

const shortcuts = [
  { label: "My classes", to: "/teacher/classes", icon: Users },
  { label: "Students", to: "/teacher/students", icon: Users },
  { label: "Subjects", to: "/teacher/subjects", icon: BookOpen },
  { label: "Attendance", to: "/teacher/attendance", icon: CheckSquare },
  { label: "Results", to: "/teacher/results", icon: ClipboardList },
];

function TeacherDashboardPage() {
  const user = authSession.getUser();
  const firstName = user?.firstname || "Teacher";

  return (
    <DashboardLayout
      role="teacher"
      title={`${firstName}'s Workspace`}
      description="Access your classes, attendance, and teaching tools."
    >
      <section className="dashboard-grid lg:grid-cols-[minmax(0,1fr)_min(100%,380px)]">
        <Card className="p-4 sm:p-5 md:p-6">
          <h2 className="section-title">Teaching Overview</h2>
          <EmptyState
            title="No teacher dashboard metrics yet"
            description="Class load, attendance, and timetable summaries will appear when backend endpoints are available."
          />
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
