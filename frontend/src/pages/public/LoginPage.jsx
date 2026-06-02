import  { useState } from "react";
import { Link } from "react-router-dom";
import Card from "../../components/ui/Card";
import Input from "../../components/ui/Input";
import Button from "../../components/ui/Button";

function LoginPage() {
  const [formData, setFormData] = useState({ email: "", password: "" });
  const [isLoading, setIsLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setIsLoading(true);
    // Simulate login
    setTimeout(() => {
      setIsLoading(false);
      console.log("Logged in with:", formData);
    }, 1500);
  };

  return (
    <div className="min-h-screen relative flex items-center justify-center bg-background p-4 text-text overflow-hidden">
      {/* Background Animated Blobs */}
      <div className="absolute inset-0 z-0 pointer-events-none">
        <div className="absolute top-1/4 left-1/4 h-72 w-72 rounded-full bg-primary opacity-30 blur-3xl animate-blob"></div>
        <div className="absolute top-1/3 right-1/4 h-72 w-72 rounded-full bg-accent opacity-30 blur-3xl animate-blob animation-delay-2000"></div>
        <div className="absolute -bottom-8 left-1/2 h-72 w-72 -translate-x-1/2 rounded-full bg-primary opacity-20 blur-3xl animate-blob animation-delay-4000"></div>
      </div>

      <div className="w-full max-w-md animate-fadein z-10 relative">
        <Link
          to="/"
          className="mb-8 flex items-center justify-center gap-3 transition-opacity duration-300 hover:opacity-90"
        >
          <img
            src="/src/assets/images/favicon.png"
            alt="Learnly AI logo"
            className="h-10 w-10 rounded-xl border border-border bg-surface p-1 shadow-sm"
          />
          <p className="text-xl font-extrabold tracking-tight text-text">
            Learnly AI
          </p>
        </Link>

        <Card className="p-8 shadow-2xl relative overflow-hidden">
          <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-primary via-accent to-primary animate-text-gradient bg-[length:200%_auto]"></div>
          
          <div className="text-center mb-8">
            <h1 className="text-2xl font-bold text-text">Welcome back</h1>
            <p className="text-sm text-text-muted mt-2">Log in to manage your school workspace.</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="group">
              <Input
                label="Work email"
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="name@school.edu"
                required
                className="transition-all duration-300 group-hover:border-primary/50"
              />
            </div>
            
            <div className="group">
              <Input
                label="Password"
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="••••••••"
                required
                className="transition-all duration-300 group-hover:border-primary/50"
              />
            </div>

            <div className="flex items-center justify-between text-sm">
              <label className="flex items-center gap-2 cursor-pointer">
                <input type="checkbox" className="rounded border-border text-primary focus:ring-primary/20 accent-primary" />
                <span className="text-text-soft">Remember me</span>
              </label>
              <a href="#" className="font-semibold text-primary hover:text-primary-hover transition-colors">
                Forgot password?
              </a>
            </div>

            <Button
              type="submit"
              className="w-full mt-2 group relative overflow-hidden"
              disabled={isLoading}
            >
              <span className={`transition-all duration-300 ${isLoading ? 'opacity-0' : 'opacity-100'}`}>
                Log in to workspace
              </span>
              {isLoading && (
                <span className="absolute inset-0 flex items-center justify-center">
                  <span className="h-5 w-5 rounded-full border-2 border-text-inverse border-t-transparent animate-spin"></span>
                </span>
              )}
            </Button>
          </form>

          <p className="mt-8 text-center text-sm text-text-soft">
            Don't have an account?{" "}
            <Link to="/register" className="font-semibold text-primary hover:text-primary-hover transition-colors">
              Get started
            </Link>
          </p>
        </Card>
      </div>
    </div>
  );
}

export default LoginPage;
