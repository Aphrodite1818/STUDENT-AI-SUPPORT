import { useEffect, useState } from "react";
import { Link, useSearchParams, useNavigate } from "react-router-dom";
import Card from "../../components/ui/Card";
import Input from "../../components/ui/Input";
import Button from "../../components/ui/Button";
import logoImage from "../../assets/images/favicon.png";
import { authService } from "../../services/auth.service";
import { getErrorMessage } from "../../services/api";

function InvitePage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const token = searchParams.get("token");
  const [inviteMeta, setInviteMeta] = useState({
    status: token ? "loading" : "invalid",
    purpose: null,
  });

  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);

  useEffect(() => {
    if (!token) {
      return;
    }

    let isMounted = true;
    const timeoutId = window.setTimeout(() => {
      setInviteMeta({ status: "loading", purpose: null });

      const loadInviteStatus = async () => {
        try {
          const result = await authService.getInviteStatus(token);
          if (!isMounted) return;
          setInviteMeta({
            status: result?.status || "invalid",
            purpose: result?.purpose || null,
          });
        } catch {
          if (!isMounted) return;
          setInviteMeta({ status: "invalid", purpose: null });
        }
      };

      loadInviteStatus();
    }, 0);

    return () => {
      isMounted = false;
      window.clearTimeout(timeoutId);
    };
  }, [token]);

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
      const result =
        inviteMeta.purpose === "tenant_activation"
          ? await authService.activateTenant(
              formData.email,
              formData.password,
              token,
            )
          : await authService.acceptInvite(
              formData.email,
              formData.password,
              token,
            );
      setSuccessMessage(result?.detail || "Account activated successfully.");
      navigate("/login?verified=true", { replace: true });
    } catch (err) {
      const message = getErrorMessage(err, "Failed to activate account.");
      if (message.toLowerCase().includes("already been used")) {
        setInviteMeta((prev) => ({ ...prev, status: "used" }));
      } else if (message.toLowerCase().includes("invalid")) {
        setInviteMeta((prev) => ({ ...prev, status: "invalid" }));
      } else if (
        message.toLowerCase().includes("expired")
      ) {
        setInviteMeta((prev) => ({ ...prev, status: "expired" }));
      } else {
        setError(message);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const inviteStatus = token ? inviteMeta.status : "invalid";
  const invitePurpose = token ? inviteMeta.purpose : null;
  const isTenantActivation = invitePurpose === "tenant_activation";
  const isInviteLoading = inviteStatus === "loading";
  const isInviteValid = inviteStatus === "valid";
  const showExpiredState = inviteStatus === "expired";
  const showInvalidState = inviteStatus === "invalid";
  const showUsedState = inviteStatus === "used";

  const heading = isTenantActivation
    ? "Complete administrator setup"
    : "Join your school";
  const subheading = isTenantActivation
    ? "Confirm your email and set your password to activate your administrator account."
    : "Use your invite link to confirm your email address and set your password.";

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
            <h1 className="text-2xl font-bold text-text">{heading}</h1>
            <p className="text-sm text-text-muted mt-2">
              {subheading}
            </p>
          </div>

          {!token && (
            <div className="mb-6 p-3 bg-red-500/10 border border-red-500/50 text-red-500 rounded-md text-sm text-center">
              Missing invite token. Please check your invitation link.
            </div>
          )}

          {isInviteLoading && (
            <div className="mb-6 p-3 bg-primary/10 border border-primary/20 text-text rounded-md text-sm text-center">
              Checking your invite link...
            </div>
          )}

          {showInvalidState && (
            <div className="mb-6 p-4 bg-red-500/10 border border-red-500/40 text-sm rounded-md text-center">
              <p className="font-semibold text-red-700 mb-2">
                This invite link is invalid.
              </p>
              <p className="text-red-800/90">
                Open the latest email invite, or request a new link if this one was copied from a different environment.
              </p>
            </div>
          )}

          {showExpiredState && (
            <div className="mb-6 p-4 bg-yellow-500/10 border border-yellow-500/40 text-sm rounded-md text-center">
              <p className="font-semibold text-yellow-700 mb-2">
                {isTenantActivation ? "This activation link has expired." : "This invite link has expired."}
              </p>
              <p className="text-yellow-800/90">
                {isTenantActivation
                  ? "Please contact support or the platform team for a new activation link."
                  : "Please request a new invite from your school admin."}
              </p>
            </div>
          )}

          {showUsedState && (
            <div className="mb-6 p-4 bg-green-500/10 border border-green-500/40 text-sm rounded-md text-center">
              <p className="font-semibold text-green-700 mb-2">
                This invite link has already been used.
              </p>
              <p className="text-green-800/90">
                Your account setup is complete. Please log in instead.
              </p>
            </div>
          )}

          {error && (
            <div className="mb-4 p-3 bg-red-500/10 border border-red-500/50 text-red-500 rounded-md text-sm text-center">
              {error}
            </div>
          )}

          {successMessage && !error && (
            <div className="mb-4 p-3 bg-green-500/10 border border-green-500/50 text-green-500 rounded-md text-sm text-center">
              {successMessage}
            </div>
          )}

          {isInviteValid && (
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
                  {isTenantActivation ? "Activate Account" : "Set Up Account"}
                </span>
                {isLoading && (
                  <span className="absolute inset-0 flex items-center justify-center">
                    <span className="h-5 w-5 rounded-full border-2 border-text-inverse border-t-transparent animate-spin"></span>
                  </span>
                )}
              </Button>
            </div>
          </form>
          )}

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
