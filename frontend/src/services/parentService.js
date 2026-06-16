import { api } from "./api";

const buildParentQuery = ({ skip = 0, limit = 100 } = {}) => {
  const params = new URLSearchParams();
  params.set("skip", String(skip));
  params.set("limit", String(limit));
  return params.toString();
};

export const parentService = {
  getParents: (options = {}) =>
    api.get(`/parents?${buildParentQuery(options)}`),

  getMyParent: () =>
    api.get("/parents/me"),

  updateMyParentProfile: (payload) =>
    api.patch("/parents/me/profile", payload),

  getMyStudents: () =>
    api.get("/parents/me/students"),

  getParent: (parentId) =>
    api.get(`/parents/${parentId}`),

  updateParent: (parentId, payload) =>
    api.patch(`/parents/${parentId}`, payload),

  deleteParent: (parentId) =>
    api.delete(`/parents/${parentId}`),
};
