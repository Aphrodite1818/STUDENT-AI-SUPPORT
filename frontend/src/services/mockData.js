export const mockClasses = [
  { id: "class-8a", name: "Grade 8", level: "Junior Secondary", arm: "A", teacher_id: "teacher-1", description: "Core academic class" },
  { id: "class-7b", name: "Grade 7", level: "Junior Secondary", arm: "B", teacher_id: "teacher-2", description: "Science-focused class" },
  { id: "class-9a", name: "Grade 9", level: "Junior Secondary", arm: "A", teacher_id: "teacher-3", description: "Exam preparation class" },
];

export const mockUsers = [
  { id: "user-parent-1", firstname: "Ada", lastname: "Okafor", email: "ada.parent@example.com", role: "parent", account_status: "active" },
  { id: "user-teacher-1", firstname: "Anita", lastname: "Sharma", email: "anita.sharma@example.com", role: "teacher", account_status: "active" },
  { id: "user-teacher-2", firstname: "David", lastname: "Mensah", email: "david.mensah@example.com", role: "teacher", account_status: "active" },
];

export const mockTeachers = [
  {
    id: "teacher-1",
    user_id: "user-teacher-1",
    staff_id: "TCH-1021",
    qualification: "B.Ed Mathematics",
    specialization: "Mathematics",
    status: "active",
    user: mockUsers[1],
  },
  {
    id: "teacher-2",
    user_id: "user-teacher-2",
    staff_id: "TCH-1044",
    qualification: "M.Sc Computer Science",
    specialization: "Computer Science",
    status: "active",
    user: mockUsers[2],
  },
];

export const mockSubjects = [
  { id: "subject-math", name: "Mathematics", code: "MTH", is_active: true, description: "Core numeracy and problem solving" },
  { id: "subject-eng", name: "English", code: "ENG", is_active: true, description: "Language and comprehension" },
  { id: "subject-sci", name: "Science", code: "SCI", is_active: true, description: "General science foundations" },
  { id: "subject-cs", name: "Computer Science", code: "CSC", is_active: true, description: "Digital literacy and programming" },
];

export const mockStudents = [
  { id: "student-1", firstname: "Maya", lastname: "Cole", gender: "female", admission_number: "ADM-2401", class_id: "class-8a", parent_id: "user-parent-1", status: "active", admission_date: "2024-09-01" },
  { id: "student-2", firstname: "Tunde", lastname: "Adebayo", gender: "male", admission_number: "ADM-2402", class_id: "class-7b", parent_id: "user-parent-1", status: "active", admission_date: "2024-09-01" },
  { id: "student-3", firstname: "Lina", lastname: "Park", gender: "female", admission_number: "ADM-2403", class_id: "class-9a", parent_id: "user-parent-1", status: "active", admission_date: "2024-09-01" },
];

export const mockAttendance = [
  { id: "attendance-1", student_id: "student-1", class_id: "class-8a", attendance_date: "2026-06-12", status: "present", note: "" },
  { id: "attendance-2", student_id: "student-2", class_id: "class-7b", attendance_date: "2026-06-12", status: "late", note: "Arrived after assembly" },
  { id: "attendance-3", student_id: "student-3", class_id: "class-9a", attendance_date: "2026-06-12", status: "present", note: "" },
];

export const mockExams = [
  { id: "exam-1", name: "Unit Test 1", subject_id: "subject-math", class_id: "class-8a", term: "Second term", academic_session: "2025/2026", max_score: 100 },
  { id: "exam-2", name: "Midterm Assessment", subject_id: "subject-sci", class_id: "class-9a", term: "Second term", academic_session: "2025/2026", max_score: 100 },
];

export const mockResults = [
  { id: "result-1", student_id: "student-1", subject_id: "subject-math", class_id: "class-8a", exam_id: "exam-1", score: 86, grade: "A", term: "Second term", academic_session: "2025/2026", remark: "Excellent" },
  { id: "result-2", student_id: "student-2", subject_id: "subject-sci", class_id: "class-7b", exam_id: "exam-2", score: 74, grade: "B", term: "Second term", academic_session: "2025/2026", remark: "Good progress" },
];

export const mockFees = [
  { id: "fee-1", name: "Second Term Tuition", amount: 125000, due_date: "2026-07-15", class_id: "", description: "Standard tuition" },
  { id: "fee-2", name: "Science Lab Fee", amount: 18500, due_date: "2026-07-01", class_id: "class-9a", description: "Lab materials" },
];

export const mockPayments = [
  { id: "payment-1", student_id: "student-1", fee_id: "fee-1", amount: 125000, status: "paid", reference: "PAY-1001", paid_at: "2026-06-10T09:00" },
  { id: "payment-2", student_id: "student-2", fee_id: "fee-2", amount: 18500, status: "pending", reference: "PAY-1002", paid_at: "" },
];

export const page = (items) => ({ items, total: items.length });
