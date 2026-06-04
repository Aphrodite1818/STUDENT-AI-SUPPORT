import { api } from "./api";

export const authService = {
    login: async (email, password) => {
        const response = await api.post("/auth/login", { email, password });
        if (response.access_token) {
            localStorage.setItem("token", response.access_token);
        }
        return response;
    },
    
    requestOtp: (email, purpose) => 
        api.post("/auth/request-otp", { email, purpose }),
        
    verifyOtp: (email, code, purpose) => 
        api.post("/auth/verify-otp", { email, code, purpose }),
        
    resetPassword: (email, reset_token, new_password) => 
        api.post("/auth/reset-password", { email, reset_token, new_password }),
        
    logout: () => {
        localStorage.removeItem("token");
    }
};
