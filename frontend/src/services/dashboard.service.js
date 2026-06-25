import { api } from "./api";

export const dashboardService = {
  getTenantAdminAnalytics: () =>
    api.get("/metrics/tenant-admin/dashboard"),

  getSuperadminAnalytics: () =>
    api.get("/metrics/superadmin/dashboard"),

  getTeacherAnalytics: () =>
    api.get("/metrics/teacher/dashboard"),

  getParentAnalytics: () =>
    api.get("/metrics/parent/dashboard"),

  getStudentAnalytics: () =>
    api.get("/metrics/student/dashboard"),
};
