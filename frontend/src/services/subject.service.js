import { api } from "./api";

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
    api.get(`/subjects?${buildSubjectQuery(options)}`),

  getSubject: (subjectId) =>
    api.get(`/subjects/${subjectId}`),

  createSubject: (data) =>
    api.post("/subjects", data),

  updateSubject: (subjectId, data) =>
    api.patch(`/subjects/${subjectId}`, data),

  activateSubject: (subjectId) =>
    api.patch(`/subjects/${subjectId}/activate`),

  deactivateSubject: (subjectId) =>
    api.patch(`/subjects/${subjectId}/deactivate`),

  deleteSubject: (subjectId) =>
    api.delete(`/subjects/${subjectId}`),
};
