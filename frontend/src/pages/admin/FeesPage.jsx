import ResourceModulePage from "../shared/ResourceModulePage";
import { feeResourceConfig } from "../shared/resourceConfigs";

function FeesPage() {
  return (
    <ResourceModulePage
      role="admin"
      title="Fees"
      description="Configure fee items, due dates, and class-specific billing."
      config={feeResourceConfig}
    />
  );
}

export default FeesPage;
