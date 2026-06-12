import ResourceModulePage from "../shared/ResourceModulePage";
import { getAttendanceResourceConfig } from "../shared/resourceConfigs";

function AttendancePage() {
  return (
    <ResourceModulePage
      role="admin"
      title="Attendance"
      description="Mark, review, and audit daily student attendance by class and date."
      config={getAttendanceResourceConfig({ writable: true, canDelete: true })}
    />
  );
}

export default AttendancePage;
