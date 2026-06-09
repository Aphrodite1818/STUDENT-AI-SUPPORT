import { api } from "./api";

export const userService = {
    // Current user
    getMe: () => api.get("/users/get-authenticated-user"),
    
    // General user endpoints
    inviteUser: (data) => api.post("/users/user-create", data),
    registerUser: (data) => api.post("/users/user-create", data),
    getUsers: (skip = 0, limit = 100) => api.get(`/users?skip=${skip}&limit=${limit}`),
    getUser: (userId) => api.get(`/users/${userId}`),
    resendInvite: (userId) => api.post(`/users/${userId}/resend-invite`, {}),
    
    // Updates
    updateProfile: (userId, data) => api.patch(`/users/${userId}`, data),
    updateAdminStatus: (userId, data) => api.patch(`/users/${userId}/admin`, data),
    
    // Delete
    deleteUser: (userId) => api.delete(`/users/${userId}`)
};
