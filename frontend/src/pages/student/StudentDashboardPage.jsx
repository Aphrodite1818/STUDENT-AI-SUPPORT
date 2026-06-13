import { Link } from "react-router-dom";
import { BarChart3, CalendarDays, ClipboardList, FileText } from "lucide-react";
import DashboardLayout from "../../components/layout/DashboardLayout";
import Card from "../../components/ui/Card";
import EmptyState from "../../components/shared/EmptyState";
import { authSession } from "../../services/api";

const links = [
  { label: "Timetable", to: "/student/timetable", icon: CalendarDays },
  { label: "Assignments", to: "/student/assignments", icon: ClipboardList },
  { label: "Results", to: "/student/results", icon: BarChart3 },
  { label: "Notices", to: "/student/notices", icon: FileText },
];

function StudentDashboardPage() {
  const user = authSession.getUser();
  const firstName = user?.firstname || "Student";

  return (
    <DashboardLayout
      role="student"
      title={`${firstName}'s Portal`}
      description="Your student dashboard will show live academic data when student APIs are connected."
    >
      <section className="grid gap-5 lg:grid-cols-[minmax(0,1fr)_360px]">
        <Card className="p-5 sm:p-6">
          <h2 className="text-xl font-semibold">Learning Overview</h2>
          <EmptyState
            title="No student metrics available"
            description="Attendance, scores, assignments, and timetable data are hidden until real backend endpoints are available."
          />
        </Card>

        <Card className="p-5 sm:p-6">
          <h2 className="text-xl font-semibold">Student Modules</h2>
          <div className="mt-5 grid gap-3">
            {links.map((item) => {
              const Icon = item.icon;
              return (
                <Link
                  key={item.to}
                  to={item.to}
                  className="flex items-center gap-3 rounded-2xl border border-border bg-surface px-4 py-3 font-semibold text-text-soft transition hover:border-primary/30 hover:bg-primary-subtle hover:text-primary"
                >
                  <Icon className="h-5 w-5" />
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
