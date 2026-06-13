import { api } from "./api";

const emptyOverview = {
  stats: [],
  sections: [],
};

const getListCount = async (endpoint) => {
  const result = await api.get(endpoint);

  if (Number.isFinite(result?.total)) return result.total;
  if (Array.isArray(result?.items)) return result.items.length;
  if (Array.isArray(result)) return result.length;

  return 0;
};

const settleCount = async (endpoint) => {
  try {
    return await getListCount(endpoint);
  } catch {
    return null;
  }
};

export const dashboardService = {
  getAdminOverview: async () => {
    const [users, teachers, subjects] = await Promise.all([
      settleCount("/users?skip=0&limit=100"),
      settleCount("/teachers?skip=0&limit=100"),
      settleCount("/subjects?skip=0&limit=100"),
    ]);

    return {
      stats: [
        users !== null && {
          label: "Users",
          value: users,
          description: "tenant accounts",
          tone: "primary",
        },
        teachers !== null && {
          label: "Teachers",
          value: teachers,
          description: "teacher profiles",
          tone: "success",
        },
        subjects !== null && {
          label: "Subjects",
          value: subjects,
          description: "academic catalog",
          tone: "accent",
        },
      ].filter(Boolean),
      sections: [],
    };
  },

  getTeacherOverview: async () => emptyOverview,

  getStudentOverview: async () => emptyOverview,

  getParentOverview: async () => emptyOverview,
};
