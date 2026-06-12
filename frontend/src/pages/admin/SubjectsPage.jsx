import ResourceModulePage from "../shared/ResourceModulePage";
import { subjectResourceConfig } from "../shared/resourceConfigs";

function SubjectsPage() {
  return (
    <ResourceModulePage
      role="admin"
      title="Subjects"
      description="Maintain the subject catalog used by classes, teachers, exams, and results."
      config={subjectResourceConfig}
    />
  );
}

export default SubjectsPage;
