import { Navigate, Outlet, useLocation } from "react-router-dom";

export const getTokenPayload = (token) => {
  try {
    const payload = token.split(".")[1];
    const normalizedPayload = payload.replace(/-/g, "+").replace(/_/g, "/");
    return JSON.parse(atob(normalizedPayload));
  } catch {
    return null;
  }
};

export const getValidTokenPayload = () => {
  const token = localStorage.getItem("token");
  if (!token) return null;

  const payload = getTokenPayload(token);
  const expiresAt = payload?.exp ? payload.exp * 1000 : null;

  if (!payload || !expiresAt || expiresAt <= Date.now()) {
    localStorage.removeItem("token");
    return null;
  }

  return payload;
};

function ProtectedRoute() {
  const location = useLocation();
  const payload = getValidTokenPayload();

  if (!payload) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  return <Outlet />;
}

export default ProtectedRoute;
