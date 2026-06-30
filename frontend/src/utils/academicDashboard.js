export const EMPTY_TEXT = "-";

export const cleanText = (value, fallback = EMPTY_TEXT) => {
  if (value === undefined || value === null || value === "") return fallback;
  return String(value).replace(/_/g, " ");
};

export const formatChartLabel = (value, fallback = "Unknown") => {
  const normalized = cleanText(value, fallback);
  return normalized
    .split(/\s+/)
    .filter(Boolean)
    .map((word) => {
      if (word === word.toUpperCase()) return word;
      if (word === word.toLowerCase()) return word.charAt(0).toUpperCase() + word.slice(1);
      return word;
    })
    .join(" ");
};

export const asItems = (response) => response?.items || [];

export const averageScore = (items, key = "total_score") => {
  const scores = (Array.isArray(items) ? items : [])
    .map((item) => Number(item?.[key]))
    .filter((value) => Number.isFinite(value));
  if (scores.length === 0) return 0;
  return Math.round(scores.reduce((sum, value) => sum + value, 0) / scores.length);
};

export const chartFromCounts = (items, key, fallbackLabel = "unknown") => {
  const counts = (Array.isArray(items) ? items : []).reduce((groups, item) => {
    const label = cleanText(item?.[key], fallbackLabel);
    groups[label] = (groups[label] || 0) + 1;
    return groups;
  }, {});
  return Object.entries(counts).map(([label, value]) => ({ label, value }));
};

export const subjectPerformanceChart = (results) =>
  (Array.isArray(results) ? results : []).map((item) => ({
    label: item.subject_code || item.subject_name || "Subject",
    value: Number(item.total_score || 0),
  }));

export const averageBy = (items, labelGetter, valueKey = "total_score") => {
  const groups = {};
  (Array.isArray(items) ? items : []).forEach((item) => {
    const label = labelGetter(item) || "Unknown";
    const value = Number(item?.[valueKey]);
    if (!Number.isFinite(value)) return;
    if (!groups[label]) groups[label] = { total: 0, count: 0 };
    groups[label].total += value;
    groups[label].count += 1;
  });
  return Object.entries(groups).map(([label, group]) => ({
    label,
    value: Math.round(group.total / group.count),
  }));
};

export const reportCardStatusChart = (cards) => chartFromCounts(cards, "status", "not generated");

export const bestAndWeakestSubject = (results) => {
  const scored = (Array.isArray(results) ? results : [])
    .map((item) => ({
      label: item.subject_name || item.subject_code || "Subject",
      value: Number(item.total_score),
    }))
    .filter((item) => Number.isFinite(item.value));
  if (scored.length === 0) return { best: null, weakest: null };
  const sorted = [...scored].sort((a, b) => b.value - a.value);
  return { best: sorted[0], weakest: sorted[sorted.length - 1] };
};

export const completionPercent = (completed, total) => {
  const safeTotal = Number(total) || 0;
  if (safeTotal <= 0) return 0;
  return Math.round((Number(completed || 0) / safeTotal) * 100);
};
