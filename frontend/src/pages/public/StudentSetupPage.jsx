import { useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { ArrowRight, CheckCircle2, TriangleAlert } from "lucide-react";
import AuthLayout from "../../components/layout/AuthLayout";
import Input from "../../components/ui/Input";
import Button from "../../components/ui/Button";
import { authService } from "../../services/auth.service";
import { parseApiError } from "../../services/api";

function Notice({ type = "success", children }) {
  const Icon = type === "error" ? TriangleAlert : CheckCircle2;
  const styles =
    type === "error"
      ? "border-error/20 bg-error-soft text-error"
      : "border-success/20 bg-success-soft text-emerald-700";

  return (
    <div className={`mb-4 flex gap-3 rounded-2xl border px-4 py-3 text-sm font-medium ${styles}`}>
      <Icon className="mt-0.5 h-4 w-4 shrink-0" />
      {children}
    </div>
  );
}

function StudentSetupPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token");

  const [formData, setFormData] = useState({
    password: "",
    confirmPassword: "",
  });
  
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [fieldErrors, setFieldErrors] = useState({});

  if (!token) {
    return (
      <AuthLayout title="Invalid Link" description="This link is missing a required setup token.">
        <Notice type="error">Please check your email and use the full link provided.</Notice>
      </AuthLayout>
    );
  }

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    setFieldErrors((prev) => ({ ...prev, [name]: undefined }));
    setError(null);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setIsLoading(true);
    setError(null);
    setFieldErrors({});

    if (formData.password !== formData.confirmPassword) {
      setFieldErrors({ confirmPassword: "Passwords do not match." });
      setIsLoading(false);
      return;
    }

    try {
      await authService.setupStudentPassword(token, formData.password);
      navigate("/login?invite=success", { replace: true });
    } catch (err) {
      const apiError = parseApiError(err, "Failed to set up student password.");
      if (Object.keys(apiError.fieldErrors || {}).length > 0) {
        setFieldErrors(apiError.fieldErrors);
      }
      setError(apiError.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AuthLayout
      title="Student Setup"
      description="Set an initial password for the student account to complete registration."
    >
      {error && <Notice type="error">{error}</Notice>}

      <form onSubmit={handleSubmit} className="space-y-5">
        <Input
          label="New Password"
          type="password"
          name="password"
          value={formData.password}
          onChange={handleChange}
          placeholder="Create a strong password"
          required
          error={fieldErrors.password}
        />
        <Input
          label="Confirm Password"
          type="password"
          name="confirmPassword"
          value={formData.confirmPassword}
          onChange={handleChange}
          placeholder="Confirm password"
          required
          error={fieldErrors.confirmPassword}
        />

        <Button type="submit" className="w-full" disabled={isLoading}>
          {isLoading ? "Saving..." : "Set Password"}
          <ArrowRight className="h-4 w-4" />
        </Button>
      </form>
    </AuthLayout>
  );
}

export default StudentSetupPage;
