import DashboardLayout from "../../components/layout/DashboardLayout";
import StatCard from "../../components/shared/StatCard";

function DashboardShell(props) {
  return <DashboardLayout {...props} />;
}

export function DashboardStat({ label, value, hint, icon }) {
  return (
    <StatCard
      label={label}
      value={value}
      description={hint}
      icon={icon}
      compact
    />
  );
}

export default DashboardShell;
