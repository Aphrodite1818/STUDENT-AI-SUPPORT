import DashboardLayout from "../../components/layout/DashboardLayout";
import ResourcePage from "./ResourcePage";

function ResourceModulePage({
  role,
  title,
  description,
  config,
  actions,
}) {
  return (
    <DashboardLayout role={role} title={title} description={description} actions={actions}>
      <ResourcePage config={config} />
    </DashboardLayout>
  );
}

export default ResourceModulePage;
