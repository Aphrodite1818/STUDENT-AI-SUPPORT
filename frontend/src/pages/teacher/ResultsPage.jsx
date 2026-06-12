import ResourceModulePage from "../shared/ResourceModulePage";
import { getResultResourceConfig } from "../shared/resourceConfigs";

function ResultsPage() {
  return (
    <ResourceModulePage
      role="teacher"
      title="Results"
      description="Enter scores and review performance for your assigned classes."
      config={getResultResourceConfig({ canDelete: false })}
    />
  );
}

export default ResultsPage;
