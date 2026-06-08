import { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import Card from "../../components/ui/Card";
import Input from "../../components/ui/Input";
import Button from "../../components/ui/Button";
import logoImage from "../../assets/images/favicon.png";
import { authService } from "../../services/auth.service";
import { getErrorMessage } from "../../services/api";
import { getTokenPayload } from "../../utils/auth";

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
  const [needsVerification, setNeedsVerification] = useState(false);
  const [canResendOtp, setCanResendOtp] = useState(false);
  const [verificationEmail, setVerificationEmail] = useState("");

  const [formData, setFormData] = useState({
    email: "",
    password: "",
    remember: true,
  });
  const [isLoading, setIsLoading] = useState(false);
  const [isResendingOtp, setIsResendingOtp] = useState(false);
  const [error, setError] = useState(null);

  const redirectToVerification = (email, notice) => {
    authService.setPendingVerificationEmail(email);
    navigate(
      `/verify-otp?email=${encodeURIComponent(email)}&purpose=verification`,
      {
        replace: true,
        state: { notice },
      }
    );
  };

  const handleChange = (e) => {
    const { checked, name, type, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
    if (needsVerification) {
      setNeedsVerification(false);
      setCanResendOtp(false);
      setError(null);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    setNeedsVerification(false);
    setCanResendOtp(false);

    try {
      const data = await authService.login(formData.email, formData.password, {
        remember: formData.remember,
      });

      authService.clearPendingVerificationEmail();

      const decoded = getTokenPayload(data.access_token);
      const role = decoded?.role?.toUpperCase();
      const route = ROLE_ROUTES[role];

      if (!route) {
        setError(`Unknown role "${decoded?.role}". Please contact support.`);
        authService.logout();
        return;
      }

      navigate(route, { replace: true });
    } catch (err) {
      if (err?.response?.status === 403) {
        const resendAvailable =
          err?.response?.headers?.["x-resend-otp-available"] === "true";
        const email =
          formData.email ||
          err?.response?.headers?.["x-email"] ||
          "";
        const verificationMessage = getErrorMessage(
          err,
          "Your account needs to be verified before logging in."
        );

        setVerificationEmail(email);

        if (resendAvailable && email) {
          try {
            await authService.requestOtp(email, "verification");
            redirectToVerification(
              email,
              "Your account is not verified yet. We sent a new verification code to your email."
            );
            return;
          } catch (resendErr) {
            if (resendErr?.response?.status === 429) {
              redirectToVerification(
                email,
                "Your account is not verified yet. A verification code was sent recently. Please use that code or wait a moment before requesting another one."
              );
              return;
            }

            const resendMessage = getErrorMessage(
              resendErr,
              "We couldn't send a new verification code. Please try again."
            );
            setNeedsVerification(true);
            setCanResendOtp(true);
            setError(`${verificationMessage} ${resendMessage}`);
            return;
          }
        }

        setNeedsVerification(resendAvailable);
        setCanResendOtp(resendAvailable);
        setError(verificationMessage);
      } else {
        setError(getErrorMessage(err, "Invalid email or password."));
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleResendOtp = async () => {
    setIsResendingOtp(true);
    setError(null);
    try {
      await authService.requestOtp(verificationEmail, "verification");
      navigate(`/verify-otp?email=${encodeURIComponent(verificationEmail)}&purpose=verification`);
    } catch (err) {
      setError(getErrorMessage(err, "Failed to resend code."));
    } finally {
      setIsResendingOtp(false);
    }
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
            src={logoImage}
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
            <p className="text-sm text-text-muted mt-2">
              Log in to manage your school workspace.
            </p>
          </div>

          {justVerified && (
            <div className="mb-4 p-3 bg-green-500/10 border border-green-500/50 text-green-500 rounded-md text-sm text-center">
              Account verified! You can now log in.
            </div>
          )}

          {error && (
            <div className="mb-4 p-3 bg-red-500/10 border border-red-500/50 text-red-500 rounded-md text-sm text-center">
              {error}
            </div>
          )}

          {needsVerification && canResendOtp && (
            <div className="mb-4 p-4 bg-yellow-500/10 border border-yellow-500/50 rounded-md text-sm text-center">
              <p className="text-yellow-600 dark:text-yellow-400 font-medium mb-2">
                Your account needs email verification before you can log in.
              </p>
              <button
                type="button"
                onClick={handleResendOtp}
                disabled={isResendingOtp}
                className="font-semibold text-primary hover:text-primary-hover transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isResendingOtp ? "Sending..." : "Resend verification code"}
              </button>
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
                className={`transition-all duration-300 ${isLoading ? "opacity-0" : "opacity-100"}`}
              >
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
