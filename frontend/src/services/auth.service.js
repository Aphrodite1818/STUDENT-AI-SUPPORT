import { api, authSession } from "./api";

const PENDING_VERIFICATION_EMAIL_KEY = "pendingVerificationEmail";

export const authService = {
    login: async (email, password, { remember = true } = {}) => {
        const response = await api.post("/auth/login", { email, password });
        if (response.access_token) {
            authSession.setToken(response.access_token, { remember });
        }
        return response;
    },
    
    requestOtp: (email, purpose) => 
        api.post("/auth/request-otp", { email, purpose }),
        
    verifyOtp: (email, code, purpose) => 
        api.post("/auth/verify-otp", { email, code, purpose }),

    activateTenant: (email, password, token) =>
        api.post("/auth/activate-tenant", { email, password, token }),

    getInviteStatus: (token) =>
        api.get(`/auth/invite-status?token=${encodeURIComponent(token)}`),

    acceptInvite: (email, password, token) =>
        api.post("/auth/accept-invite", { email, password, token }),
        
    resetPassword: (email, reset_token, new_password) => 
        api.post("/auth/reset-password", { email, reset_token, new_password }),

    setPendingVerificationEmail: (email) => {
        sessionStorage.setItem(PENDING_VERIFICATION_EMAIL_KEY, email);
    },

    clearPendingVerificationEmail: () => {
        sessionStorage.removeItem(PENDING_VERIFICATION_EMAIL_KEY);
    },
        
    logout: () => {
        authSession.clearToken();
    }
};
