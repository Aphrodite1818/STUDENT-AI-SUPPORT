import { Link, useLocation, useNavigate } from "react-router-dom";
import Button from "../../components/ui/Button";
import Card from "../../components/ui/Card";
import logoImage from "../../assets/images/favicon.png";
import { authService } from "../../services/auth.service";
import { authSession } from "../../services/api";

const navItems = {
  admin: [
    { label: "Dashboard", to: "/admin/dashboard" },
    { label: "Users", to: "/admin/users" },
    { label: "Teachers", to: "/admin/teachers" },
    { label: "Students", to: "/admin/students" },
    { label: "Classes", to: "/admin/classes" },
    { label: "Subjects", to: "/admin/subjects" },
    { label: "Attendance", to: "/admin/attendance" },
    { label: "Exams", to: "/admin/exams" },
    { label: "Results", to: "/admin/results" },
    { label: "Fees", to: "/admin/fees" },
    { label: "Payments", to: "/admin/payments" },
  ],
  teacher: [
    { label: "Dashboard", to: "/teacher/dashboard" },
    { label: "My Classes", to: "/teacher/classes" },
    { label: "Students", to: "/teacher/students" },
    { label: "Subjects", to: "/teacher/subjects" },
    { label: "Attendance", to: "/teacher/attendance" },
    { label: "Exams", to: "/teacher/exams" },
    { label: "Results", to: "/teacher/results" },
  ],
};

function getUserLabel(user) {
  const name = [user?.firstname, user?.lastname].filter(Boolean).join(" ");
  return name || user?.email || "User";
}

function DashboardShell({
  role = "admin",
  title,
  description,
  actions = null,
  children,
}) {
  const location = useLocation();
  const navigate = useNavigate();
  const user = authSession.getUser();
  const items = navItems[role] || navItems.admin;

  const handleLogout = () => {
    authService.logout();
    navigate("/login", { replace: true });
  };

  return (
    <div className="min-h-screen bg-background text-text lg:flex">
      <aside className="border-b border-border bg-surface lg:sticky lg:top-0 lg:h-screen lg:w-64 lg:border-b-0 lg:border-r">
        <div className="flex h-16 items-center gap-3 border-b border-border px-5">
          <img src={logoImage} alt="Learnly AI" className="h-8 w-8 rounded-lg" />
          <Link to="/" className="font-bold">
            Learnly AI
          </Link>
        </div>

        <nav className="flex gap-2 overflow-x-auto p-4 lg:block lg:space-y-1">
          {items.map((item) => {
            const isActive = location.pathname === item.to;

            return (
              <Link
                key={item.to}
                to={item.to}
                className={`whitespace-nowrap rounded-md px-3 py-2 text-sm font-medium transition-colors lg:flex ${
                  isActive
                    ? "bg-primary/10 text-primary"
                    : "text-text-soft hover:bg-surface-muted hover:text-text"
                }`}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>

        <div className="hidden border-t border-border p-4 lg:block">
          <p className="truncate text-sm font-medium">{getUserLabel(user)}</p>
          <p className="truncate text-xs capitalize text-text-muted">
            {user?.role || role}
          </p>
        </div>
      </aside>

      <main className="min-w-0 flex-1">
        <header className="sticky top-0 z-10 border-b border-border bg-background/95 px-5 py-4 backdrop-blur md:px-8">
          <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <div>
              <h1 className="text-2xl font-bold">{title}</h1>
              {description && (
                <p className="mt-1 max-w-3xl text-sm text-text-muted">
                  {description}
                </p>
              )}
            </div>
            <div className="flex flex-wrap gap-2">
              {actions}
              <Button variant="secondary" size="small" onClick={handleLogout}>
                Logout
              </Button>
            </div>
          </div>
        </header>

        <div className="p-5 md:p-8">{children}</div>
      </main>
    </div>
  );
}

export function DashboardStat({ label, value, hint }) {
  return (
    <Card className="p-5">
      <p className="text-sm font-medium text-text-muted">{label}</p>
      <p className="mt-2 text-3xl font-bold">{value}</p>
      {hint && <p className="mt-2 text-xs text-text-soft">{hint}</p>}
    </Card>
  );
}

export default DashboardShell;
