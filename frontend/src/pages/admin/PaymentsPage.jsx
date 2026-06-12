import ResourceModulePage from "../shared/ResourceModulePage";
import { paymentResourceConfig } from "../shared/resourceConfigs";

function PaymentsPage() {
  return (
    <ResourceModulePage
      role="admin"
      title="Payments"
      description="Record and track fee payments with clear status visibility."
      config={paymentResourceConfig}
    />
  );
}

export default PaymentsPage;
