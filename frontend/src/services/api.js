
const API_URL = import.meta.env.MODE === "development" ? import.meta.env.VITE_API_URL_DEV : import.meta.env.VITE_API_URL

async function request(endpoint, options = {}) {
    const token = localStorage.getItem("token");
    
    const headers = {
        "Content-Type": "application/json",
        ...(token ? { "Authorization": `Bearer ${token}` } : {}),
        ...options.headers,
    };

    const config = {
        ...options,
        headers,
    };

    try {
        const response = await fetch(`${API_URL}${endpoint}`, config);
        const data = await response.json().catch(() => ({}));

        if (!response.ok) {
            // Check for unauthenticated error
            if (response.status === 401) {
                localStorage.removeItem("token");
                // Optionally trigger a redirect to login page here
            }
            const detail = data.detail;
            const message = Array.isArray(detail)
                ? detail.map((item) => item.msg || String(item)).join(", ")
                : (detail || data.message || "An error occurred");
            throw new Error(message);
        }

        return data;
    } catch (error) {
        console.error(`API Error on ${endpoint}:`, error);
        throw error;
    }
}

export const api = {
    get: (endpoint, options) => request(endpoint, { method: "GET", ...options }),
    post: (endpoint, body, options) => request(endpoint, { method: "POST", body: JSON.stringify(body), ...options }),
    patch: (endpoint, body, options) => request(endpoint, { method: "PATCH", body: JSON.stringify(body), ...options }),
    delete: (endpoint, options) => request(endpoint, { method: "DELETE", ...options }),
};
