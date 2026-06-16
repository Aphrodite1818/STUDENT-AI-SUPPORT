import { api, authSession } from "./api";
import { userService } from "./user.service";

const PENDING_VERIFICATION_EMAIL_KEY = "pendingVerificationEmail";

export const authService = {
    login: async (email, password, { remember = true } = {}) => {
        const response = await api.post(
            "/auth/login",
            { email, password },
            { auth: false }
        );

        if (response.access_token) {
            authSession.setToken(response.access_token, { remember });
        }

        let currentUser = response.user || null;
        let role = response.role || currentUser?.role || null;

        if (response.access_token) {
            try {
                currentUser = await userService.getMe();
                role = currentUser?.role || null;
            } catch (error) {
                console.error("Failed to fetch authenticated user after login:", error);
            }
        }

        if (currentUser) {
            authSession.setUser(currentUser, { remember });
        } else if (role) {
            authSession.setRole(role, { remember });
        }

        return {
            ...response,
            role,
            user: currentUser,
        };
    },
    
    requestOtp: (email, purpose) => 
        api.post("/auth/request-otp", { email, purpose }, { auth: false }),
        
    verifyOtp: (email, code, purpose) => 
        api.post("/auth/verify-otp", { email, code, purpose }, { auth: false }),

    activateTenant: (email, password, token) =>
        api.post(
            "/auth/activate-tenant",
            { email, password, token },
            { auth: false }
        ),

    getInviteStatus: (token) =>
        api.get(`/auth/invite-status?token=${encodeURIComponent(token)}`, {
            auth: false,
        }),

    acceptInvite: (email, password, token) =>
        api.post(
            "/auth/accept-invite",
            { email, password, token },
            { auth: false }
        ),
        
    resetPassword: (email, reset_token, new_password) => 
        api.post(
            "/auth/reset-password",
            { email, reset_token, new_password },
            { auth: false }
        ),

    setPendingVerificationEmail: (email) => {
        sessionStorage.setItem(PENDING_VERIFICATION_EMAIL_KEY, email);
    },

    getPendingVerificationEmail: () =>
        sessionStorage.getItem(PENDING_VERIFICATION_EMAIL_KEY),

    clearPendingVerificationEmail: () => {
        sessionStorage.removeItem(PENDING_VERIFICATION_EMAIL_KEY);
    },
        
    logout: () => {
        authSession.clear();
    }
};
