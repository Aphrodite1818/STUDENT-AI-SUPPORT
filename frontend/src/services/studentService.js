import { api } from "./api";

const buildStudentQuery = ({ skip = 0, limit = 100, search, classId, status } = {}) => {
  const params = new URLSearchParams();
  params.set("skip", String(skip));
  params.set("limit", String(limit));
  if (search) params.set("search", search);
  if (classId) params.set("class_id", classId);
  if (status) params.set("status", status);
  return params.toString();
};

export const studentService = {
  getStudents: (options = {}) =>
    api.get(`/students?${buildStudentQuery(options)}`),

  getMyStudent: () =>
    api.get("/students/me"),

  updateMyStudentProfile: (payload) =>
    api.patch("/students/me/profile", payload),

  getMyParentLinks: () =>
    api.get("/students/me/parent-links"),

  getStudent: (studentId) =>
    api.get(`/students/${studentId}`),

  updateStudent: (studentId, payload) =>
    api.patch(`/students/${studentId}`, payload),

  deleteStudent: (studentId) =>
    api.delete(`/students/${studentId}`),

  redeemLinkCode: (payload) =>
    api.post("/students/link-codes/redeem", payload),
};
