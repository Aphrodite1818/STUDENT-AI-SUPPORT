import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import Card from "../../components/ui/Card";
import Input from "../../components/ui/Input";
import Button from "../../components/ui/Button";
import logoImage from "../../assets/images/favicon.png";
import { tenantService } from "../../services/tenant.service";

function RegisterPage() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    schoolName: "",
    email: "",
    password: "",
    confirmPassword: "",
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);
  const [passwordStrength, setPasswordStrength] = useState(0);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));

    if (name === "password") {
      setPasswordStrength(getPasswordStrength(value));
    }
  };

  const getPasswordStrength = (password) => {
    let score = 0;
    if (password.length >= 8) score++;
    if (password.length >= 12) score++;
    if (/[A-Z]/.test(password)) score++;
    if (/[0-9]/.test(password)) score++;
    if (/[^A-Za-z0-9]/.test(password)) score++;
    return score;
  };

  const strengthLabel = ["", "Weak", "Fair", "Good", "Strong", "Very strong"];
  const strengthColor = [
    "",
    "bg-red-500",
    "bg-orange-400",
    "bg-yellow-400",
    "bg-green-400",
    "bg-green-500",
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    if (formData.password !== formData.confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    if (formData.password.length < 8) {
      setError("Password must be at least 8 characters.");
      return;
    }

    setIsLoading(true);

    try {
      const result = await tenantService.registerTenant({
        school_name: formData.schoolName,
        email: formData.email,
        password: formData.password,
      });

      if (result?.message) {
        setError(null);
        setSuccessMessage(result.message);
      }

      sessionStorage.setItem("pendingVerificationEmail", formData.email);

      navigate(`/verify-otp?email=${encodeURIComponent(formData.email)}`);
    } catch (err) {
      const message =
        err?.response?.data?.detail ||
        err?.message ||
        "Registration failed. Please try again.";
      setError(message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen relative flex items-center justify-center bg-background p-4 text-text py-12 overflow-hidden">
      {/* Background Animated Blobs */}
      <div className="absolute inset-0 z-0 pointer-events-none">
        <div className="absolute top-1/4 left-1/4 h-80 w-80 rounded-full bg-primary opacity-30 blur-3xl animate-blob"></div>
        <div className="absolute top-1/3 right-1/4 h-72 w-72 rounded-full bg-accent opacity-30 blur-3xl animate-blob animation-delay-2000"></div>
        <div className="absolute -bottom-8 left-1/2 h-96 w-96 -translate-x-1/2 rounded-full bg-primary opacity-20 blur-3xl animate-blob animation-delay-4000"></div>
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
            <h1 className="text-2xl font-bold text-text">Create an account</h1>
            <p className="text-sm text-text-muted mt-2">
              Set up Learnly AI for your school.
            </p>
          </div>

          {successMessage && !error && (
            <div className="mb-4 p-3 bg-green-500/10 border border-green-500/50 text-green-500 rounded-md text-sm text-center">
              {successMessage}
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
                label="School name"
                type="text"
                name="schoolName"
                value={formData.schoolName}
                onChange={handleChange}
                placeholder="Greenwood High School"
                required
                className="transition-all duration-300 group-hover:border-primary/50"
              />
            </div>

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
                placeholder="············"
                required
                minLength={8}
                className="transition-all duration-300 group-hover:border-primary/50"
              />
              {/* Password strength meter */}
              {formData.password.length > 0 && (
                <div className="mt-2 space-y-1">
                  <div className="flex gap-1">
                    {[1, 2, 3, 4, 5].map((level) => (
                      <div
                        key={level}
                        className={`h-1 flex-1 rounded-full transition-all duration-300 ${
                          passwordStrength >= level
                            ? strengthColor[passwordStrength]
                            : "bg-border"
                        }`}
                      />
                    ))}
                  </div>
                  <p className="text-xs text-text-muted">
                    Strength:{" "}
                    <span className="font-medium text-text">
                      {strengthLabel[passwordStrength] || "Too short"}
                    </span>
                  </p>
                </div>
              )}
            </div>

            <div className="group">
              <Input
                label="Confirm password"
                type="password"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleChange}
                placeholder="············"
                required
                className="transition-all duration-300 group-hover:border-primary/50"
              />
              {/* Inline mismatch hint */}
              {formData.confirmPassword.length > 0 &&
                formData.password !== formData.confirmPassword && (
                  <p className="mt-1 text-xs text-red-500">
                    Passwords do not match.
                  </p>
                )}
            </div>

            <div className="pt-2">
              <Button
                type="submit"
                className="w-full group relative overflow-hidden"
                disabled={isLoading}
              >
                <span
                  className={`transition-all duration-300 ${isLoading ? "opacity-0" : "opacity-100"}`}
                >
                  Create workspace
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
            <Link
              to="/login"
              className="font-semibold text-primary hover:text-primary-hover transition-colors"
            >
              Log in
            </Link>
          </p>
        </Card>
      </div>
    </div>
  );
}

export default RegisterPage;
