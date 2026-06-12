import ResourceModulePage from "../shared/ResourceModulePage";
import { teacherResourceConfig } from "../shared/resourceConfigs";

function TeachersPage() {
  return (
    <ResourceModulePage
      role="admin"
      title="Teacher Directory"
      description="Manage teacher profiles, qualifications, specializations, and class assignments."
      config={teacherResourceConfig}
    />
  );
}

export default TeachersPage;
