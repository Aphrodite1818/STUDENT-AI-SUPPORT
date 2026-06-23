import { api } from "./api";

export const dashboardService = {
  getTenantAdminAnalytics: () =>
    api.get("/tenant-admin/analytics/overview"),

  getSuperadminAnalytics: () =>
    api.get("/superadmin/analytics/overview"),
};
