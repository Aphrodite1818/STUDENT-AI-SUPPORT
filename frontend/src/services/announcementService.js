import { api } from "./api";
import { withMockFallback } from "./serviceFallback";

const mockAnnouncements = [
  { id: "notice-1", title: "Parent-Teacher Meeting", category: "Important", audience: "Parents", status: "published", date: "2026-06-18" },
  { id: "notice-2", title: "Annual Sports Day", category: "General", audience: "All school", status: "draft", date: "2026-06-24" },
  { id: "notice-3", title: "Unit Test Schedule", category: "Academic", audience: "Students", status: "published", date: "2026-06-20" },
];

export const announcementService = {
  getAnnouncements: () =>
    withMockFallback(
      () => api.get("/announcements"),
      () => ({ items: mockAnnouncements, total: mockAnnouncements.length })
    ),

  createAnnouncement: (payload) =>
    withMockFallback(
      () => api.post("/announcements", payload),
      () => ({ id: `notice-${Date.now()}`, status: "draft", ...payload })
    ),
};
