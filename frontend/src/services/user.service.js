import { api } from "./api";

export const userService = {
    // Current user
    getMe: () => api.get("/users/me"),
    
    // General user endpoints
    registerUser: (data) => api.post("/users", data),
    getUsers: (skip = 0, limit = 100) => api.get(`/users?skip=${skip}&limit=${limit}`),
    getUser: (userId) => api.get(`/users/${userId}`),
    
    // Updates
    updateProfile: (userId, data) => api.patch(`/users/${userId}`, data),
    updateAdminStatus: (userId, data) => api.patch(`/users/${userId}/admin`, data),
    
    // Delete
    deleteUser: (userId) => api.delete(`/users/${userId}`)
};
