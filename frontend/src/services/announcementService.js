import { api } from "./api";

export const announcementService = {
  getAnnouncements: () => api.get("/announcements"),

  createAnnouncement: (payload) =>
    api.post("/announcements", payload),
};
