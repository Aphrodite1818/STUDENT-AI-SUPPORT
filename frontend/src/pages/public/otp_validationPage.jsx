import { useState, useRef, useEffect } from "react";
import { Link, useSearchParams, useNavigate } from "react-router-dom";
import Card from "../../components/ui/Card";
import Button from "../../components/ui/Button";
import logoImage from "../../assets/images/favicon.png";
import { authService } from "../../services/auth.service";

function OTPValidationPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const emailParam = searchParams.get("email");
  const purpose = searchParams.get("purpose") || "verification";
  const email = emailParam || "";

  const [otp, setOtp] = useState(["", "", "", "", "", ""]);
  const [isLoading, setIsLoading] = useState(false);
  const [isResending, setIsResending] = useState(false);
  const [error, setError] = useState(null);
  const [resendMessage, setResendMessage] = useState(null);
  const inputRefs = useRef([]);

  useEffect(() => {
    // No email in URL — nothing to verify, send them back
    if (!emailParam) {
      navigate("/register", { replace: true });
      return;
    }
    inputRefs.current[0]?.focus();
  }, [emailParam, navigate]);

  const handleChange = (index, e) => {
    const value = e.target.value;
    if (isNaN(value)) return;

    const newOtp = [...otp];

    // Handle paste into a single box
    if (value.length > 1) {
      const pastedData = value.slice(0, 6).split("");
      for (let i = 0; i < pastedData.length; i++) {
        if (index + i < 6) newOtp[index + i] = pastedData[i];
      }
      setOtp(newOtp);
      const nextEmptyIndex = newOtp.findIndex((val) => val === "");
      const focusIndex = nextEmptyIndex !== -1 ? nextEmptyIndex : 5;
      inputRefs.current[focusIndex]?.focus();
      return;
    }

    newOtp[index] = value;
    setOtp(newOtp);

    // Auto-advance to next box
    if (value !== "" && index < 5) {
      inputRefs.current[index + 1]?.focus();
    }
  };

  const handleKeyDown = (index, e) => {
    if (e.key === "Backspace" && otp[index] === "" && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const otpString = otp.join("");
    if (otpString.length < 6) {
      setError("Please enter a valid 6-digit code.");
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const result = await authService.verifyOtp(email, otpString, purpose);
if (purpose === "password_reset") {
         navigate("/forgot-password", { replace: true, state: { email, reset_token: result.reset_token } });
       } else {
        navigate("/login?verified=true", { replace: true });
      }
    } catch (err) {
      const message =
        err?.response?.data?.detail || err?.message || "Invalid OTP code.";
      setError(message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleResend = async () => {
    setError(null);
    setResendMessage(null);
    setIsResending(true);
    try {
      await authService.requestOtp(email, purpose);
      setResendMessage("A new code has been sent to your email.");
      setOtp(["", "", "", "", "", ""]);
      inputRefs.current[0]?.focus();
    } catch (err) {
      const message =
        err?.response?.data?.detail || err?.message || "Failed to resend code.";
      setError(message);
    } finally {
      setIsResending(false);
    }
  };

  return (
    <div className="min-h-screen relative flex items-center justify-center bg-background p-4 text-text py-12 overflow-hidden">
      {/* Background Animated Blobs */}
      <div className="absolute inset-0 z-0 pointer-events-none">
        <div className="absolute top-1/4 left-1/4 h-80 w-80 rounded-full bg-primary opacity-30 blur-3xl animate-blob"></div>
        <div className="absolute bottom-1/4 right-1/4 h-72 w-72 rounded-full bg-accent opacity-30 blur-3xl animate-blob animation-delay-2000"></div>
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

          <div className="text-center mb-6">
            <h1 className="text-2xl font-bold text-text">Check your email</h1>
            <p className="text-sm text-text-muted mt-2">
              We sent a 6-digit verification code to <br />
              <span className="font-semibold text-text">{email}</span>
            </p>
          </div>

          {error && (
            <div className="mb-4 p-3 bg-red-500/10 border border-red-500/50 text-red-500 rounded-md text-sm text-center animate-shake">
              {error}
            </div>
          )}

          {resendMessage && !error && (
            <div className="mb-4 p-3 bg-green-500/10 border border-green-500/50 text-green-500 rounded-md text-sm text-center">
              {resendMessage}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="flex justify-between gap-2">
              {otp.map((digit, index) => (
                <input
                  key={index}
                  ref={(el) => (inputRefs.current[index] = el)}
                  type="text"
                  inputMode="numeric"
                  maxLength={6}
                  value={digit}
                  onChange={(e) => handleChange(index, e)}
                  onKeyDown={(e) => handleKeyDown(index, e)}
                  className="w-12 h-14 text-center text-xl font-semibold bg-surface border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all duration-300 text-text"
                />
              ))}
            </div>

            <Button
              type="submit"
              className="w-full group relative overflow-hidden"
              disabled={isLoading || otp.join("").length < 6}
            >
              <span
                className={`transition-all duration-300 ${isLoading ? "opacity-0" : "opacity-100"}`}
              >
                Verify Code
              </span>
              {isLoading && (
                <span className="absolute inset-0 flex items-center justify-center">
                  <span className="h-5 w-5 rounded-full border-2 border-text-inverse border-t-transparent animate-spin"></span>
                </span>
              )}
            </Button>
          </form>

          <p className="mt-8 text-center text-sm text-text-soft">
            Didn't receive the code?{" "}
            <button
              type="button"
              className="font-semibold text-primary hover:text-primary-hover transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              disabled={isLoading || isResending || !email}
              onClick={handleResend}
            >
              {isResending ? "Sending..." : "Resend"}
            </button>
          </p>
        </Card>
      </div>
    </div>
  );
}

export default OTPValidationPage;