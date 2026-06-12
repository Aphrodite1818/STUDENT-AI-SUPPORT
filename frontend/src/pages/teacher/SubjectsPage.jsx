import ResourceModulePage from "../shared/ResourceModulePage";
import { subjectReadOnlyResourceConfig } from "../shared/resourceConfigs";

function SubjectsPage() {
  return (
    <ResourceModulePage
      role="teacher"
      title="Subjects"
      description="Browse the subjects available in your school workspace."
      config={subjectReadOnlyResourceConfig}
    />
  );
}

export default SubjectsPage;
