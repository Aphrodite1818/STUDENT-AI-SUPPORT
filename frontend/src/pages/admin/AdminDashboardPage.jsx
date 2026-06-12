import { useEffect, useState } from "react";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import {
  BarChart3,
  BookOpen,
  Bot,
  CalendarDays,
  CheckCircle2,
  ClipboardCheck,
  GraduationCap,
  Megaphone,
  Plus,
  School,
  Sparkles,
  TriangleAlert,
  Users,
} from "lucide-react";
import DashboardLayout from "../../components/layout/DashboardLayout";
import Button from "../../components/ui/Button";
import Card from "../../components/ui/Card";
import Badge from "../../components/ui/Badge";
import StatCard from "../../components/shared/StatCard";
import LoadingState from "../../components/shared/LoadingState";
import { dashboardService } from "../../services/dashboard.service";
import { cn } from "../../utils/cn";

const statIcons = [GraduationCap, Users, School, ClipboardCheck];
const toneIcons = {
  success: CheckCircle2,
  warning: TriangleAlert,
  primary: BarChart3,
  error: Megaphone,
};

const subjectTone = {
  Mathematics: "primary",
  Science: "success",
  English: "accent",
  Physics: "primary",
  Chemistry: "accent",
  "Computer Science": "success",
};

function TimetableCard({ items = [] }) {
  return (
    <Card className="p-5 sm:p-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-3">
          <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary-soft text-primary">
            <CalendarDays className="h-5 w-5" />
          </span>
          <div>
            <h2 className="text-lg font-semibold">Today's Timetable</h2>
            <p className="text-sm text-text-muted">Live operational schedule for Grade 8 - A.</p>
          </div>
        </div>
        <Button variant="ghost" size="sm">View full timetable</Button>
      </div>

      <div className="mt-6 pb-1">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-3 xl:grid-cols-6">
          {items.map((item) => (
            <div
              key={`${item.time}-${item.subject}`}
              className={cn(
                "flex min-h-[164px] flex-col items-start rounded-[16px] border border-border/40 p-5 text-left transition hover:shadow-sm",
                item.active
                  ? "bg-primary-subtle border-primary/20"
                  : "bg-surface hover:border-border/80"
              )}
            >
              <p className="text-[11px] font-bold uppercase tracking-wider text-primary">{item.time}</p>
              <p className="mt-4 text-sm font-semibold text-text">{item.className}</p>
              <p className="mt-1 flex-1 text-sm text-text-soft">{item.subject}</p>
              <div className="mt-4 flex w-full items-center justify-between border-t border-border/40 pt-4">
                <span className="text-xs text-text-muted">{item.room}</span>
                {item.students && (
                  <span className="text-xs font-semibold text-text-soft">{item.students} students</span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </Card>
  );
}

function AttendanceActions({ classes = [] }) {
  return (
    <Card className="p-5 sm:p-6">
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-accent-soft text-accent">
            <ClipboardCheck className="h-5 w-5" />
          </span>
          <div>
            <h2 className="text-lg font-semibold">Mark Attendance</h2>
            <p className="text-sm text-text-muted">Quick shortcuts for today.</p>
          </div>
        </div>
      </div>
      <div className="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {classes.map((item) => (
          <button
            key={item.className}
            type="button"
            className={cn(
              "flex flex-col items-start rounded-[16px] border p-5 text-left transition hover:-translate-y-0.5",
              item.active
                ? "border-primary bg-primary text-white shadow-sm shadow-primary/20"
                : "border-border/40 bg-surface hover:border-border/80 hover:shadow-sm"
            )}
          >
            <div className="flex w-full items-center justify-between">
              <span className={cn("flex h-10 w-10 items-center justify-center rounded-[12px]", item.active ? "bg-white/20 text-white" : "bg-primary-soft text-primary")}>
                <Users className="h-5 w-5" />
              </span>
              <p className={cn("text-xs font-semibold", item.active ? "text-white/90" : "text-text-muted")}>
                {item.students} students
              </p>
            </div>
            <p className="mt-4 text-base font-semibold">{item.className}</p>
            <p className={cn("mt-1 text-sm", item.active ? "text-white/80" : "text-text-soft")}>{item.subject}</p>
          </button>
        ))}
        <button
          type="button"
          className="flex min-h-[140px] flex-col items-center justify-center rounded-[16px] border border-dashed border-border/60 bg-surface/50 text-sm font-semibold text-text-muted transition hover:border-primary/40 hover:bg-primary-subtle hover:text-primary"
        >
          <Plus className="mb-2 h-5 w-5" />
          Other class
        </button>
      </div>
    </Card>
  );
}

function PerformanceCard({ data = [] }) {
  const chartData = [{ name: "Average", value: data[0]?.value || 78 }];

  return (
    <Card className="p-5 sm:p-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-lg font-semibold">Student Performance Overview</h2>
          <p className="text-sm text-text-muted">This term at a glance.</p>
        </div>
        <Button variant="outline" size="sm">This Term</Button>
      </div>
      <div className="mt-6 grid gap-6 xl:grid-cols-[220px_minmax(0,1fr)] xl:items-center">
        <div className="relative mx-auto h-52 w-full max-w-[240px] xl:h-56">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={[{ name: "Remaining", value: 100 }]}
                dataKey="value"
                innerRadius={58}
                outerRadius={76}
                startAngle={90}
                endAngle={-270}
              >
                <Cell fill="#E2E8F0" />
              </Pie>
              <Pie
                data={chartData}
                dataKey="value"
                innerRadius={58}
                outerRadius={76}
                startAngle={90}
                endAngle={-270}
                cornerRadius={10}
              >
                <Cell fill="#10B981" />
              </Pie>
            </PieChart>
          </ResponsiveContainer>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <p className="text-3xl font-semibold">{chartData[0].value}%</p>
            <p className="text-xs text-text-muted">Average Score</p>
          </div>
        </div>
        <div className="grid gap-3 sm:grid-cols-2">
          {[
            ["Top Performers", "18%", "+4% vs last term", "success"],
            ["At Risk Students", "7", "-2 vs last term", "error"],
            ["Average Attendance", "92%", "+3% vs last term", "success"],
            ["Assessments Done", "24", "This term", "primary"],
          ].map(([label, value, detail, tone]) => (
            <div key={label} className="min-h-[112px] rounded-2xl border border-border bg-surface-muted/40 p-4">
              <p className="text-xs font-semibold text-text-muted">{label}</p>
              <p className="mt-2 text-2xl font-semibold">{value}</p>
              <p className={cn("mt-1 text-xs font-semibold", tone === "error" ? "text-error" : tone === "success" ? "text-success" : "text-primary")}>
                {detail}
              </p>
            </div>
          ))}
        </div>
      </div>
      <Button variant="outline" size="sm" className="mt-5 w-full sm:w-auto">View detailed analytics</Button>
    </Card>
  );
}

function AssignedClasses({ classes = [] }) {
  return (
    <Card className="p-5 sm:p-6">
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary-soft text-primary">
            <BookOpen className="h-5 w-5" />
          </span>
          <h2 className="text-lg font-semibold">Assigned Classes & Subjects</h2>
        </div>
        <Button variant="ghost" size="sm">View all</Button>
      </div>
      <div className="mt-6 space-y-4">
        {classes.map((item) => (
          <button key={item.className} type="button" className="w-full rounded-2xl border border-border bg-surface p-4 text-left transition hover:border-primary/30 hover:bg-primary-subtle">
            <div className="flex items-start gap-3">
              <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-primary-soft text-primary">
                <Users className="h-5 w-5" />
              </span>
              <div className="min-w-0 flex-1">
                <div className="flex items-center justify-between gap-3">
                  <p className="font-semibold">{item.className}</p>
                  <span className="text-xs text-text-muted">{item.students} students</span>
                </div>
                <p className="text-sm text-text-muted">{item.role}</p>
                <div className="mt-2 flex flex-wrap gap-2">
                  {item.subjects.map((subject) => (
                    <Badge key={subject} variant={subjectTone[subject] || "default"}>
                      {subject}
                    </Badge>
                  ))}
                </div>
              </div>
            </div>
          </button>
        ))}
      </div>
    </Card>
  );
}

function ListCard({ title, items = [], action = "View all", icon: Icon = Megaphone }) {
  return (
    <Card className="p-5 sm:p-6">
      <div className="flex items-center justify-between gap-3">
        <h2 className="text-lg font-semibold">{title}</h2>
        <Button variant="ghost" size="sm">{action}</Button>
      </div>
      <div className="mt-5 divide-y divide-border">
        {items.map((item) => {
          const ToneIcon = toneIcons[item.tone] || Icon;
          return (
            <div key={item.title} className="flex gap-4 py-4">
              <span className={cn(
                "flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl",
                item.tone === "success" && "bg-success-soft text-success",
                item.tone === "warning" && "bg-warning-soft text-warning",
                item.tone === "error" && "bg-error-soft text-error",
                item.tone === "primary" && "bg-primary-soft text-primary"
              )}>
                <ToneIcon className="h-5 w-5" />
              </span>
              <div className="min-w-0 flex-1">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    {item.category && <Badge variant={item.tone}>{item.category}</Badge>}
                    <p className="mt-2 font-semibold">{item.title}</p>
                  </div>
                  {item.date && <span className="text-xs text-text-muted">{item.date}</span>}
                </div>
                <p className="mt-1 text-sm leading-6 text-text-muted">{item.detail}</p>
              </div>
            </div>
          );
        })}
      </div>
    </Card>
  );
}

function AttendanceSnapshot({ weeklyAttendance = [] }) {
  const totals = [
    { name: "Present", value: 1184, color: "#10B981" },
    { name: "Absent", value: 76, color: "#E11D48" },
    { name: "Late", value: 24, color: "#F59E0B" },
  ];

  return (
    <Card className="p-5 sm:p-6">
      <div className="flex items-center justify-between gap-3">
        <h2 className="text-lg font-semibold">Attendance Snapshot</h2>
        <Button variant="outline" size="sm">This Week</Button>
      </div>
      <div className="mt-6 grid gap-6 md:grid-cols-[190px_minmax(0,1fr)] xl:grid-cols-1 2xl:grid-cols-[190px_minmax(0,1fr)]">
        <div className="relative mx-auto h-52 w-full max-w-[230px]">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={totals} dataKey="value" innerRadius={54} outerRadius={76} paddingAngle={3}>
                {totals.map((entry) => (
                  <Cell key={entry.name} fill={entry.color} />
                ))}
              </Pie>
            </PieChart>
          </ResponsiveContainer>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <p className="text-3xl font-semibold">92%</p>
            <p className="text-xs text-text-muted">Overall</p>
          </div>
        </div>
        <div className="space-y-3 self-center">
          {totals.map((item) => (
            <div key={item.name} className="flex items-center justify-between gap-4 text-sm">
              <span className="flex items-center gap-2 text-text-soft">
                <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: item.color }} />
                {item.name}
              </span>
              <span className="font-semibold">{item.value.toLocaleString()}</span>
            </div>
          ))}
        </div>
      </div>
      <div className="mt-6 h-48 rounded-2xl border border-border/50 bg-surface-muted/30 p-3">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={weeklyAttendance}>
            <CartesianGrid vertical={false} stroke="#E2E8F0" />
            <XAxis dataKey="day" tickLine={false} axisLine={false} />
            <YAxis hide />
            <Tooltip />
            <Bar dataKey="present" fill="#2563EB" radius={[8, 8, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
}

function AiActivity({ items = [] }) {
  return (
    <Card className="p-5">
      <div className="flex items-center gap-3">
        <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-accent-soft text-accent">
          <Bot className="h-5 w-5" />
        </span>
        <div>
          <h2 className="text-lg font-semibold">Learnly AI Activity</h2>
          <p className="text-sm text-text-muted">Automations and summaries from the last 24 hours.</p>
        </div>
      </div>
      <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {items.map((item) => (
          <div key={item.title} className="rounded-2xl border border-border bg-surface-muted/40 p-4">
            <p className="text-sm font-semibold text-primary">{item.title}</p>
            <p className="mt-1 text-sm text-text-soft">{item.detail}</p>
            <p className="mt-3 text-xs text-text-muted">{item.time}</p>
          </div>
        ))}
      </div>
    </Card>
  );
}

function AdminDashboardPage() {
  const [overview, setOverview] = useState(null);

  useEffect(() => {
    let mounted = true;
    dashboardService.getAdminOverview().then((data) => {
      if (mounted) setOverview(data);
    });
    return () => {
      mounted = false;
    };
  }, []);

  if (!overview) {
    return (
      <DashboardLayout role="admin" title="Dashboard">
        <LoadingState label="Loading dashboard..." />
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout
      role="admin"
      title="Good morning, Anita"
      description="Here's what's happening at Greenfield International School today."
      actions={
        <>
          <Button variant="outline">
            <Sparkles className="h-4 w-4" />
            AI Assistant
          </Button>
          <Button>
            <Plus className="h-4 w-4" />
            Quick action
          </Button>
        </>
      }
    >
      <section className="grid gap-5 sm:grid-cols-2 xl:grid-cols-4">
        {overview.stats.map((stat, index) => (
          <StatCard
            key={stat.label}
            {...stat}
            icon={statIcons[index]}
            trend={stat.change?.startsWith("-") ? "down" : "up"}
          />
        ))}
      </section>

      <section className="grid gap-8 xl:grid-cols-[minmax(0,1fr)_420px]">
        <div className="space-y-8">
          <TimetableCard items={overview.timetable} />
          <AttendanceActions classes={overview.attendanceClasses} />
          <div className="grid gap-8 2xl:grid-cols-[minmax(0,1.05fr)_minmax(340px,0.95fr)]">
            <PerformanceCard data={overview.performance} />
            <AssignedClasses classes={overview.assignedClasses} />
          </div>
          <AiActivity items={overview.aiActivity} />
        </div>

        <div className="space-y-8">
          <ListCard title="Recent Notices" items={overview.notices} />
          <ListCard title="AI Insights" items={overview.insights} icon={Sparkles} />
          <AttendanceSnapshot weeklyAttendance={overview.weeklyAttendance} />
          <Card className="p-5 sm:p-6">
            <h2 className="text-lg font-semibold">Enrollment Trends</h2>
            <p className="text-sm text-text-muted">New admissions across recent terms.</p>
            <div className="mt-6 h-56 rounded-2xl border border-border/50 bg-surface-muted/30 p-3">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart
                  data={[
                    { month: "Jan", students: 980 },
                    { month: "Feb", students: 1040 },
                    { month: "Mar", students: 1110 },
                    { month: "Apr", students: 1160 },
                    { month: "May", students: 1248 },
                  ]}
                  margin={{ top: 10, right: 0, left: 0, bottom: 0 }}
                >
                  <defs>
                    <linearGradient id="colorStudents" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#2563EB" stopOpacity={0.2} />
                      <stop offset="95%" stopColor="#2563EB" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid vertical={false} stroke="#E2E8F0" strokeDasharray="4 4" />
                  <XAxis dataKey="month" tickLine={false} axisLine={false} tick={{ fontSize: 12, fill: '#64748B' }} dy={10} />
                  <YAxis hide />
                  <Tooltip cursor={{ stroke: '#94A3B8', strokeWidth: 1, strokeDasharray: '4 4' }} contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 8px 30px rgba(15, 23, 42, 0.08)', padding: '12px' }} />
                  <Area type="monotone" dataKey="students" stroke="#2563EB" fill="url(#colorStudents)" strokeWidth={3} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </Card>
        </div>
      </section>
    </DashboardLayout>
  );
}

export default AdminDashboardPage;
