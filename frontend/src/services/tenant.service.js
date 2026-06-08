import { api } from "./api";

export const tenantService = {
    // Public register endpoint
    registerTenant: (data) => api.post("/tenants/register", data),
    
    // Superadmin endpoints
    createTenant: (data) => api.post("/tenants", data),
    getAllTenants: (skip = 0, limit = 50) => api.get(`/tenants?skip=${skip}&limit=${limit}`),
    
    // Admin / Superadmin endpoints
    getTenant: (tenantId) => api.get(`/tenants/${tenantId}`),
    updateTenant: (tenantId, data) => api.patch(`/tenants/${tenantId}`, data),
    
    // Superadmin specific updates
    updateTenantStatus: (tenantId, statusData) => api.patch(`/tenants/${tenantId}/status`, statusData),
    deleteTenant: (tenantId) => api.delete(`/tenants/${tenantId}`),
    restoreTenant: (tenantId) => api.patch(`/tenants/${tenantId}/restore`, {})
};
