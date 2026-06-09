import { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import Card from "../../components/ui/Card";
import Input from "../../components/ui/Input";
import Button from "../../components/ui/Button";
import logoImage from "../../assets/images/favicon.png";
import { authService } from "../../services/auth.service";
import { parseApiError } from "../../services/api";

const ROLE_ROUTES = {
  SUPERADMIN: "/superadmin/dashboard",
  ADMIN: "/admin/dashboard",
  TEACHER: "/teacher/dashboard",
  STUDENT: "/student/dashboard",
  PARENT: "/parent/dashboard",
};

function LoginPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const justVerified = searchParams.get("verified") === "true";
  const passwordReset = searchParams.get("reset") === "true";
  const inviteCompleted = searchParams.get("invite") === "success";

  const [formData, setFormData] = useState({
    email: "",
    password: "",
    remember: true,
  });

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [fieldErrors, setFieldErrors] = useState({});

  const redirectToVerification = (
    email,
    notice,
    purpose = "verification",
    redirectTo = "/verify-otp"
  ) => {
    if (!email) return;

    authService.setPendingVerificationEmail(email);

    navigate(
      `${redirectTo}?email=${encodeURIComponent(email)}&purpose=${encodeURIComponent(purpose)}`,
      {
        replace: true,
        state: { notice },
      }
    );
  };

  const handleChange = (event) => {
    const { checked, name, type, value } = event.target;

    setFormData((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));

    setFieldErrors((prev) => ({
      ...prev,
      [name]: undefined,
    }));

    setError(null);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    setIsLoading(true);
    setError(null);
    setFieldErrors({});

    try {
      const data = await authService.login(formData.email, formData.password, {
        remember: formData.remember,
      });

      authService.clearPendingVerificationEmail();

      const role = String(data?.role || data?.user?.role || "").toUpperCase();
      const route = ROLE_ROUTES[role] || "/";

      navigate(route, { replace: true });
    } catch (err) {
      const apiError = parseApiError(err, "Invalid email or password.");

      if (Object.keys(apiError.fieldErrors || {}).length > 0) {
        setFieldErrors(apiError.fieldErrors);
      }

      if (apiError.verificationRequired) {
        redirectToVerification(
          apiError.email || formData.email,
          apiError.message,
          apiError.purpose || "verification",
          apiError.redirectTo || "/verify-otp"
        );
        return;
      }

      setError(apiError.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen relative flex items-center justify-center bg-background p-4 text-text overflow-hidden">
      <div className="absolute inset-0 z-0 pointer-events-none">
        <div className="absolute top-1/4 left-1/4 h-72 w-72 rounded-full bg-primary opacity-30 blur-3xl animate-blob" />
        <div className="absolute top-1/3 right-1/4 h-72 w-72 rounded-full bg-accent opacity-30 blur-3xl animate-blob animation-delay-2000" />
        <div className="absolute -bottom-8 left-1/2 h-72 w-72 -translate-x-1/2 rounded-full bg-primary opacity-20 blur-3xl animate-blob animation-delay-4000" />
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
          <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-primary via-accent to-primary animate-text-gradient bg-[length:200%_auto]" />

          <div className="text-center mb-8">
            <h1 className="text-2xl font-bold text-text">Welcome back</h1>
            <p className="text-sm text-text-muted mt-2">
              Log in to manage your school workspace.
            </p>
          </div>

          {justVerified && (
            <div className="mb-4 p-3 bg-green-500/10 border border-green-500/50 text-green-500 rounded-md text-sm text-center">
              Account verified! You can now log in.
            </div>
          )}

          {passwordReset && (
            <div className="mb-4 p-3 bg-green-500/10 border border-green-500/50 text-green-500 rounded-md text-sm text-center">
              Password reset successful. You can now log in.
            </div>
          )}

          {inviteCompleted && (
            <div className="mb-4 p-3 bg-green-500/10 border border-green-500/50 text-green-500 rounded-md text-sm text-center">
              Account setup completed successfully. You can now log in.
            </div>
          )}

          {error && (
            <div className="mb-4 p-3 bg-red-500/10 border border-red-500/50 text-red-500 rounded-md text-sm text-center">
              {error}
            </div>
          )}

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
                error={fieldErrors.email}
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
                error={fieldErrors.password}
                className="transition-all duration-300 group-hover:border-primary/50"
              />
            </div>

            <div className="flex items-center justify-between text-sm">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  name="remember"
                  checked={formData.remember}
                  onChange={handleChange}
                  className="rounded border-border text-primary focus:ring-primary/20 accent-primary"
                />
                <span className="text-text-soft">Remember me</span>
              </label>

              <Link
                to="/forgot-password"
                className="font-semibold text-primary hover:text-primary-hover transition-colors"
              >
                Forgot password?
              </Link>
            </div>

            <Button
              type="submit"
              className="w-full mt-2 group relative overflow-hidden"
              disabled={isLoading}
            >
              <span
                className={`transition-all duration-300 ${
                  isLoading ? "opacity-0" : "opacity-100"
                }`}
              >
                Log in to workspace
              </span>

              {isLoading && (
                <span className="absolute inset-0 flex items-center justify-center">
                  <span className="h-5 w-5 rounded-full border-2 border-text-inverse border-t-transparent animate-spin" />
                </span>
              )}
            </Button>
          </form>

          <p className="mt-8 text-center text-sm text-text-soft">
            Don't have an account?{" "}
            <Link
              to="/register"
              className="font-semibold text-primary hover:text-primary-hover transition-colors"
            >
              Get started
            </Link>
          </p>
        </Card>
      </div>
    </div>
  );
}

export default LoginPage;
