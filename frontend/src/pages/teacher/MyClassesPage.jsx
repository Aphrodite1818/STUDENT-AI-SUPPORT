import ResourceModulePage from "../shared/ResourceModulePage";
import { getClassResourceConfig } from "../shared/resourceConfigs";

function MyClassesPage() {
  return (
    <ResourceModulePage
      role="teacher"
      title="My Classes"
      description="View class groups and students assigned to your teaching schedule."
      config={getClassResourceConfig({ role: "teacher", writable: false })}
    />
  );
}

export default MyClassesPage;
