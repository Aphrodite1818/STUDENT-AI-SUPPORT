import { useEffect, useState } from "react";
import { BookOpen, CalendarDays, CheckCircle2, ClipboardList } from "lucide-react";
import DashboardLayout from "../../components/layout/DashboardLayout";
import Card from "../../components/ui/Card";
import Badge from "../../components/ui/Badge";
import StatCard from "../../components/shared/StatCard";
import LoadingState from "../../components/shared/LoadingState";
import { dashboardService } from "../../services/dashboard.service";

function StudentDashboardPage() {
  const [overview, setOverview] = useState(null);

  useEffect(() => {
    let mounted = true;
    dashboardService.getStudentOverview().then((data) => {
      if (mounted) setOverview(data);
    });
    return () => {
      mounted = false;
    };
  }, []);

  if (!overview) {
    return (
      <DashboardLayout role="student" title="Student Dashboard">
        <LoadingState label="Loading learning portal..." />
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout
      role="student"
      title="Learning Portal"
      description="A clean overview of your timetable, assignments, notices, and academic performance."
    >
      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {overview.stats.map((stat, index) => {
          const icons = [BookOpen, CheckCircle2, ClipboardList, CalendarDays];
          const Icon = icons[index];
          return <StatCard key={stat.label} {...stat} icon={Icon} />;
        })}
      </section>

      <section className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_380px]">
        <Card className="p-5">
          <h2 className="text-lg font-semibold">Today's Classes</h2>
          <div className="mt-5 space-y-3">
            {[
              ["09:30", "Mathematics", "Room 204", "Active"],
              ["10:20", "Science", "Room 204", "Next"],
              ["12:45", "Social Studies", "Room 204", "Later"],
            ].map(([time, subject, room, status]) => (
              <div key={subject} className="flex flex-col gap-3 rounded-2xl border border-border bg-surface p-4 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <p className="text-sm font-bold text-primary">{time}</p>
                  <p className="mt-1 font-semibold">{subject}</p>
                  <p className="text-sm text-text-muted">{room}</p>
                </div>
                <Badge variant={status === "Active" ? "success" : "default"}>{status}</Badge>
              </div>
            ))}
          </div>
        </Card>

        <div className="space-y-6">
          <Card className="p-5">
            <h2 className="text-lg font-semibold">Assignments</h2>
            <div className="mt-4 space-y-3">
              {["Mathematics exercises", "Science lab note", "English essay"].map((item) => (
                <div key={item} className="rounded-2xl bg-surface-muted/50 p-4">
                  <p className="font-semibold">{item}</p>
                  <p className="mt-1 text-sm text-text-muted">Due this week</p>
                </div>
              ))}
            </div>
          </Card>

          <Card className="p-5">
            <h2 className="text-lg font-semibold">Recent Notices</h2>
            <p className="mt-3 text-sm leading-6 text-text-muted">
              Unit Test 1 schedule has been published. Annual Sports Day practice begins next week.
            </p>
          </Card>
        </div>
      </section>
    </DashboardLayout>
  );
}

export default StudentDashboardPage;
