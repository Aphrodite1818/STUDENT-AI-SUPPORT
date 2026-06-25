import ResourceModulePage from "../shared/ResourceModulePage";
import { getAttendanceResourceConfig } from "../shared/resourceConfigs";

function AttendancePage() {
  return (
    <ResourceModulePage
      role="teacher"
      title="Attendance"
      description="Mark attendance for assigned classes and review daily attendance history."
      config={getAttendanceResourceConfig({ writable: true, canDelete: false, role: "teacher" })}
    />
  );
}

export default AttendancePage;
