import { api } from "./api";
import {
  mockAttendance,
  mockClasses,
  mockExams,
  mockResults,
  page,
} from "./mockData";
import { filterItems, withMockFallback } from "./serviceFallback";

const buildQuery = (options = {}, map = {}) => {
  const params = new URLSearchParams();
  params.set("skip", String(options.skip ?? 0));
  params.set("limit", String(options.limit ?? 100));

  Object.entries(map).forEach(([optionKey, paramKey]) => {
    if (options[optionKey]) params.set(paramKey, options[optionKey]);
  });

  return params.toString();
};

export const classService = {
  getClasses: (options = {}) =>
    withMockFallback(
      () => api.get(`/classes?${buildQuery(options, { search: "search" })}`),
      () => page(filterItems(mockClasses, options.search, ["name", "level", "arm"]))
    ),

  createClass: (payload) =>
    withMockFallback(() => api.post("/classes", payload), () => ({ id: `class-${Date.now()}`, ...payload })),

  updateClass: (classId, payload) =>
    withMockFallback(() => api.patch(`/classes/${classId}`, payload), () => ({ id: classId, ...payload })),

  deleteClass: (classId) =>
    withMockFallback(() => api.delete(`/classes/${classId}`), () => ({ detail: `Class ${classId} deleted in demo mode.` })),
};

export const attendanceService = {
  getAttendance: (options = {}) =>
    withMockFallback(
      () =>
        api.get(
          `/attendance?${buildQuery(options, {
            classId: "class_id",
            studentId: "student_id",
            attendanceDate: "attendance_date",
          })}`
        ),
      () => {
        let items = [...mockAttendance];
        if (options.classId) items = items.filter((item) => item.class_id === options.classId);
        if (options.studentId) items = items.filter((item) => item.student_id === options.studentId);
        if (options.attendanceDate) items = items.filter((item) => item.attendance_date === options.attendanceDate);
        return page(items);
      }
    ),

  createAttendance: (payload) =>
    withMockFallback(() => api.post("/attendance", payload), () => ({ id: `attendance-${Date.now()}`, ...payload })),

  updateAttendance: (attendanceId, payload) =>
    withMockFallback(() => api.patch(`/attendance/${attendanceId}`, payload), () => ({ id: attendanceId, ...payload })),

  deleteAttendance: (attendanceId) =>
    withMockFallback(() => api.delete(`/attendance/${attendanceId}`), () => ({ detail: `Attendance ${attendanceId} deleted in demo mode.` })),
};

export const examService = {
  getExams: (options = {}) =>
    withMockFallback(
      () => api.get(`/exams?${buildQuery(options, { classId: "class_id", subjectId: "subject_id" })}`),
      () => {
        let items = [...mockExams];
        if (options.classId) items = items.filter((item) => item.class_id === options.classId);
        if (options.subjectId) items = items.filter((item) => item.subject_id === options.subjectId);
        return page(items);
      }
    ),

  createExam: (payload) =>
    withMockFallback(() => api.post("/exams", payload), () => ({ id: `exam-${Date.now()}`, ...payload })),

  updateExam: (examId, payload) =>
    withMockFallback(() => api.patch(`/exams/${examId}`, payload), () => ({ id: examId, ...payload })),

  deleteExam: (examId) =>
    withMockFallback(() => api.delete(`/exams/${examId}`), () => ({ detail: `Exam ${examId} deleted in demo mode.` })),
};

export const resultService = {
  getResults: (options = {}) =>
    withMockFallback(
      () =>
        api.get(
          `/results?${buildQuery(options, {
            studentId: "student_id",
            classId: "class_id",
            subjectId: "subject_id",
            term: "term",
            academicSession: "academic_session",
          })}`
        ),
      () => {
        let items = [...mockResults];
        if (options.studentId) items = items.filter((item) => item.student_id === options.studentId);
        if (options.classId) items = items.filter((item) => item.class_id === options.classId);
        if (options.subjectId) items = items.filter((item) => item.subject_id === options.subjectId);
        if (options.term) items = items.filter((item) => item.term === options.term);
        if (options.academicSession) items = items.filter((item) => item.academic_session === options.academicSession);
        return page(items);
      }
    ),

  createResult: (payload) =>
    withMockFallback(() => api.post("/results", payload), () => ({ id: `result-${Date.now()}`, ...payload })),

  updateResult: (resultId, payload) =>
    withMockFallback(() => api.patch(`/results/${resultId}`, payload), () => ({ id: resultId, ...payload })),

  deleteResult: (resultId) =>
    withMockFallback(() => api.delete(`/results/${resultId}`), () => ({ detail: `Result ${resultId} deleted in demo mode.` })),
};
