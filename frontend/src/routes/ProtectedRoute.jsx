import { Navigate, Outlet, useLocation } from "react-router-dom";
import { getValidTokenPayload } from "../utils/auth";

function ProtectedRoute() {
  const location = useLocation();
  const payload = getValidTokenPayload();

  if (!payload) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  return <Outlet />;
}

export default ProtectedRoute;
