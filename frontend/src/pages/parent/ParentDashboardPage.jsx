import { Link, useNavigate } from "react-router-dom";
import Card from "../../components/ui/Card";
import Button from "../../components/ui/Button";
import { authService } from "../../services/auth.service";

function ParentDashboardPage() {
  const navigate = useNavigate();

  const handleLogout = () => {
    authService.logout();
    navigate("/login", { replace: true });
  };

  return (
    <div className="min-h-screen bg-background flex text-text">
      <aside className="w-64 transition-all duration-300 bg-surface border-r border-border flex flex-col">
        <div className="h-16 flex items-center justify-between px-4 border-b border-border">
          <Link to="/" className="flex items-center gap-3">
            <span className="font-bold text-lg">Learnly AI</span>
          </Link>
        </div>
        <nav className="p-4 space-y-2">
          <Link to="/parent/dashboard" className="flex items-center gap-3 px-3 py-2.5 rounded-lg bg-primary/10 text-primary">
            <span>Dashboard</span>
          </Link>
        </nav>
      </aside>
      <main className="flex-1 p-6 md:p-8">
        <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <h1 className="text-2xl font-bold">Parent Dashboard</h1>
          <Button variant="secondary" size="small" onClick={handleLogout}>
            Logout
          </Button>
        </div>
        <Card className="p-6">
          <p className="text-text-muted">Welcome to your parent portal.</p>
        </Card>
      </main>
    </div>
  );
}

export default ParentDashboardPage;
