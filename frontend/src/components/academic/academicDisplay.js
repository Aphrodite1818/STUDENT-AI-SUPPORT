export const termLabels = {
  first_term: "First Term",
  second_term: "Second Term",
  third_term: "Third Term",
};

export const displayTerm = (value) => termLabels[value] || String(value || "Term").replaceAll("_", " ");

export const displayClass = (item) =>
  [item?.name, item?.arm].filter(Boolean).join(" ") || "Class";

export const displayPerson = (item) =>
  [item?.first_name, item?.last_name].filter(Boolean).join(" ") ||
  item?.full_name ||
  item?.name ||
  item?.staff_id ||
  item?.admission_number ||
  "Unnamed";
