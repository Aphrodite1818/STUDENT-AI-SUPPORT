import { api } from "./api";

export const aiService = {
  getMetrics: () => api.get("/ai/metrics"),
};
