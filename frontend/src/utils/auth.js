import { authSession } from "../services/api";

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
  const token = authSession.getToken();
  if (!token) return null;

  const payload = getTokenPayload(token);
  const expiresAt = payload?.exp ? payload.exp * 1000 : null;

  if (!payload || !expiresAt || expiresAt <= Date.now()) {
    authSession.clearToken();
    return null;
  }

  return payload;
};
