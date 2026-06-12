export const dashboardService = {
  getAdminOverview: async () => ({
    stats: [
      { label: "Total Students", value: "1,248", change: "+12%", description: "vs last month", tone: "primary" },
      { label: "Teachers", value: "86", change: "+4", description: "active staff", tone: "success" },
      { label: "Classes", value: "42", change: "+3", description: "across sections", tone: "accent" },
      { label: "Attendance Rate", value: "92%", change: "+3%", description: "this week", tone: "success" },
    ],
    timetable: [
      { time: "09:30 - 10:15", className: "Grade 8 - A", subject: "Mathematics", room: "Room 204", students: 28, active: true },
      { time: "10:20 - 11:05", className: "Grade 8 - A", subject: "Science", room: "Room 204", students: 28 },
      { time: "11:20 - 12:05", className: "Grade 8 - A", subject: "English", room: "Room 204", students: 28 },
      { time: "12:05 - 12:45", className: "Lunch Break", subject: "Break", room: "Cafeteria", students: null },
      { time: "12:45 - 13:30", className: "Grade 8 - A", subject: "Social Studies", room: "Room 204", students: 28 },
      { time: "13:35 - 14:20", className: "Grade 8 - A", subject: "Computer Science", room: "Lab 2", students: 28 },
    ],
    attendanceClasses: [
      { className: "Grade 8 - A", subject: "Mathematics", students: 28, active: true },
      { className: "Grade 7 - B", subject: "English", students: 26 },
      { className: "Grade 9 - A", subject: "Science", students: 30 },
    ],
    performance: [
      { name: "Average Score", value: 78 },
      { name: "Attendance", value: 92 },
      { name: "Assessment Done", value: 86 },
    ],
    weeklyAttendance: [
      { day: "Mon", present: 91, late: 5, absent: 4 },
      { day: "Tue", present: 93, late: 4, absent: 3 },
      { day: "Wed", present: 89, late: 6, absent: 5 },
      { day: "Thu", present: 94, late: 3, absent: 3 },
      { day: "Fri", present: 92, late: 2, absent: 6 },
    ],
    notices: [
      { title: "Parent-Teacher Meeting", category: "Important", tone: "error", date: "10 May, 09:15", detail: "PTM for Grades 6-10 will be held on May 18, 2025." },
      { title: "Annual Sports Day", category: "General", tone: "warning", date: "9 May, 16:40", detail: "Annual Sports Day will be held on May 24." },
      { title: "Unit Test Schedule", category: "Academic", tone: "primary", date: "8 May, 11:20", detail: "Unit Test 1 schedule has been published." },
    ],
    insights: [
      { title: "Attendance improved by 3%", detail: "Compared to last month", tone: "success" },
      { title: "7 students are at academic risk", detail: "Intervention recommended", tone: "warning" },
      { title: "Grade 8 - A performance trend", detail: "Improving steadily", tone: "primary" },
    ],
    assignedClasses: [
      { className: "Grade 8 - A", role: "Homeroom", students: 28, subjects: ["Mathematics", "Science", "English"] },
      { className: "Grade 7 - B", role: "Mathematics", students: 26, subjects: ["Mathematics", "Computer Science"] },
      { className: "Grade 9 - A", role: "Science", students: 30, subjects: ["Physics", "Chemistry"] },
    ],
    aiActivity: [
      { title: "AI report generated", detail: "Weekly attendance report", time: "2 hours ago" },
      { title: "Smart suggestion", detail: "5 students need intervention", time: "5 hours ago" },
      { title: "Message summary", detail: "3 unread parent messages", time: "Yesterday" },
      { title: "Timetable updated", detail: "Science lab allocation changed", time: "Yesterday" },
    ],
  }),

  getTeacherOverview: async () => ({
    stats: [
      { label: "Assigned Classes", value: "6", change: "+1", description: "this term", tone: "primary" },
      { label: "Students", value: "184", change: "+8", description: "under care", tone: "success" },
      { label: "Pending Marks", value: "12", change: "-6", description: "to review", tone: "warning" },
      { label: "Attendance Today", value: "94%", change: "+2%", description: "marked", tone: "success" },
    ],
  }),

  getStudentOverview: async () => ({
    stats: [
      { label: "Average Score", value: "84%", change: "+5%", description: "this term", tone: "success" },
      { label: "Attendance", value: "96%", change: "+1%", description: "this week", tone: "primary" },
      { label: "Assignments", value: "3", change: "Due", description: "this week", tone: "warning" },
      { label: "Notices", value: "5", change: "New", description: "school updates", tone: "accent" },
    ],
  }),

  getParentOverview: async () => ({
    stats: [
      { label: "Children", value: "2", change: "Active", description: "enrolled", tone: "primary" },
      { label: "Attendance", value: "93%", change: "+2%", description: "family average", tone: "success" },
      { label: "Outstanding Fees", value: "NGN 42k", change: "Due", description: "this term", tone: "warning" },
      { label: "Unread Notices", value: "4", change: "New", description: "school messages", tone: "accent" },
    ],
  }),
};
