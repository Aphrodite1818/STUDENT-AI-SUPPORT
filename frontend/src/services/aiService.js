import { api } from "./api";
import { withMockFallback } from "./serviceFallback";

const mockMetrics = {
  responseQuality: 94,
  automatedReplies: 1284,
  escalations: 18,
  failedResponses: [
    { id: "fail-1", topic: "Fee balance", reason: "Missing payment record", count: 4 },
    { id: "fail-2", topic: "Transport route", reason: "Route data unavailable", count: 2 },
  ],
  topics: [
    { name: "Attendance", value: 34 },
    { name: "Assignments", value: 28 },
    { name: "Fees", value: 18 },
    { name: "Notices", value: 20 },
  ],
};

export const aiService = {
  getMetrics: () =>
    withMockFallback(
      () => api.get("/ai/metrics"),
      () => mockMetrics
    ),
};
