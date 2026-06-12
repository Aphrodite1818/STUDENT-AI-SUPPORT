import { api } from "./api";
import { mockSubjects, page } from "./mockData";
import { filterItems, withMockFallback } from "./serviceFallback";

const buildSubjectQuery = ({
  skip = 0,
  limit = 100,
  isActive,
  search,
} = {}) => {
  const params = new URLSearchParams();

  params.set("skip", String(skip));
  params.set("limit", String(limit));

  if (typeof isActive === "boolean") {
    params.set("is_active", String(isActive));
  }

  if (search) {
    params.set("search", search);
  }

  return params.toString();
};

export const subjectService = {
  getSubjects: (options = {}) =>
    withMockFallback(
      () => api.get(`/subjects?${buildSubjectQuery(options)}`),
      () => {
        let items = filterItems(mockSubjects, options.search, ["name", "code", "description"]);
        if (typeof options.isActive === "boolean") {
          items = items.filter((subject) => subject.is_active === options.isActive);
        }
        return page(items);
      }
    ),

  getSubject: (subjectId) =>
    withMockFallback(
      () => api.get(`/subjects/${subjectId}`),
      () => mockSubjects.find((subject) => subject.id === subjectId) || null
    ),

  createSubject: (data) =>
    withMockFallback(() => api.post("/subjects", data), () => ({ id: `subject-${Date.now()}`, is_active: true, ...data })),

  updateSubject: (subjectId, data) =>
    withMockFallback(() => api.patch(`/subjects/${subjectId}`, data), () => ({ id: subjectId, ...data })),

  activateSubject: (subjectId) =>
    withMockFallback(() => api.patch(`/subjects/${subjectId}/activate`), () => ({ id: subjectId, is_active: true })),

  deactivateSubject: (subjectId) =>
    withMockFallback(() => api.patch(`/subjects/${subjectId}/deactivate`), () => ({ id: subjectId, is_active: false })),

  deleteSubject: (subjectId) =>
    withMockFallback(() => api.delete(`/subjects/${subjectId}`), () => ({ detail: `Subject ${subjectId} deleted in demo mode.` })),
};
