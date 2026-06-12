import ResourceModulePage from "../shared/ResourceModulePage";
import { getExamResourceConfig } from "../shared/resourceConfigs";

function ExamsPage() {
  return (
    <ResourceModulePage
      role="admin"
      title="Exams"
      description="Schedule assessments and maintain exam metadata for classes and subjects."
      config={getExamResourceConfig({ canDelete: true })}
    />
  );
}

export default ExamsPage;
