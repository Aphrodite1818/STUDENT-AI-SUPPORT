import { api } from "./api";

const buildTeacherQuery = ({ skip = 0, limit = 100, search } = {}) => {
  const params = new URLSearchParams();
  params.set("skip", String(skip));
  params.set("limit", String(limit));
  if (search) params.set("search", search);
  return params.toString();
};

export const teacherService = {
  getTeachers: (options = {}) =>
    api.get(`/tenant-admin/teachers?${buildTeacherQuery(options)}`),

  createTeacher: (payload) =>
    api.post("/tenant-admin/teachers", payload),

  getMyTeacher: () =>
    api.get("/teachers/me"),

  getMySubjects: (options = {}) =>
    api.get(
      `/teachers/me/subjects?${new URLSearchParams({
        skip: String(options.skip ?? 0),
        limit: String(options.limit ?? 100),
        ...(options.search ? { search: options.search } : {}),
        ...(typeof options.isActive === "boolean"
          ? { is_active: String(options.isActive) }
          : {}),
      }).toString()}`
    ),

  getTeacher: (teacherId) =>
    api.get(`/tenant-admin/teachers/${teacherId}`),

  updateTeacher: (teacherId, payload) =>
    api.patch(`/tenant-admin/teachers/${teacherId}`, payload),

  updateMyTeacherProfile: (payload) =>
    api.patch("/teachers/me/profile", payload),

  deleteTeacher: (teacherId) =>
    api.delete(`/tenant-admin/teachers/${teacherId}`),
};
