import { api } from "./api";

export const searchService = {
  searchTenant: (query, limit = 20) =>
    api.get(
      `/tenant-admin/search?q=${encodeURIComponent(query)}&limit=${encodeURIComponent(limit)}`
    ),
};

export default searchService;
