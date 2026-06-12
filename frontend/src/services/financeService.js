import { api } from "./api";
import { mockFees, mockPayments, page } from "./mockData";
import { withMockFallback } from "./serviceFallback";

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
    withMockFallback(
      () => api.get(`/finance/fees?${buildQuery(options, { classId: "class_id" })}`),
      () => {
        const items = options.classId
          ? mockFees.filter((fee) => fee.class_id === options.classId)
          : mockFees;
        return page(items);
      }
    ),

  createFee: (payload) =>
    withMockFallback(() => api.post("/finance/fees", payload), () => ({ id: `fee-${Date.now()}`, ...payload })),

  updateFee: (feeId, payload) =>
    withMockFallback(() => api.patch(`/finance/fees/${feeId}`, payload), () => ({ id: feeId, ...payload })),

  deleteFee: (feeId) =>
    withMockFallback(() => api.delete(`/finance/fees/${feeId}`), () => ({ detail: `Fee ${feeId} deleted in demo mode.` })),

  getPayments: (options = {}) =>
    withMockFallback(
      () => api.get(`/finance/payments?${buildQuery(options, { studentId: "student_id", feeId: "fee_id" })}`),
      () => {
        let items = [...mockPayments];
        if (options.studentId) items = items.filter((payment) => payment.student_id === options.studentId);
        if (options.feeId) items = items.filter((payment) => payment.fee_id === options.feeId);
        return page(items);
      }
    ),

  createPayment: (payload) =>
    withMockFallback(() => api.post("/finance/payments", payload), () => ({ id: `payment-${Date.now()}`, ...payload })),

  updatePayment: (paymentId, payload) =>
    withMockFallback(() => api.patch(`/finance/payments/${paymentId}`, payload), () => ({ id: paymentId, ...payload })),

  deletePayment: (paymentId) =>
    withMockFallback(() => api.delete(`/finance/payments/${paymentId}`), () => ({ detail: `Payment ${paymentId} deleted in demo mode.` })),
};
