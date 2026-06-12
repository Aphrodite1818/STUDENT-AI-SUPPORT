import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { BookOpen, CalendarDays, CheckSquare, ClipboardList, GraduationCap, Plus, Users } from "lucide-react";
import DashboardLayout from "../../components/layout/DashboardLayout";
import Card from "../../components/ui/Card";
import Button from "../../components/ui/Button";
import Badge from "../../components/ui/Badge";
import StatCard from "../../components/shared/StatCard";
import LoadingState from "../../components/shared/LoadingState";
import { dashboardService } from "../../services/dashboard.service";

const shortcuts = [
  { label: "Mark attendance", to: "/teacher/attendance", icon: CheckSquare },
  { label: "Add result", to: "/teacher/results", icon: ClipboardList },
  { label: "View classes", to: "/teacher/classes", icon: Users },
  { label: "Schedule exam", to: "/teacher/exams", icon: CalendarDays },
];

function TeacherDashboardPage() {
  const [overview, setOverview] = useState(null);

  useEffect(() => {
    let mounted = true;
    dashboardService.getTeacherOverview().then((data) => {
      if (mounted) setOverview(data);
    });
    return () => {
      mounted = false;
    };
  }, []);

  if (!overview) {
    return (
      <DashboardLayout role="teacher" title="Teacher Dashboard">
        <LoadingState label="Loading teacher workspace..." />
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout
      role="teacher"
      title="Teacher Workspace"
      description="Your assigned classes, today's timetable, attendance shortcuts, and recent academic signals."
      actions={
        <Link to="/teacher/attendance">
          <Button>
            <Plus className="h-4 w-4" />
            Mark attendance
          </Button>
        </Link>
      }
    >
      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {overview.stats.map((stat, index) => {
          const icons = [BookOpen, GraduationCap, ClipboardList, CheckSquare];
          const Icon = icons[index];
          return <StatCard key={stat.label} {...stat} icon={Icon} />;
        })}
      </section>

      <section className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_380px]">
        <div className="space-y-6">
          <Card className="p-5">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <h2 className="text-lg font-semibold">Today's Teaching Plan</h2>
                <p className="text-sm text-text-muted">A practical schedule view for your day.</p>
              </div>
              <Badge variant="primary">4 periods</Badge>
            </div>
            <div className="mt-5 grid gap-3 md:grid-cols-2">
              {[
                ["09:30", "Grade 8 - A", "Mathematics", "Room 204"],
                ["10:20", "Grade 7 - B", "English", "Room 112"],
                ["12:45", "Grade 9 - A", "Science", "Lab 2"],
                ["13:35", "Grade 8 - A", "Computer Science", "Lab 1"],
              ].map(([time, className, subject, room]) => (
                <div key={`${time}-${subject}`} className="rounded-2xl border border-border bg-surface-muted/40 p-4">
                  <p className="text-xs font-bold text-primary">{time}</p>
                  <p className="mt-2 font-semibold">{className}</p>
                  <p className="text-sm text-text-soft">{subject}</p>
                  <p className="mt-2 text-xs text-text-muted">{room}</p>
                </div>
              ))}
            </div>
          </Card>

          <Card className="p-5">
            <h2 className="text-lg font-semibold">Assigned Subjects</h2>
            <div className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {["Mathematics", "Computer Science", "Science", "English", "Physics", "Chemistry"].map((subject) => (
                <div key={subject} className="rounded-2xl border border-border bg-surface p-4">
                  <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary-soft text-primary">
                    <BookOpen className="h-5 w-5" />
                  </span>
                  <p className="mt-3 font-semibold">{subject}</p>
                  <p className="mt-1 text-sm text-text-muted">Active this term</p>
                </div>
              ))}
            </div>
          </Card>
        </div>

        <div className="space-y-6">
          <Card className="p-5">
            <h2 className="text-lg font-semibold">Quick Actions</h2>
            <div className="mt-4 grid gap-3">
              {shortcuts.map((shortcut) => {
                const Icon = shortcut.icon;
                return (
                  <Link key={shortcut.to} to={shortcut.to} className="flex items-center gap-3 rounded-2xl border border-border bg-surface px-4 py-3 font-semibold text-text-soft transition hover:border-primary/30 hover:bg-primary-subtle hover:text-primary">
                    <Icon className="h-5 w-5" />
                    {shortcut.label}
                  </Link>
                );
              })}
            </div>
          </Card>

          <Card className="p-5">
            <h2 className="text-lg font-semibold">Recent Notices</h2>
            <div className="mt-4 space-y-4">
              {["Unit test schedule published", "Staff meeting at 3 PM", "Grade 8 intervention list ready"].map((notice) => (
                <div key={notice} className="rounded-2xl bg-surface-muted/50 p-4">
                  <p className="font-semibold">{notice}</p>
                  <p className="mt-1 text-sm text-text-muted">Shared by administration</p>
                </div>
              ))}
            </div>
          </Card>
        </div>
      </section>
    </DashboardLayout>
  );
}

export default TeacherDashboardPage;
