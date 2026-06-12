import { api } from "./api";
import { mockStudents, page } from "./mockData";
import { filterItems, withMockFallback } from "./serviceFallback";

const buildStudentQuery = ({ skip = 0, limit = 100, search, classId, status } = {}) => {
  const params = new URLSearchParams();
  params.set("skip", String(skip));
  params.set("limit", String(limit));
  if (search) params.set("search", search);
  if (classId) params.set("class_id", classId);
  if (status) params.set("status", status);
  return params.toString();
};

const filterStudents = (options = {}) => {
  let items = filterItems(mockStudents, options.search, ["firstname", "lastname", "admission_number"]);
  if (options.classId) items = items.filter((student) => student.class_id === options.classId);
  if (options.status) items = items.filter((student) => student.status === options.status);
  return page(items);
};

export const studentService = {
  getStudents: (options = {}) =>
    withMockFallback(
      () => api.get(`/students?${buildStudentQuery(options)}`),
      () => filterStudents(options)
    ),

  getStudent: (studentId) =>
    withMockFallback(
      () => api.get(`/students/${studentId}`),
      () => mockStudents.find((student) => student.id === studentId) || null
    ),

  createStudent: (payload) =>
    withMockFallback(
      () => api.post("/students", payload),
      () => ({ id: `student-${Date.now()}`, ...payload })
    ),

  updateStudent: (studentId, payload) =>
    withMockFallback(
      () => api.patch(`/students/${studentId}`, payload),
      () => ({ id: studentId, ...payload })
    ),

  updateAcademicStatus: (studentId, payload) =>
    withMockFallback(
      () => api.patch(`/students/${studentId}/academic-status`, payload),
      () => ({ id: studentId, ...payload })
    ),

  deleteStudent: (studentId) =>
    withMockFallback(
      () => api.delete(`/students/${studentId}`),
      () => ({ detail: `Student ${studentId} deleted in demo mode.` })
    ),
};
