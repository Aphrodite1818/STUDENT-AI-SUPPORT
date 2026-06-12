import ResourceModulePage from "../shared/ResourceModulePage";
import { getStudentResourceConfig } from "../shared/resourceConfigs";

function StudentsPage() {
  return (
    <ResourceModulePage
      role="teacher"
      title="Students"
      description="Review student records for classes assigned to you."
      config={getStudentResourceConfig({ writable: false })}
    />
  );
}

export default StudentsPage;
