export const isMockableApiError = (error) => {
  const status = error?.response?.status;
  return !error?.response || status === 404 || status === 405 || status === 501;
};

export const withMockFallback = async (request, fallback) => {
  try {
    return await request();
  } catch (error) {
    if (isMockableApiError(error)) {
      return typeof fallback === "function" ? fallback() : fallback;
    }

    throw error;
  }
};

export const filterItems = (items, search, fields = []) => {
  const query = String(search || "").trim().toLowerCase();
  if (!query) return items;

  return items.filter((item) =>
    fields.some((field) => String(item[field] || "").toLowerCase().includes(query))
  );
};
