import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import Card from "../../components/ui/Card";
import Button from "../../components/ui/Button";
import logoImage from "../../assets/images/favicon.png";
import { authService } from "../../services/auth.service";

function AdminDashboardPage() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const navigate = useNavigate();

  const handleLogout = () => {
    authService.logout();
    navigate("/login", { replace: true });
  };

  return (
    <div className="min-h-screen bg-background flex overflow-hidden text-text">
      {/* Sidebar */}
      <aside 
        className={`${isSidebarOpen ? 'w-64' : 'w-20'} transition-all duration-300 ease-in-out bg-surface border-r border-border flex flex-col justify-between`}
      >
        <div>
          <div className="h-16 flex items-center justify-between px-4 border-b border-border">
            <Link to="/" className="flex items-center gap-3">
              <img src={logoImage} alt="Logo" className="h-8 w-8 rounded-lg" />
              {isSidebarOpen && <span className="font-bold text-lg whitespace-nowrap">Learnly AI</span>}
            </Link>
            <button 
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              className="text-text-muted hover:text-text transition-colors p-1"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          </div>

          <nav className="p-4 space-y-2">
            {[
              { name: 'Dashboard', to: '/admin/dashboard', icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6' },
              { name: 'Users', to: '/admin/users', icon: 'M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z' },
            ].map((item, index) => (
              <Link 
                key={index}
                to={item.to}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors ${index === 0 ? 'bg-primary/10 text-primary' : 'text-text-soft hover:bg-surface-muted hover:text-text'}`}
                title={!isSidebarOpen ? item.name : undefined}
              >
                <svg className="w-5 h-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={item.icon} />
                </svg>
                {isSidebarOpen && <span className="font-medium">{item.name}</span>}
              </Link>
            ))}
          </nav>
        </div>

        <div className="p-4 border-t border-border">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-primary to-accent flex items-center justify-center text-white font-bold flex-shrink-0">
              A
            </div>
            {isSidebarOpen && (
              <div className="overflow-hidden">
                <p className="text-sm font-medium truncate">Admin User</p>
                <p className="text-xs text-text-muted truncate">admin@school.edu</p>
              </div>
            )}
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col min-w-0 bg-background relative overflow-y-auto">
        {/* Background Accents */}
        <div className="absolute top-0 right-0 w-96 h-96 bg-primary/5 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2 pointer-events-none"></div>
        
        {/* Header */}
        <header className="h-16 flex items-center justify-between px-8 border-b border-border/50 sticky top-0 bg-background/80 backdrop-blur-md z-10">
          <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-text to-text-soft">
            Overview
          </h1>
          <div className="flex items-center gap-4">
            <button className="text-text-soft hover:text-primary transition-colors">
              <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
              </svg>
            </button>
            <Link to="/admin/users">
              <Button variant="outline" size="sm">Manage Users</Button>
            </Link>
            <Button variant="secondary" size="sm" onClick={handleLogout}>
              Logout
            </Button>
          </div>
        </header>

        {/* Dashboard Content */}
        <div className="p-8 max-w-6xl mx-auto w-full space-y-8 relative z-0">
          
          <div className="flex items-end justify-between">
            <div>
              <h2 className="text-3xl font-extrabold tracking-tight">Welcome back, Admin!</h2>
              <p className="text-text-muted mt-1">Here's what's happening at your school today.</p>
            </div>
            <div className="text-sm text-text-soft bg-surface border border-border px-3 py-1.5 rounded-full shadow-sm">
              Greenwood High School
            </div>
          </div>

          {/* Stats Row */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              { label: "Total Students", value: "1,248", trend: "+12% this month", color: "from-blue-500/20 to-cyan-500/20", iconColor: "text-blue-500" },
              { label: "Active Teachers", value: "42", trend: "+2 this week", color: "from-emerald-500/20 to-teal-500/20", iconColor: "text-emerald-500" },
              { label: "WhatsApp Queries", value: "892", trend: "Today", color: "from-purple-500/20 to-pink-500/20", iconColor: "text-purple-500" },
            ].map((stat, i) => (
              <Card key={i} className="p-6 relative overflow-hidden group hover:shadow-lg transition-all duration-300 border-border/50 bg-surface/50 backdrop-blur-sm">
                <div className={`absolute top-0 right-0 w-32 h-32 bg-gradient-to-br ${stat.color} rounded-full blur-2xl -translate-y-1/2 translate-x-1/2 group-hover:scale-110 transition-transform duration-500`}></div>
                <div className="relative z-10">
                  <p className="text-sm font-medium text-text-soft">{stat.label}</p>
                  <p className="text-4xl font-bold mt-2 text-text">{stat.value}</p>
                  <div className="mt-4 flex items-center gap-2 text-xs font-medium">
                    <span className={`px-2 py-1 rounded-full bg-surface border border-border ${stat.iconColor}`}>
                      {stat.trend}
                    </span>
                  </div>
                </div>
              </Card>
            ))}
          </div>

          {/* Quick Actions & Recent Activity */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <Card className="lg:col-span-2 p-6 border-border/50 bg-surface/50 backdrop-blur-sm">
              <h3 className="text-lg font-bold mb-4">AI Usage Overview</h3>
              <div className="h-64 flex items-center justify-center border border-dashed border-border rounded-lg bg-background/50">
                <p className="text-text-muted flex items-center gap-2">
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
                  </svg>
                  Usage Chart Placeholder
                </p>
              </div>
            </Card>

            <Card className="p-6 border-border/50 bg-surface/50 backdrop-blur-sm">
              <h3 className="text-lg font-bold mb-4">Quick Actions</h3>
              <div className="space-y-3">
                {[
                  { name: "Add New Student", icon: "M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" },
                  { name: "Create Class", icon: "M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" },
                  { name: "Broadcast Message", icon: "M11 5.882V19.24a1.76 1.76 0 01-3.417.592l-2.147-6.15M18 13a3 3 0 100-6M5.436 13.683A4.001 4.001 0 017 6h1.832c4.1 0 7.625-1.234 9.168-3v14c-1.543-1.766-5.067-3-9.168-3H7a3.988 3.988 0 01-1.564-.317z" },
                ].map((action, i) => (
                  <button key={i} className="w-full flex items-center gap-3 p-3 rounded-lg border border-border hover:border-primary/50 hover:bg-primary/5 transition-all text-left group">
                    <div className="p-2 rounded-md bg-surface group-hover:bg-primary/10 transition-colors">
                      <svg className="w-5 h-5 text-text-soft group-hover:text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={action.icon} />
                      </svg>
                    </div>
                    <span className="font-medium text-sm text-text-soft group-hover:text-text transition-colors">{action.name}</span>
                  </button>
                ))}
              </div>
            </Card>
          </div>
          
        </div>
      </main>
    </div>
  );
}

export default AdminDashboardPage;
