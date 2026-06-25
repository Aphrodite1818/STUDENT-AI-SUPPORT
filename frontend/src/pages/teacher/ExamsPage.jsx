import ResourceModulePage from "../shared/ResourceModulePage";
import { getExamResourceConfig } from "../shared/resourceConfigs";

function ExamsPage() {
  return (
    <ResourceModulePage
      role="teacher"
      title="Exams"
      description="Schedule and update assessments for your assigned subjects."
      config={getExamResourceConfig({ canDelete: false, role: "teacher" })}
    />
  );
}

export default ExamsPage;
