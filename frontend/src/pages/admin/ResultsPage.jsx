import ResourceModulePage from "../shared/ResourceModulePage";
import { getResultResourceConfig } from "../shared/resourceConfigs";

function ResultsPage() {
  return (
    <ResourceModulePage
      role="admin"
      title="Grades & Results"
      description="Enter scores, review grades, and prepare academic reporting."
      config={getResultResourceConfig({ canDelete: true })}
    />
  );
}

export default ResultsPage;
