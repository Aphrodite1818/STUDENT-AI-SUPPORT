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
      description="Live teaching tools are available through the module links below."
    >
      <section className="grid gap-5 lg:grid-cols-[minmax(0,1fr)_380px]">
        <Card className="p-5 sm:p-6">
          <h2 className="text-xl font-semibold">Teaching Overview</h2>
          <EmptyState
            title="No teacher dashboard metrics yet"
            description="Class load, attendance, assignment, and timetable summaries will appear after backend summary endpoints are available."
          />
        </Card>

        <Card className="p-5 sm:p-6">
          <h2 className="text-xl font-semibold">Quick Actions</h2>
          <div className="mt-5 grid gap-3">
            {shortcuts.map((shortcut) => {
              const Icon = shortcut.icon;
              return (
                <Link
                  key={shortcut.to}
                  to={shortcut.to}
                  className="flex items-center gap-3 rounded-2xl border border-border bg-surface px-4 py-3 font-semibold text-text-soft transition hover:border-primary/30 hover:bg-primary-subtle hover:text-primary"
                >
                  <Icon className="h-5 w-5" />
                  {shortcut.label}
                </Link>
              );
            })}
          </div>
          <Link to="/teacher/attendance" className="mt-5 block">
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
