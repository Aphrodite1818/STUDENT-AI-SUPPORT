import ResourceModulePage from "../shared/ResourceModulePage";
import { getClassResourceConfig } from "../shared/resourceConfigs";

function ClassesPage() {
  return (
    <ResourceModulePage
      role="admin"
      title="Classes"
      description="Organize classes, arms, class teachers, and academic groupings."
      config={getClassResourceConfig({ role: "admin", writable: true })}
    />
  );
}

export default ClassesPage;
