import { useEffect, useMemo, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import {
  BarChart3,
  Bell,
  BookOpen,
  CalendarDays,
  CheckSquare,
  ChevronDown,
  ChevronsRight,
  ClipboardList,
  CreditCard,
  FileText,
  GraduationCap,
  HelpCircle,
  Home,
  Library,
  LogOut,
  Menu,
  MessageSquare,
  Moon,
  PanelLeftClose,
  PanelLeftOpen,
  Receipt,
  Search,
  Settings,
  Shield,
  Sun,
  Users,
  X,
} from "lucide-react";
import Button from "../ui/Button";
import Avatar from "../ui/Avatar";
import Dropdown from "../ui/Dropdown";
import Input from "../ui/Input";
import Modal from "../ui/Modal";
import logoImage from "../../assets/images/favicon.png";
import { authService } from "../../services/auth.service";
import { authSession, parseApiError } from "../../services/api";
import { userService } from "../../services/user.service";
import { cn } from "../../utils/cn";
import BottomNav from "./BottomNav";

const roleLabels = {
  admin: "Administrator",
  teacher: "Teacher",
  student: "Student",
  parent: "Parent",
  superadmin: "Platform admin",
};

const navGroups = {
  admin: [
    {
      label: "Overview",
      items: [
        { label: "Dashboard", to: "/admin/dashboard", icon: Home },
        { label: "Calendar", to: "/admin/timetable", icon: CalendarDays },
      ],
    },
    {
      label: "Academics",
      items: [
        { label: "Students", to: "/admin/students", icon: GraduationCap },
        { label: "Teachers", to: "/admin/teachers", icon: Users },
        { label: "Classes", to: "/admin/classes", icon: Library },
        { label: "Subjects", to: "/admin/subjects", icon: BookOpen },
        { label: "Timetable", to: "/admin/timetable", icon: CalendarDays },
        { label: "Attendance", to: "/admin/attendance", icon: CheckSquare },
        { label: "Grades & Exams", to: "/admin/results", icon: ClipboardList },
      ],
    },
    {
      label: "Communication",
      items: [
        { label: "Notices", to: "/admin/announcements", icon: FileText },
        { label: "Messages", to: "/admin/messages", icon: MessageSquare, badge: "3" },
        { label: "Users", to: "/admin/users", icon: Shield },
      ],
    },
    {
      label: "Operations",
      items: [
        { label: "Reports", to: "/admin/reports", icon: BarChart3 },
        { label: "Fees", to: "/admin/fees", icon: Receipt },
        { label: "Payments", to: "/admin/payments", icon: CreditCard },
        { label: "Settings", to: "/admin/settings", icon: Settings },
      ],
    },
  ],
  teacher: [
    {
      label: "Teaching",
      items: [
        { label: "Dashboard", to: "/teacher/dashboard", icon: Home },
        { label: "My Classes", to: "/teacher/classes", icon: Library },
        { label: "Students", to: "/teacher/students", icon: GraduationCap },
        { label: "Subjects", to: "/teacher/subjects", icon: BookOpen },
        { label: "Timetable", to: "/teacher/timetable", icon: CalendarDays },
        { label: "Attendance", to: "/teacher/attendance", icon: CheckSquare },
        { label: "Assignments", to: "/teacher/assignments", icon: ClipboardList },
        { label: "Exams", to: "/teacher/exams", icon: FileText },
        { label: "Results", to: "/teacher/results", icon: BarChart3 },
      ],
    },
  ],
  student: [
    {
      label: "Learning",
      items: [
        { label: "Dashboard", to: "/student/dashboard", icon: Home },
        { label: "Timetable", to: "/student/timetable", icon: CalendarDays },
        { label: "Assignments", to: "/student/assignments", icon: ClipboardList },
        { label: "Results", to: "/student/results", icon: BarChart3 },
        { label: "Notices", to: "/student/notices", icon: FileText },
      ],
    },
  ],
  parent: [
    {
      label: "Family",
      items: [
        { label: "Dashboard", to: "/parent/dashboard", icon: Home },
        { label: "Attendance", to: "/parent/attendance", icon: CheckSquare },
        { label: "Results", to: "/parent/results", icon: BarChart3 },
        { label: "Notices", to: "/parent/notices", icon: FileText },
        { label: "Fees", to: "/parent/fees", icon: CreditCard },
      ],
    },
  ],
  superadmin: [
    {
      label: "Platform",
      items: [
        { label: "Dashboard", to: "/superadmin/dashboard", icon: Home },
        { label: "Tenants", to: "/superadmin/dashboard", icon: Library },
        { label: "Verification", to: "/superadmin/verification", icon: Shield },
        { label: "Activity", to: "/superadmin/activity", icon: BarChart3 },
        { label: "Settings", to: "/superadmin/settings", icon: Settings },
      ],
    },
  ],
};

function getUserLabel(user) {
  return [user?.firstname, user?.lastname].filter(Boolean).join(" ") || user?.email || "Anita Sharma";
}

function getRole(user, fallback) {
  return String(user?.role || authSession.getRole() || fallback || "admin").toLowerCase();
}

function SidebarContent({ role, collapsed, onToggleCollapsed, onNavigate, mobile = false }) {
  const location = useLocation();
  const groups = navGroups[role] || navGroups.admin;

  return (
    <div className="flex h-full flex-col">
      <div className="flex h-20 items-center gap-3 px-4">
        <Link to="/" className="flex min-w-0 items-center gap-3" onClick={onNavigate}>
          <img src={logoImage} alt="Learnly AI" className="h-10 w-10 rounded-2xl border border-border bg-surface p-1" />
          {!collapsed && (
            <span className="min-w-0">
              <span className="block truncate text-lg font-bold leading-tight">Learnly AI</span>
              <span className="block truncate text-xs font-medium text-text-muted">School Management</span>
            </span>
          )}
        </Link>
        {!mobile && (
          <Button
            type="button"
            variant="ghost"
            size="icon"
            className="ml-auto hidden lg:inline-flex"
            onClick={onToggleCollapsed}
            aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
          >
            {collapsed ? <PanelLeftOpen className="h-4 w-4" /> : <PanelLeftClose className="h-4 w-4" />}
          </Button>
        )}
      </div>

      {!collapsed && (
        <div className="mx-4 mb-5 rounded-2xl border border-border bg-surface p-3">
          <div className="flex items-center gap-3">
            <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary-subtle text-primary">
              <Library className="h-5 w-5" />
            </span>
            <div className="min-w-0">
              <p className="truncate text-sm font-semibold">Greenfield International School</p>
              <p className="truncate text-xs text-text-muted">AY 2024-25</p>
            </div>
            <ChevronDown className="ml-auto h-4 w-4 text-text-faint" />
          </div>
        </div>
      )}

      <nav className="flex-1 space-y-5 overflow-y-auto px-3 pb-4">
        {groups.map((group) => (
          <div key={group.label}>
            {!collapsed && (
              <p className="mb-2 px-3 text-[11px] font-bold uppercase tracking-wide text-text-faint">
                {group.label}
              </p>
            )}
            <div className="space-y-1">
              {group.items.map((item) => {
                const Icon = item.icon;
                const isActive =
                  location.pathname === item.to ||
                  (item.to !== "/" && location.pathname.startsWith(`${item.to}/`));

                return (
                  <Link
                    key={`${group.label}-${item.label}`}
                    to={item.to}
                    onClick={onNavigate}
                    title={collapsed ? item.label : undefined}
                    className={cn("nav-item", isActive ? "nav-item-active" : "nav-item-idle", collapsed && "justify-center px-2")}
                  >
                    <Icon className="h-4 w-4 shrink-0" />
                    {!collapsed && (
                      <>
                        <span className="truncate">{item.label}</span>
                        {item.badge && (
                          <span className={cn("ml-auto rounded-full px-2 py-0.5 text-[11px] font-bold", isActive ? "bg-white/20 text-white" : "bg-primary-soft text-primary")}>
                            {item.badge}
                          </span>
                        )}
                      </>
                    )}
                  </Link>
                );
              })}
            </div>
          </div>
        ))}
      </nav>

      {!collapsed && (
        <div className="border-t border-border p-4">
          <Link
            to="/help"
            onClick={onNavigate}
            className="flex items-center gap-3 rounded-2xl border border-border bg-surface px-3 py-3 text-sm font-medium text-text-soft transition hover:border-primary/30 hover:bg-primary-subtle hover:text-primary"
          >
            <HelpCircle className="h-4 w-4" />
            Help & Support
            <ChevronsRight className="ml-auto h-4 w-4" />
          </Link>
        </div>
      )}
    </div>
  );
}

function Topbar({ title, role, onOpenMobileNav }) {
  const navigate = useNavigate();
  const user = authSession.getUser();
  const userName = getUserLabel(user);
  const [themeHint, setThemeHint] = useState(() => {
    if (typeof window === "undefined") return "light";
    return (
      localStorage.getItem("theme") ||
      (window.matchMedia?.("(prefers-color-scheme: dark)").matches ? "dark" : "light")
    );
  });

  const toggleTheme = () => {
    setThemeHint((current) => {
      const nextTheme = current === "light" ? "dark" : "light";
      document.documentElement.dataset.theme = nextTheme;
      localStorage.setItem("theme", nextTheme);
      return nextTheme;
    });
  };

  useEffect(() => {
    document.documentElement.dataset.theme = themeHint;
  }, [themeHint]);

  const handleLogout = () => {
    authService.logout();
    navigate("/login", { replace: true });
  };

  return (
    <header className="sticky top-0 z-30 border-b border-border bg-background/90 backdrop-blur-xl">
      <div className="flex min-h-16 items-center gap-3 px-4 sm:min-h-20 sm:px-6 lg:px-8">
        <Button
          type="button"
          variant="ghost"
          size="icon"
          className="lg:hidden"
          onClick={onOpenMobileNav}
          aria-label="Open navigation"
        >
          <Menu className="h-5 w-5" />
        </Button>

        <div className="min-w-0 lg:hidden">
          <p className="truncate text-sm font-semibold">{title}</p>
          <p className="truncate text-xs text-text-muted">Greenfield International School</p>
        </div>

        <div className="hidden w-full max-w-lg items-center gap-3 rounded-2xl border border-border bg-surface px-3.5 py-2.5 shadow-sm lg:flex">
          <Search className="h-4 w-4 text-text-faint" />
          <input
            type="search"
            aria-label="Search workspace"
            placeholder="Search students, classes, teachers, notes..."
            className="w-full bg-transparent text-sm text-text outline-none placeholder:text-text-faint"
          />
          <kbd className="rounded-md border border-border bg-surface-muted px-1.5 py-0.5 text-xs font-semibold text-text-faint">/</kbd>
        </div>

        <div className="ml-auto flex items-center gap-2">
          <Dropdown
            trigger={
              <Button type="button" variant="outline" className="hidden sm:inline-flex">
                <CalendarDays className="h-4 w-4" />
                2024-25
                <ChevronDown className="h-4 w-4 text-text-faint" />
              </Button>
            }
          >
            {["2024-25", "2023-24", "2022-23"].map((year) => (
              <button key={year} type="button" className="w-full rounded-xl px-3 py-2 text-left text-sm font-medium text-text-soft hover:bg-surface-muted">
                {year}
              </button>
            ))}
          </Dropdown>

          <Button
            type="button"
            variant="outline"
            size="icon"
            onClick={toggleTheme}
            aria-label="Toggle theme preview"
            title="Toggle theme"
          >
            {themeHint === "light" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
          </Button>

          <Dropdown
            trigger={
              <Button type="button" variant="outline" size="icon" className="relative">
                <Bell className="h-4 w-4" />
                <span className="absolute -right-1 -top-1 flex h-5 min-w-5 items-center justify-center rounded-full bg-error px-1 text-[10px] font-bold text-white">
                  8
                </span>
              </Button>
            }
          >
            <div className="px-2 py-1">
              <p className="text-sm font-semibold">Notifications</p>
              <p className="text-xs text-text-muted">No live notification feed is connected yet.</p>
            </div>
            <p className="mt-2 rounded-xl bg-surface-muted px-3 py-3 text-sm text-text-muted">
              Notifications will appear here when the backend exposes them.
            </p>
          </Dropdown>

          <Dropdown
            trigger={
              <button type="button" className="flex items-center gap-3 rounded-2xl border border-border bg-surface p-1.5 pr-3 shadow-sm transition hover:bg-surface-muted" aria-label="Open account menu">
                <Avatar name={userName} />
                <span className="hidden min-w-0 text-left xl:block">
                  <span className="block max-w-32 truncate text-sm font-semibold">{userName}</span>
                  <span className="block text-xs text-text-muted">{roleLabels[role] || "User"}</span>
                </span>
                <ChevronDown className="hidden h-4 w-4 text-text-faint sm:block" />
              </button>
            }
          >
            <div className="flex items-center gap-3 px-3 py-2">
              <Avatar name={userName} />
              <div className="min-w-0">
                <p className="truncate text-sm font-semibold">{userName}</p>
                <p className="truncate text-xs text-text-muted">{roleLabels[role] || "User"}</p>
              </div>
            </div>
            <div className="my-2 border-t border-border" />
            <Link to="/profile" className="flex w-full items-center gap-2 rounded-xl px-3 py-2 text-sm font-medium text-text-soft hover:bg-surface-muted">
              <Settings className="h-4 w-4" />
              Account settings
            </Link>
            <button type="button" onClick={handleLogout} className="flex w-full items-center gap-2 rounded-xl px-3 py-2 text-sm font-medium text-error hover:bg-error-soft">
              <LogOut className="h-4 w-4" />
              Log out
            </button>
          </Dropdown>
        </div>
      </div>
    </header>
  );
}

function DashboardLayout({
  role: roleProp,
  title = "Dashboard",
  description,
  actions,
  children,
}) {
  const user = authSession.getUser();
  const role = getRole(user, roleProp);
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [profileUser, setProfileUser] = useState(user);
  const [profileForm, setProfileForm] = useState(() => ({
    firstname: user?.firstname || "",
    lastname: user?.lastname || "",
    phone_number: user?.phone_number || "",
    whatsapp_id: user?.whatsapp_id || "",
  }));
  const [profileErrors, setProfileErrors] = useState({});
  const [profileSubmitError, setProfileSubmitError] = useState(null);
  const [isSavingProfile, setIsSavingProfile] = useState(false);

  const pageTitle = useMemo(() => title || `${roleLabels[role] || "Workspace"} Dashboard`, [role, title]);
  const needsOnboarding = Boolean(
    profileUser?.id &&
      (!profileUser.firstname || !profileUser.lastname || !profileUser.phone_number)
  );

  const handleProfileChange = (event) => {
    const { name, value } = event.target;
    setProfileForm((current) => ({ ...current, [name]: value }));
    setProfileErrors((current) => ({ ...current, [name]: undefined }));
    setProfileSubmitError(null);
  };

  const handleProfileSubmit = async (event) => {
    event.preventDefault();
    if (!profileUser?.id) return;

    setIsSavingProfile(true);
    setProfileErrors({});
    setProfileSubmitError(null);

    try {
      const updatedUser = await userService.updateProfile(profileUser.id, {
        firstname: profileForm.firstname,
        lastname: profileForm.lastname,
        phone_number: profileForm.phone_number,
        whatsapp_id: profileForm.whatsapp_id || null,
      });

      const nextUser = { ...profileUser, ...updatedUser };
      authSession.setUser(nextUser);
      setProfileUser(nextUser);
    } catch (error) {
      const parsed = parseApiError(error, "Failed to update your profile.");
      setProfileErrors(parsed.fieldErrors || {});
      setProfileSubmitError(parsed.message);
    } finally {
      setIsSavingProfile(false);
    }
  };

  return (
    <div className="min-h-screen bg-background text-text">
      <a
        href="#dashboard-content"
        className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-[60] focus:rounded-xl focus:bg-primary focus:px-4 focus:py-2 focus:text-sm focus:font-semibold focus:text-white"
      >
        Skip to content
      </a>
      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-40 hidden border-r border-border bg-surface lg:block",
          collapsed ? "w-[88px]" : "w-[272px]"
        )}
      >
        <SidebarContent
          role={role}
          collapsed={collapsed}
          onToggleCollapsed={() => setCollapsed((current) => !current)}
        />
      </aside>

      {mobileOpen && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div className="absolute inset-0 bg-slate-950/40 backdrop-blur-sm" onClick={() => setMobileOpen(false)} />
          <aside className="absolute inset-y-0 left-0 w-[86vw] max-w-80 border-r border-border bg-surface shadow-premium">
            <div className="absolute right-3 top-3">
              <Button type="button" variant="ghost" size="icon" onClick={() => setMobileOpen(false)} aria-label="Close navigation">
                <X className="h-5 w-5" />
              </Button>
            </div>
            <SidebarContent role={role} collapsed={false} mobile onNavigate={() => setMobileOpen(false)} />
          </aside>
        </div>
      )}

      <div className={cn("min-h-screen transition-all duration-300", collapsed ? "lg:pl-[88px]" : "lg:pl-[272px]")}>
        <Topbar title={pageTitle} role={role} onOpenMobileNav={() => setMobileOpen(true)} />

        <main id="dashboard-content" className="px-4 py-5 pb-24 sm:px-6 lg:px-8 lg:py-6 lg:pb-6">
          <div className="mx-auto max-w-[1400px] w-full space-y-6">
            <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
              <div className="min-w-0">
                <h1 className="text-2xl font-semibold tracking-tight sm:text-3xl">
                  {pageTitle}
                </h1>
                {description && (
                  <p className="mt-2 max-w-3xl text-sm leading-6 text-text-muted">
                    {description}
                  </p>
                )}
              </div>
              {actions && <div className="flex flex-wrap gap-2">{actions}</div>}
            </div>
            {children}
          </div>
        </main>
      </div>
      <BottomNav role={role} onOpenMenu={() => setMobileOpen(true)} />
      <Modal
        open={needsOnboarding}
        title="Complete your profile"
        description="Add the required details before continuing to your workspace."
        footer={
          <Button form="profile-onboarding-form" type="submit" className="w-full" disabled={isSavingProfile}>
            {isSavingProfile ? "Saving..." : "Save profile"}
          </Button>
        }
      >
        {profileSubmitError && (
          <div className="mb-4 rounded-2xl border border-error/30 bg-error-soft px-4 py-3 text-sm font-medium text-error">
            {profileSubmitError}
          </div>
        )}
        <form id="profile-onboarding-form" onSubmit={handleProfileSubmit} className="space-y-4">
          <div className="grid gap-4 sm:grid-cols-2">
            <Input label="First name" name="firstname" value={profileForm.firstname} onChange={handleProfileChange} error={profileErrors.firstname} required />
            <Input label="Last name" name="lastname" value={profileForm.lastname} onChange={handleProfileChange} error={profileErrors.lastname} required />
          </div>
          <Input label="Phone number" name="phone_number" value={profileForm.phone_number} onChange={handleProfileChange} placeholder="+2348012345678" error={profileErrors.phone_number} required />
          <Input label="WhatsApp ID" name="whatsapp_id" value={profileForm.whatsapp_id} onChange={handleProfileChange} placeholder="+2348012345678" error={profileErrors.whatsapp_id} />
        </form>
      </Modal>
    </div>
  );
}

export default DashboardLayout;
