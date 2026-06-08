const DEFAULT_API_URL =
    import.meta.env.MODE === "development"
        ? "http://localhost:8080/api/v1"
        : "/api/v1";

const API_URL =
    (import.meta.env.MODE === "development"
        ? import.meta.env.VITE_API_URL_DEV
        : import.meta.env.VITE_API_URL) || DEFAULT_API_URL;

const API_BASE_URL = API_URL.replace(/\/$/, "");
const TOKEN_KEY = "token";

const normalizeDetail = (detail) => {
    if (!detail) return null;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail)) {
        return detail
            .map((item) => {
                if (typeof item === "string") return item;
                if (item?.msg) return item.msg;
                if (item?.message) return item.message;
                return null;
            })
            .filter(Boolean)
            .join(", ");
    }
    if (typeof detail === "object") {
        return detail.message || detail.msg || JSON.stringify(detail);
    }
    return String(detail);
};

export const authSession = {
    getToken: () =>
        localStorage.getItem(TOKEN_KEY) || sessionStorage.getItem(TOKEN_KEY),
    setToken: (token, { remember = true } = {}) => {
        const primaryStorage = remember ? localStorage : sessionStorage;
        const secondaryStorage = remember ? sessionStorage : localStorage;

        secondaryStorage.removeItem(TOKEN_KEY);
        primaryStorage.setItem(TOKEN_KEY, token);
    },
    clearToken: () => {
        localStorage.removeItem(TOKEN_KEY);
        sessionStorage.removeItem(TOKEN_KEY);
    },
};

export const getErrorMessage = (error, fallback = "An error occurred") => {
    if (!error) return fallback;

    const responseDetail = normalizeDetail(error?.response?.data?.detail);
    if (responseDetail) return responseDetail;

    const responseMessage = normalizeDetail(error?.response?.data?.message);
    if (responseMessage) return responseMessage;

    if (typeof error?.message === "string" && error.message.trim()) {
        return error.message;
    }

    return fallback;
};

async function request(endpoint, options = {}) {
    const token = authSession.getToken();

    const headers = {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...options.headers,
    };

    const config = {
        ...options,
        headers,
    };

    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
        const data = await response.json().catch(() => ({}));

        if (!response.ok) {
            if (response.status === 401) {
                authSession.clearToken();
            }

            const error = new Error(
                getErrorMessage({ response: { data } }, "An error occurred")
            );
            error.response = {
                status: response.status,
                data,
                headers: Object.fromEntries(response.headers.entries()),
            };
            throw error;
        }

        return data;
    } catch (error) {
        console.error(`API Error on ${endpoint}:`, error);
        throw error;
    }
}

export const api = {
    get: (endpoint, options) => request(endpoint, { method: "GET", ...options }),
    post: (endpoint, body, options) =>
        request(endpoint, { method: "POST", body: JSON.stringify(body), ...options }),
    patch: (endpoint, body, options) =>
        request(endpoint, { method: "PATCH", body: JSON.stringify(body), ...options }),
    delete: (endpoint, options) =>
        request(endpoint, { method: "DELETE", ...options }),
};
