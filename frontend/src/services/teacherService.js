import { api } from "./api";
import { mockTeachers, page } from "./mockData";
import { filterItems, withMockFallback } from "./serviceFallback";

const buildTeacherQuery = ({ skip = 0, limit = 100, search } = {}) => {
  const params = new URLSearchParams();
  params.set("skip", String(skip));
  params.set("limit", String(limit));
  if (search) params.set("search", search);
  return params.toString();
};

export const teacherService = {
  getTeachers: (options = {}) =>
    withMockFallback(
      () => api.get(`/teachers?${buildTeacherQuery(options)}`),
      () => page(filterItems(mockTeachers, options.search, ["staff_id", "qualification", "specialization"]))
    ),

  getTeacher: (teacherId) =>
    withMockFallback(
      () => api.get(`/teachers/${teacherId}`),
      () => mockTeachers.find((teacher) => teacher.id === teacherId) || null
    ),

  updateTeacher: (teacherId, payload) =>
    withMockFallback(
      () => api.patch(`/teachers/${teacherId}`, payload),
      () => ({ id: teacherId, ...payload })
    ),

  deleteTeacher: (teacherId) =>
    withMockFallback(
      () => api.delete(`/teachers/${teacherId}`),
      () => ({ detail: `Teacher ${teacherId} archived in demo mode.` })
    ),
};
