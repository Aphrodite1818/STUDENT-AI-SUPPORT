import { Navigate, Outlet } from "react-router-dom";
import { getValidTokenPayload } from "./ProtectedRoute";

function RoleGuard({ allowedRoles = [] }) {
  const payload = getValidTokenPayload();
  const userRole = payload?.role?.toLowerCase();
  const normalizedRoles = allowedRoles.map((role) => role.toLowerCase());

  if (!payload) {
    return <Navigate to="/login" replace />;
  }

  if (!normalizedRoles.includes(userRole)) {
    return <Navigate to="/" replace />;
  }

  return <Outlet />;
}

export default RoleGuard;
