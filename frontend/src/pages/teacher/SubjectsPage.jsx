import DashboardShell from "../shared/DashboardShell";
import ResourcePage from "../shared/ResourcePage";
import { subjectReadOnlyResourceConfig } from "../shared/resourceConfigs";

function TeacherSubjectsPage() {
  return (
    <DashboardShell
      role="teacher"
      title="Subjects"
      description="View active and inactive subjects available in the tenant catalog."
    >
      <ResourcePage config={subjectReadOnlyResourceConfig} />
    </DashboardShell>
  );
}

export default TeacherSubjectsPage;
