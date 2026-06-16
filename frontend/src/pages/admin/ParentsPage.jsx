import ResourceModulePage from "../shared/ResourceModulePage";
import { parentResourceConfig } from "../shared/resourceConfigs";

function ParentsPage() {
  return (
    <ResourceModulePage
      role="admin"
      title="Parent Directory"
      description="Review invited parent profiles and maintain optional contact details."
      config={parentResourceConfig}
    />
  );
}

export default ParentsPage;
