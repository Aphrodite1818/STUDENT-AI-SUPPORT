import { api } from "./api";

export const tenantService = {
    registerTenant: (data) => api.post("/tenants/register", data, { auth: false }),

    getTenant: (tenantId) => api.get(`/tenants/${tenantId}`),
    updateTenant: (tenantId, data) => api.patch(`/tenants/${tenantId}`, data),
};
