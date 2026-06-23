import { api } from "./api";

const buildQuery = (options = {}, map = {}) => {
  const params = new URLSearchParams();
  params.set("skip", String(options.skip ?? 0));
  params.set("limit", String(options.limit ?? 100));

  Object.entries(map).forEach(([optionKey, paramKey]) => {
    if (options[optionKey]) params.set(paramKey, options[optionKey]);
  });

  return params.toString();
};

export const financeService = {
  getFees: (options = {}) =>
    api.get(`/finance/fees?${buildQuery(options, { classId: "class_id" })}`),

  createFee: (payload) =>
    api.post("/finance/fees", payload),

  updateFee: (feeId, payload) =>
    api.patch(`/finance/fees/${feeId}`, payload),

  deleteFee: (feeId) =>
    api.delete(`/finance/fees/${feeId}`),

  getPayments: (options = {}) =>
    api.get(`/finance/payments?${buildQuery(options, { feeId: "fee_id", studentId: "student_id" })}`),

  createPayment: (payload) =>
    api.post("/finance/payments", payload),

  updatePayment: (paymentId, payload) =>
    api.patch(`/finance/payments/${paymentId}`, payload),

  deletePayment: (paymentId) =>
    api.delete(`/finance/payments/${paymentId}`),
};
