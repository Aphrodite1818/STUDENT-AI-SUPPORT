import { api } from "./api";

const buildParentQuery = ({ skip = 0, limit = 100 } = {}) => {
  const params = new URLSearchParams();
  params.set("skip", String(skip));
  params.set("limit", String(limit));
  return params.toString();
};

export const parentService = {
  getParents: (options = {}) =>
    api.get(`/tenant-admin/parents?${buildParentQuery(options)}`),

  createParent: (payload) =>
    api.post("/tenant-admin/parents", payload),

  getMyParent: () =>
    api.get("/parents/me"),

  updateMyParentProfile: (payload) =>
    api.patch("/parents/me/profile", payload),

  getMyStudents: () =>
    api.get("/parents/me/students"),

  createStudentLinkRequest: (payload) =>
    api.post("/parents/me/student-link-requests", payload),

  getMyStudentLinkRequests: () =>
    api.get("/parents/me/student-link-requests"),

  getParent: (parentId) =>
    api.get(`/tenant-admin/parents/${parentId}`),

  updateParent: (parentId, payload) =>
    api.patch(`/tenant-admin/parents/${parentId}`, payload),

  deleteParent: (parentId) =>
    api.delete(`/tenant-admin/parents/${parentId}`),
};
