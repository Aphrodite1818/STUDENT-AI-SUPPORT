import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import LandingPage from "../pages/public/LandingPage";
import LoginPage from "../pages/public/LoginPage";
import RegisterPage from "../pages/public/RegisterPage";
import OTPValidationPage from "../pages/public/otp_validationPage";
import InvitePage from "../pages/public/InvitePage";
import ForgotPasswordPage from "../pages/public/ForgotPasswordPage";
import AdminDashboardPage from "../pages/admin/AdminDashboardPage";
import UserManagementPage from "../pages/admin/UserManagementPage";
import TeacherDashboardPage from "../pages/teacher/TeacherDashboardPage";
import StudentDashboardPage from "../pages/student/StudentDashboardPage";
import ParentDashboardPage from "../pages/parent/ParentDashboardPage";
import SuperadminDashboardPage from "../pages/superadmin/SuperadminDashboardPage";
import ProtectedRoute from "./ProtectedRoute";
import RoleGuard from "./RoleGuard";

function AppRoutes() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/verify-otp" element={<OTPValidationPage />} />
        <Route path="/invite" element={<InvitePage />} />
        <Route path="/forgot-password" element={<ForgotPasswordPage />} />
        <Route element={<ProtectedRoute />}>
          <Route element={<RoleGuard allowedRoles={["admin"]} />}>
            <Route path="/admin/dashboard" element={<AdminDashboardPage />} />
            <Route path="/admin/users" element={<UserManagementPage />} />
          </Route>
          <Route element={<RoleGuard allowedRoles={["teacher"]} />}>
            <Route path="/teacher/dashboard" element={<TeacherDashboardPage />} />
          </Route>
          <Route element={<RoleGuard allowedRoles={["student"]} />}>
            <Route path="/student/dashboard" element={<StudentDashboardPage />} />
          </Route>
          <Route element={<RoleGuard allowedRoles={["parent"]} />}>
            <Route path="/parent/dashboard" element={<ParentDashboardPage />} />
          </Route>
          <Route element={<RoleGuard allowedRoles={["superadmin"]} />}>
            <Route path="/superadmin/dashboard" element={<SuperadminDashboardPage />} />
          </Route>
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default AppRoutes;
