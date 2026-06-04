import { useState } from "react";
import { Link, useSearchParams, useNavigate } from "react-router-dom";
import Card from "../../components/ui/Card";
import Input from "../../components/ui/Input";
import Button from "../../components/ui/Button";
import logoImage from "../../assets/images/favicon.png";

function InvitePage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const token = searchParams.get("token");

  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!token) {
      setError("Invalid or missing invite token.");
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      // Replace with actual user registration via invite API
      // const response = await fetch(`/api/v1/users/invite?token=${token}`, { ... })
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      console.log("Account created via invite for:", formData.email);
      // Route to OTP verification
      navigate(`/verify-otp?email=${encodeURIComponent(formData.email)}`);
      
    } catch (err) {
      setError(err.message || "Failed to create account.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen relative flex items-center justify-center bg-background p-4 text-text py-12 overflow-hidden">
      {/* Background Animated Blobs */}
      <div className="absolute inset-0 z-0 pointer-events-none">
        <div className="absolute top-1/4 right-1/4 h-80 w-80 rounded-full bg-accent opacity-30 blur-3xl animate-blob"></div>
        <div className="absolute bottom-1/4 left-1/4 h-72 w-72 rounded-full bg-primary opacity-30 blur-3xl animate-blob animation-delay-2000"></div>
      </div>

      <div className="w-full max-w-md animate-fadein z-10 relative">
        <Link
          to="/"
          className="mb-8 flex items-center justify-center gap-3 transition-opacity duration-300 hover:opacity-90"
        >
          <img
            src={logoImage}
            alt="Learnly AI logo"
            className="h-10 w-10 rounded-xl border border-border bg-surface p-1 shadow-sm"
          />
          <p className="text-xl font-extrabold tracking-tight text-text">
            Learnly AI
          </p>
        </Link>

        <Card className="p-8 shadow-2xl relative overflow-hidden">
          <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-accent via-primary to-accent animate-text-gradient bg-[length:200%_auto]"></div>
          
          <div className="text-center mb-8">
            <h1 className="text-2xl font-bold text-text">Join your school</h1>
            <p className="text-sm text-text-muted mt-2">
              You've been invited! Create your account to access the dashboard.
            </p>
          </div>

          {!token && (
            <div className="mb-6 p-3 bg-red-500/10 border border-red-500/50 text-red-500 rounded-md text-sm text-center">
              Missing invite token. Please check your invitation link.
            </div>
          )}

          {error && (
            <div className="mb-4 p-3 bg-red-500/10 border border-red-500/50 text-red-500 rounded-md text-sm text-center animate-shake">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="group">
              <Input
                label="Email"
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="name@school.edu"
                required
                className="transition-all duration-300 group-hover:border-accent/50"
              />
            </div>
            
            <div className="group">
              <Input
                label="Create Password"
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="************"
                required
                minLength={8}
                className="transition-all duration-300 group-hover:border-accent/50"
              />
            </div>

            <div className="pt-2">
              <Button
                type="submit"
                className="w-full group relative overflow-hidden"
                disabled={isLoading || !token}
              >
                <span className={`transition-all duration-300 ${isLoading ? 'opacity-0' : 'opacity-100'}`}>
                  Join School
                </span>
                {isLoading && (
                  <span className="absolute inset-0 flex items-center justify-center">
                    <span className="h-5 w-5 rounded-full border-2 border-text-inverse border-t-transparent animate-spin"></span>
                  </span>
                )}
              </Button>
            </div>
          </form>

          <p className="mt-8 text-center text-sm text-text-soft">
            Already have an account?{" "}
            <Link to="/login" className="font-semibold text-accent hover:text-accent-hover transition-colors">
              Log in
            </Link>
          </p>
        </Card>
      </div>
    </div>
  );
}

export default InvitePage;
