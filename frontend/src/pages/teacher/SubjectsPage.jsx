import ResourceModulePage from "../shared/ResourceModulePage";
import { teacherSubjectResourceConfig } from "../shared/resourceConfigs";

function SubjectsPage() {
  return (
    <ResourceModulePage
      role="teacher"
      title="Subjects"
      description="Browse the subjects currently assigned to you."
      config={teacherSubjectResourceConfig}
    />
  );
}

export default SubjectsPage;
