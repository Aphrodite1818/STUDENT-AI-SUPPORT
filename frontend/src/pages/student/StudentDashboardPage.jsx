import { Link } from "react-router-dom";
import Card from "../../components/ui/Card";

function StudentDashboardPage() {
  return (
    <div className="min-h-screen bg-background flex text-text">
      <aside className="w-64 transition-all duration-300 bg-surface border-r border-border flex flex-col">
        <div className="h-16 flex items-center justify-between px-4 border-b border-border">
          <Link to="/" className="flex items-center gap-3">
            <span className="font-bold text-lg">Learnly AI</span>
          </Link>
        </div>
        <nav className="p-4 space-y-2">
          <a className="flex items-center gap-3 px-3 py-2.5 rounded-lg bg-primary/10 text-primary">
            <span>Dashboard</span>
          </a>
        </nav>
      </aside>
      <main className="flex-1 p-8">
        <h1 className="text-2xl font-bold mb-4">Student Dashboard</h1>
        <Card className="p-6">
          <p className="text-text-muted">Welcome to your learning portal.</p>
        </Card>
      </main>
    </div>
  );
}

export default StudentDashboardPage;