import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import LandingPage from "../pages/public/LandingPage";
import LoginPage from "../pages/public/LoginPage";
import RegisterPage from "../pages/public/RegisterPage";
import OTPValidationPage from "../pages/public/otp_validationPage";
import InvitePage from "../pages/public/InvitePage";
import AdminDashboardPage from "../pages/admin/AdminDashboardPage";
function AppRoutes() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/verify-otp" element={<OTPValidationPage />} />
        <Route path="/invite" element={<InvitePage />} />
        <Route path="/admin" element={<AdminDashboardPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default AppRoutes;
