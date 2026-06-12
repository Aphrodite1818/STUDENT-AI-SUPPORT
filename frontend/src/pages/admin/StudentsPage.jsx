import ResourceModulePage from "../shared/ResourceModulePage";
import { getStudentResourceConfig } from "../shared/resourceConfigs";

function StudentsPage() {
  return (
    <ResourceModulePage
      role="admin"
      title="Student Directory"
      description="Search, filter, sort, and maintain student records across classes."
      config={getStudentResourceConfig({ writable: true })}
    />
  );
}

export default StudentsPage;
