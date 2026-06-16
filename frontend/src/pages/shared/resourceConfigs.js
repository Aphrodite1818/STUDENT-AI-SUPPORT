import React from "react";
import Badge from "../../components/ui/Badge";
import { classService, attendanceService, examService, resultService } from "../../services/academicsService";
import { financeService } from "../../services/financeService";
import { parentService } from "../../services/parentService";
import { studentService } from "../../services/studentService";
import { subjectService } from "../../services/subject.service";
import { teacherService } from "../../services/teacherService";
import { userService } from "../../services/user.service";

const studentStatuses = ["active", "withdrawn", "suspended", "graduated"];
const attendanceStatuses = ["present", "absent", "late", "excused"];
const paymentStatuses = ["pending", "paid", "failed", "refunded"];

const titleCase = (value) =>
  String(value || "")
    .replace(/_/g, " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());

const optionsFrom = (items, labelFn) =>
  (items || []).map((item) => ({
    value: item.id,
    label: labelFn(item),
  }));

const enumOptions = (values) =>
  values.map((value) => ({ value, label: titleCase(value) }));

const fullName = (item) =>
  [item?.firstname, item?.lastname].filter(Boolean).join(" ") ||
  item?.email ||
  item?.id ||
  "Unknown";

const className = (item) =>
  [item?.name, item?.arm].filter(Boolean).join(" ") || item?.id || "Unknown class";

const subjectName = (item) =>
  [item?.name, item?.code ? `(${item.code})` : ""].filter(Boolean).join(" ");

const summarizeLabels = (items = [], formatter = fullName) => {
  if (!items.length) return "Unassigned";

  const labels = items.map((item) => formatter(item)).filter(Boolean);
  if (labels.length <= 1) return labels[0] || "Unassigned";

  return `${labels[0]} +${labels.length - 1} more`;
};

const byId = (items) =>
  (items || []).reduce((map, item) => {
    map[item.id] = item;
    return map;
  }, {});

const selectedIds = (items = []) =>
  items.map((item) => item.id).filter(Boolean);

const labelFromMap = (map, id, fallback = "N/A") =>
  id && map[id] ? fullName(map[id]) || className(map[id]) || subjectName(map[id]) : fallback;

const optionalValue = (value, fallback = "Not provided") => value || fallback;

const formatDateValue = (value) => {
  if (!value) return "Not set";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
};

const statusBadge = (value, variant = "default") => (
  React.createElement(Badge, { variant }, titleCase(value || "unknown"))
);

const compactPayload = (payload) =>
  Object.entries(payload).reduce((nextPayload, [key, value]) => {
    nextPayload[key] = value === "" ? null : value;
    return nextPayload;
  }, {});

const loadAcademicContext = async ({ includeUsers = false, includeFees = false } = {}) => {
  const [classes, subjects, students, exams, users, fees] = await Promise.all([
    classService.getClasses({ limit: 100 }),
    subjectService.getSubjects({ limit: 100, isActive: true }),
    studentService.getStudents({ limit: 100 }),
    examService.getExams({ limit: 100 }),
    includeUsers ? userService.getUsers(0, 500) : Promise.resolve([]),
    includeFees ? financeService.getFees({ limit: 100 }) : Promise.resolve({ items: [] }),
  ]);

  const classItems = classes?.items || [];
  const subjectItems = subjects?.items || [];
  const studentItems = students?.items || [];
  const examItems = exams?.items || [];
  const userItems = Array.isArray(users) ? users : [];
  const feeItems = fees?.items || [];

  return {
    classes: classItems,
    subjects: subjectItems,
    students: studentItems,
    exams: examItems,
    users: userItems,
    parents: userItems.filter((user) => user.role === "parent"),
    studentUsers: userItems.filter((user) => user.role === "student"),
    teacherUsers: userItems.filter((user) => user.role === "teacher"),
    fees: feeItems,
    userById: byId(userItems),
    classById: byId(classItems),
    subjectById: byId(subjectItems),
    studentById: byId(studentItems),
    examById: byId(examItems),
    feeById: byId(feeItems),
  };
};

const loadClassContext = async () => {
  const teachers = await teacherService.getTeachers({ limit: 100 });
  const teacherItems = teachers?.items || [];

  return {
    teachers: teacherItems,
    teacherById: byId(teacherItems),
  };
};

const loadSubjectContext = async () => {
  const [teachers, users] = await Promise.all([
    teacherService.getTeachers({ limit: 100 }),
    userService.getUsers(0, 500),
  ]);

  const userItems = Array.isArray(users) ? users : [];
  const userByIdMap = byId(userItems);
  const teacherItems = (teachers?.items || []).filter(
    (teacher) => teacher.status === "active"
  );

  return {
    teachers: teacherItems,
    userById: userByIdMap,
    teacherById: byId(teacherItems),
  };
};

const classColumns = [
  { key: "name", label: "Class" },
  { key: "level", label: "Level", render: (item) => item.level || "N/A" },
  { key: "arm", label: "Arm", render: (item) => item.arm || "N/A" },
];

const classFields = (context) => [
  { name: "name", label: "Class name", required: true },
  { name: "level", label: "Level", placeholder: "Junior Secondary 1" },
  { name: "arm", label: "Arm", placeholder: "A" },
  {
    name: "teacher_id",
    label: "Class teacher",
    type: "select",
    options: optionsFrom(context.teachers, (teacher) => fullName(teacher.user)),
  },
  { name: "description", label: "Description", type: "textarea" },
];

export const getClassResourceConfig = ({ role, writable }) => ({
  singularLabel: "Class",
  pluralLabel: "Classes",
  formHelp: "Classes are created by admins. Teachers can view the classes exposed by the API.",
  canCreate: writable,
  canUpdate: writable,
  canDelete: writable,
  loadContext: writable ? loadClassContext : undefined,
  initialForm: { name: "", level: "", arm: "", teacher_id: "", description: "" },
  fields: classFields,
  filters: [{ name: "search", label: "Search", placeholder: "Class name" }],
  columns: (context) => [
    ...classColumns,
    {
      key: "teacher_id",
      label: "Teacher",
      render: (item) => {
        if (!item.teacher_id) return "Unassigned";
        const teacher = context.teacherById?.[item.teacher_id];
        return teacher ? fullName(teacher.user) : item.teacher_id;
      },
    },
  ],
  fetchItems: (filters) => classService.getClasses({ search: filters.search }),
  createItem: (payload) => classService.createClass(payload),
  updateItem: (id, payload) => classService.updateClass(id, payload),
  deleteItem: (id) => classService.deleteClass(id),
  mapItemToForm: (item) => ({
    name: item.name || "",
    level: item.level || "",
    arm: item.arm || "",
    teacher_id: item.teacher_id || "",
    description: item.description || "",
  }),
  getItemLabel: (item) => className(item),
  role,
});

export const subjectReadOnlyResourceConfig = {
  singularLabel: "Subject",
  pluralLabel: "Subjects",
  canCreate: false,
  canUpdate: false,
  canDelete: false,
  filters: [
    { name: "search", label: "Search", placeholder: "Subject name" },
    {
      name: "isActive",
      label: "Status",
      type: "select",
      options: [
        { value: "true", label: "Active" },
        { value: "false", label: "Inactive" },
      ],
    },
  ],
  columns: [
    { key: "name", label: "Subject" },
    { key: "code", label: "Code", render: (item) => item.code || "N/A" },
    {
      key: "is_active",
      label: "Status",
      render: (item) => (item.is_active ? "Active" : "Inactive"),
    },
    {
      key: "description",
      label: "Description",
      render: (item) => item.description || "N/A",
    },
  ],
  fetchItems: (filters) =>
    subjectService.getSubjects({
      search: filters.search,
      isActive:
        filters.isActive === "true"
          ? true
          : filters.isActive === "false"
            ? false
            : undefined,
    }),
  mapItemToForm: () => ({}),
};

export const teacherSubjectResourceConfig = {
  ...subjectReadOnlyResourceConfig,
  fetchItems: (filters) =>
    teacherService.getMySubjects({
      search: filters.search,
      isActive:
        filters.isActive === "true"
          ? true
          : filters.isActive === "false"
            ? false
            : undefined,
    }),
};

export const subjectResourceConfig = {
  singularLabel: "Subject",
  pluralLabel: "Subjects",
  formHelp: "Subjects define the academic catalog teachers and classes can be assigned to.",
  canCreate: true,
  canUpdate: true,
  canDelete: true,
  loadContext: loadSubjectContext,
  initialForm: {
    name: "",
    code: "",
    description: "",
    is_active: "true",
    teacher_ids: [],
  },
  fields: (context) => [
    { name: "name", label: "Subject name", required: true },
    { name: "code", label: "Subject code" },
    { name: "description", label: "Description", type: "textarea" },
    {
      name: "teacher_ids",
      label: "Assigned teachers",
      type: "multiselect",
      placeholder: "Search teachers by name, email, or staff ID",
      searchPlaceholder: "Search by name, email, or staff ID",
      options: optionsFrom(context.teachers, (teacher) => {
        const user = context.userById?.[teacher.user_id] || teacher.user;
        const primaryLabel = fullName(user) || teacher.staff_id || teacher.id;
        const secondaryLabel = [teacher.staff_id, user?.email]
          .filter(Boolean)
          .join(" | ");
        return secondaryLabel
          ? `${primaryLabel} - ${secondaryLabel}`
          : primaryLabel;
      }),
    },
    {
      name: "is_active",
      label: "Status",
      type: "select",
      options: [
        { value: "true", label: "Active" },
        { value: "false", label: "Inactive" },
      ],
    },
  ],
  filters: subjectReadOnlyResourceConfig.filters,
  columns: [
    ...subjectReadOnlyResourceConfig.columns,
    {
      key: "teachers",
      label: "Teachers",
      render: (item) => summarizeLabels(item.teachers, fullName),
    },
  ],
  fetchItems: subjectReadOnlyResourceConfig.fetchItems,
  buildPayload: (formData) =>
    compactPayload({
      name: formData.name,
      code: formData.code,
      description: formData.description,
      is_active: formData.is_active,
      teacher_ids: formData.teacher_ids,
    }),
  createItem: (payload) =>
    subjectService.createSubject({
      name: payload.name,
      code: payload.code,
      description: payload.description,
      teacher_ids: payload.teacher_ids || [],
    }),
  updateItem: async (id, payload) => {
    await subjectService.updateSubject(id, {
      name: payload.name,
      code: payload.code,
      description: payload.description,
      teacher_ids: payload.teacher_ids || [],
    });

    if (payload.is_active === "true") {
      await subjectService.activateSubject(id);
    } else if (payload.is_active === "false") {
      await subjectService.deactivateSubject(id);
    }
  },
  deleteItem: (id) => subjectService.deleteSubject(id),
  mapItemToForm: (item) => ({
    name: item.name || "",
    code: item.code || "",
    description: item.description || "",
    is_active: item.is_active ? "true" : "false",
    teacher_ids: selectedIds(item.teachers),
  }),
  getItemLabel: (item) => subjectName(item),
};

export const teacherResourceConfig = {
  singularLabel: "Teacher profile",
  pluralLabel: "Teacher profiles",
  formHelp: "Teacher profiles are created automatically when a teacher user is invited. Edit staff details and assigned subjects here.",
  canCreate: false,
  canUpdate: true,
  canDelete: true,
  loadContext: () => loadAcademicContext({ includeUsers: true }),
  initialForm: {
    staff_id: "",
    qualification: "",
    specialization: "",
    subject_ids: [],
  },
  fields: (context) => [
    { name: "staff_id", label: "Staff ID" },
    { name: "qualification", label: "Qualification" },
    { name: "specialization", label: "Specialization" },
    {
      name: "subject_ids",
      label: "Assigned subjects",
      type: "multiselect",
      placeholder: "Search subjects",
      options: optionsFrom(context.subjects, subjectName),
    },
  ],
  columns: (context) => [
    {
      key: "user_id",
      label: "Teacher",
      render: (item) => fullName(context.userById?.[item.user_id]) || item.user_id,
    },
    { key: "staff_id", label: "Staff ID", render: (item) => item.staff_id || "N/A" },
    { key: "qualification", label: "Qualification", render: (item) => item.qualification || "N/A" },
    { key: "specialization", label: "Specialization", render: (item) => item.specialization || "N/A" },
  ],
  fetchItems: () => teacherService.getTeachers({ limit: 100 }),
  updateItem: (id, payload) => teacherService.updateTeacher(id, payload),
  deleteItem: (id) => teacherService.deleteTeacher(id),
  buildPayload: (formData) =>
    compactPayload({
      staff_id: formData.staff_id,
      qualification: formData.qualification,
      specialization: formData.specialization,
      subject_ids: formData.subject_ids,
    }),
  mapItemToForm: (item) => ({
    staff_id: item.staff_id || "",
    qualification: item.qualification || "",
    specialization: item.specialization || "",
    subject_ids: selectedIds(item.subjects),
  }),
  getItemLabel: (item, context) => fullName(context.userById?.[item.user_id]) || item.user_id,
};

export const getStudentResourceConfig = ({ writable }) => ({
  singularLabel: "Student",
  pluralLabel: "Students",
  formHelp:
    "Student profiles are created automatically from user invites. Complete academic details here when they become available.",
  canCreate: false,
  canUpdate: writable,
  canDelete: writable,
  loadContext: () => loadAcademicContext({ includeUsers: writable }),
  initialForm: {
    gender: "",
    date_of_birth: "",
    class_id: "",
    arm: "",
    status: "active",
    graduation_date: "",
  },
  fields: (context) => [
    { name: "gender", label: "Gender", type: "select", options: enumOptions(["male", "female"]) },
    { name: "date_of_birth", label: "Date of birth", type: "date" },
    { name: "class_id", label: "Class", type: "select", options: optionsFrom(context.classes, className) },
    { name: "arm", label: "Arm" },
    { name: "status", label: "Academic status", type: "select", required: true, options: enumOptions(studentStatuses) },
    { name: "graduation_date", label: "Graduation date", type: "date" },
  ],
  filters: (context) => [
    { name: "search", label: "Search", placeholder: "Name or admission no." },
    { name: "classId", label: "Class", type: "select", options: optionsFrom(context.classes, className) },
    { name: "status", label: "Status", type: "select", options: enumOptions(studentStatuses) },
  ],
  columns: () => [
    { key: "name", label: "Full Name", render: (item) => fullName(item) },
    { key: "email", label: "Email", render: (item) => optionalValue(item.email) },
    { key: "admission_number", label: "Admission Number", render: (item) => optionalValue(item.admission_number, "Pending") },
    { key: "admission_date", label: "Admission Date", render: (item) => formatDateValue(item.admission_date) },
    {
      key: "profile_status",
      label: "Profile Status",
      render: (item) =>
        statusBadge(
          item.profile_status,
          item.profile_status === "incomplete" ? "warning" : "success"
        ),
    },
    {
      key: "status",
      label: "Academic Status",
      render: (item) => statusBadge(item.status, item.status === "active" ? "success" : "default"),
    },
  ],
  fetchItems: (filters) =>
    studentService.getStudents({
      search: filters.search,
      classId: filters.classId,
      status: filters.status,
    }),
  createItem: undefined,
  updateItem: (id, payload) => studentService.updateStudent(id, payload),
  deleteItem: (id) => studentService.deleteStudent(id),
  buildPayload: (formData) => compactPayload(formData),
  mapItemToForm: (item) => ({
    gender: item.gender || "",
    date_of_birth: item.date_of_birth || "",
    class_id: item.class_id || "",
    arm: item.arm || "",
    status: item.status || "active",
    graduation_date: item.graduation_date || "",
  }),
  getItemLabel: (item) => fullName(item),
});

export const parentResourceConfig = {
  singularLabel: "Parent profile",
  pluralLabel: "Parent profiles",
  formHelp:
    "Parent profiles are created automatically from user invites. Optional contact details can be completed here later.",
  canCreate: false,
  canUpdate: true,
  canDelete: true,
  initialForm: {
    occupation: "",
    address: "",
    emergency_phone: "",
  },
  fields: [
    { name: "occupation", label: "Occupation" },
    { name: "address", label: "Address", type: "textarea" },
    { name: "emergency_phone", label: "Emergency phone", placeholder: "+2348012345678" },
  ],
  columns: [
    { key: "name", label: "Full Name", render: (item) => fullName(item) },
    { key: "email", label: "Email", render: (item) => optionalValue(item.email) },
    { key: "phone_number", label: "Phone Number", render: (item) => optionalValue(item.phone_number) },
    { key: "whatsapp_id", label: "WhatsApp", render: (item) => optionalValue(item.whatsapp_id) },
    { key: "occupation", label: "Occupation", render: (item) => optionalValue(item.occupation) },
    { key: "emergency_phone", label: "Emergency Phone", render: (item) => optionalValue(item.emergency_phone) },
  ],
  fetchItems: () => parentService.getParents({ limit: 100 }),
  updateItem: (id, payload) => parentService.updateParent(id, payload),
  deleteItem: (id) => parentService.deleteParent(id),
  buildPayload: (formData) => compactPayload(formData),
  mapItemToForm: (item) => ({
    occupation: item.occupation || "",
    address: item.address || "",
    emergency_phone: item.emergency_phone || "",
  }),
  getItemLabel: (item) => fullName(item),
};

export const getAttendanceResourceConfig = ({ writable, canDelete }) => ({
  singularLabel: "Attendance record",
  pluralLabel: "Attendance records",
  formHelp: "Teachers can create and update attendance; only admins can delete records.",
  canCreate: writable,
  canUpdate: writable,
  canDelete,
  loadContext: () => loadAcademicContext(),
  initialForm: {
    student_id: "",
    class_id: "",
    attendance_date: new Date().toISOString().slice(0, 10),
    status: "present",
    note: "",
  },
  fields: (context) => [
    { name: "student_id", label: "Student", type: "select", required: true, showOnEdit: false, options: optionsFrom(context.students, fullName) },
    { name: "class_id", label: "Class", type: "select", required: true, showOnEdit: false, options: optionsFrom(context.classes, className) },
    { name: "attendance_date", label: "Date", type: "date", required: true, showOnEdit: false },
    { name: "status", label: "Status", type: "select", required: true, options: enumOptions(attendanceStatuses) },
    { name: "note", label: "Note", type: "textarea" },
  ],
  filters: (context) => [
    { name: "classId", label: "Class", type: "select", options: optionsFrom(context.classes, className) },
    { name: "studentId", label: "Student", type: "select", options: optionsFrom(context.students, fullName) },
    { name: "attendanceDate", label: "Date", type: "date" },
  ],
  columns: (context) => [
    { key: "student_id", label: "Student", render: (item) => fullName(context.studentById[item.student_id]) },
    { key: "class_id", label: "Class", render: (item) => className(context.classById[item.class_id]) },
    { key: "attendance_date", label: "Date" },
    { key: "status", label: "Status", render: (item) => titleCase(item.status) },
    { key: "note", label: "Note", render: (item) => item.note || "N/A" },
  ],
  fetchItems: (filters) =>
    attendanceService.getAttendance({
      classId: filters.classId,
      studentId: filters.studentId,
      attendanceDate: filters.attendanceDate,
    }),
  createItem: (payload) => attendanceService.createAttendance(payload),
  updateItem: (id, payload) => attendanceService.updateAttendance(id, payload),
  deleteItem: (id) => attendanceService.deleteAttendance(id),
  buildPayload: (formData, editingItem) =>
    editingItem
      ? compactPayload({ status: formData.status, note: formData.note })
      : compactPayload(formData),
  mapItemToForm: (item) => ({
    student_id: item.student_id || "",
    class_id: item.class_id || "",
    attendance_date: item.attendance_date || "",
    status: item.status || "present",
    note: item.note || "",
  }),
});

export const getExamResourceConfig = ({ canDelete }) => ({
  singularLabel: "Exam",
  pluralLabel: "Exams",
  formHelp: "Teachers can schedule and update exams. Deleting exams is reserved for admins.",
  canCreate: true,
  canUpdate: true,
  canDelete,
  loadContext: () => loadAcademicContext(),
  initialForm: {
    name: "",
    subject_id: "",
    class_id: "",
    term: "",
    academic_session: "",
    exam_date: "",
    max_score: "100",
  },
  fields: (context) => [
    { name: "name", label: "Exam name", required: true },
    { name: "subject_id", label: "Subject", type: "select", required: true, options: optionsFrom(context.subjects, subjectName) },
    { name: "class_id", label: "Class", type: "select", required: true, options: optionsFrom(context.classes, className) },
    { name: "term", label: "Term", required: true, placeholder: "First term" },
    { name: "academic_session", label: "Academic session", required: true, placeholder: "2025/2026" },
    { name: "exam_date", label: "Exam date", type: "date" },
    { name: "max_score", label: "Max score", type: "number", step: "0.01", min: "0.01", required: true },
  ],
  filters: (context) => [
    { name: "classId", label: "Class", type: "select", options: optionsFrom(context.classes, className) },
    { name: "subjectId", label: "Subject", type: "select", options: optionsFrom(context.subjects, subjectName) },
  ],
  columns: (context) => [
    { key: "name", label: "Exam" },
    { key: "subject_id", label: "Subject", render: (item) => subjectName(context.subjectById[item.subject_id]) },
    { key: "class_id", label: "Class", render: (item) => className(context.classById[item.class_id]) },
    { key: "term", label: "Term" },
    { key: "max_score", label: "Max score" },
  ],
  fetchItems: (filters) => examService.getExams({ classId: filters.classId, subjectId: filters.subjectId }),
  createItem: (payload) => examService.createExam(payload),
  updateItem: (id, payload) => examService.updateExam(id, payload),
  deleteItem: (id) => examService.deleteExam(id),
  mapItemToForm: (item) => ({
    name: item.name || "",
    subject_id: item.subject_id || "",
    class_id: item.class_id || "",
    term: item.term || "",
    academic_session: item.academic_session || "",
    exam_date: item.exam_date || "",
    max_score: item.max_score || "100",
  }),
  getItemLabel: (item) => item.name,
});

export const getResultResourceConfig = ({ canDelete }) => ({
  singularLabel: "Result",
  pluralLabel: "Results",
  formHelp: "Create results against a student, class, subject, and optionally an exam.",
  canCreate: true,
  canUpdate: true,
  canDelete,
  loadContext: () => loadAcademicContext(),
  initialForm: {
    student_id: "",
    subject_id: "",
    class_id: "",
    exam_id: "",
    term: "",
    academic_session: "",
    score: "",
    grade: "",
    remark: "",
  },
  fields: (context) => [
    { name: "student_id", label: "Student", type: "select", required: true, showOnEdit: false, options: optionsFrom(context.students, fullName) },
    { name: "subject_id", label: "Subject", type: "select", required: true, showOnEdit: false, options: optionsFrom(context.subjects, subjectName) },
    { name: "class_id", label: "Class", type: "select", required: true, showOnEdit: false, options: optionsFrom(context.classes, className) },
    { name: "exam_id", label: "Exam", type: "select", options: optionsFrom(context.exams, (exam) => exam.name) },
    { name: "term", label: "Term", required: true, showOnEdit: false },
    { name: "academic_session", label: "Academic session", required: true, showOnEdit: false },
    { name: "score", label: "Score", type: "number", step: "0.01", min: "0", required: true },
    { name: "grade", label: "Grade" },
    { name: "remark", label: "Remark", type: "textarea" },
  ],
  filters: (context) => [
    { name: "studentId", label: "Student", type: "select", options: optionsFrom(context.students, fullName) },
    { name: "classId", label: "Class", type: "select", options: optionsFrom(context.classes, className) },
    { name: "subjectId", label: "Subject", type: "select", options: optionsFrom(context.subjects, subjectName) },
    { name: "term", label: "Term" },
    { name: "academicSession", label: "Academic session" },
  ],
  columns: (context) => [
    { key: "student_id", label: "Student", render: (item) => fullName(context.studentById[item.student_id]) },
    { key: "subject_id", label: "Subject", render: (item) => subjectName(context.subjectById[item.subject_id]) },
    { key: "class_id", label: "Class", render: (item) => className(context.classById[item.class_id]) },
    { key: "score", label: "Score" },
    { key: "grade", label: "Grade", render: (item) => item.grade || "N/A" },
  ],
  fetchItems: (filters) =>
    resultService.getResults({
      studentId: filters.studentId,
      classId: filters.classId,
      subjectId: filters.subjectId,
      term: filters.term,
      academicSession: filters.academicSession,
    }),
  createItem: (payload) => resultService.createResult(payload),
  updateItem: (id, payload) => resultService.updateResult(id, payload),
  deleteItem: (id) => resultService.deleteResult(id),
  buildPayload: (formData, editingItem) =>
    editingItem
      ? compactPayload({
          exam_id: formData.exam_id,
          score: formData.score,
          grade: formData.grade,
          remark: formData.remark,
        })
      : compactPayload(formData),
  mapItemToForm: (item) => ({
    student_id: item.student_id || "",
    subject_id: item.subject_id || "",
    class_id: item.class_id || "",
    exam_id: item.exam_id || "",
    term: item.term || "",
    academic_session: item.academic_session || "",
    score: item.score || "",
    grade: item.grade || "",
    remark: item.remark || "",
  }),
});

export const feeResourceConfig = {
  singularLabel: "Fee",
  pluralLabel: "Fees",
  formHelp: "Fees can be global or tied to a specific class.",
  canCreate: true,
  canUpdate: true,
  canDelete: true,
  loadContext: () => loadAcademicContext(),
  initialForm: { name: "", amount: "", due_date: "", class_id: "", description: "" },
  fields: (context) => [
    { name: "name", label: "Fee name", required: true },
    { name: "amount", label: "Amount", type: "number", step: "0.01", min: "0.01", required: true },
    { name: "due_date", label: "Due date", type: "date" },
    { name: "class_id", label: "Class", type: "select", options: optionsFrom(context.classes, className) },
    { name: "description", label: "Description", type: "textarea" },
  ],
  filters: (context) => [
    { name: "classId", label: "Class", type: "select", options: optionsFrom(context.classes, className) },
  ],
  columns: (context) => [
    { key: "name", label: "Fee" },
    { key: "amount", label: "Amount" },
    { key: "due_date", label: "Due date", render: (item) => item.due_date || "N/A" },
    { key: "class_id", label: "Class", render: (item) => item.class_id ? className(context.classById[item.class_id]) : "All classes" },
  ],
  fetchItems: (filters) => financeService.getFees({ classId: filters.classId }),
  createItem: (payload) => financeService.createFee(payload),
  updateItem: (id, payload) => financeService.updateFee(id, payload),
  deleteItem: (id) => financeService.deleteFee(id),
  mapItemToForm: (item) => ({
    name: item.name || "",
    amount: item.amount || "",
    due_date: item.due_date || "",
    class_id: item.class_id || "",
    description: item.description || "",
  }),
  getItemLabel: (item) => item.name,
};

export const paymentResourceConfig = {
  singularLabel: "Payment",
  pluralLabel: "Payments",
  formHelp: "Record manual payments against a student and fee.",
  canCreate: true,
  canUpdate: true,
  canDelete: true,
  loadContext: () => loadAcademicContext({ includeFees: true }),
  initialForm: { student_id: "", fee_id: "", amount: "", paid_at: "", reference: "", status: "pending" },
  fields: (context) => [
    { name: "student_id", label: "Student", type: "select", required: true, showOnEdit: false, options: optionsFrom(context.students, fullName) },
    { name: "fee_id", label: "Fee", type: "select", required: true, showOnEdit: false, options: optionsFrom(context.fees, (fee) => fee.name) },
    { name: "amount", label: "Amount", type: "number", step: "0.01", min: "0.01", required: true },
    { name: "paid_at", label: "Paid at", type: "datetime-local" },
    { name: "reference", label: "Reference" },
    { name: "status", label: "Status", type: "select", required: true, options: enumOptions(paymentStatuses) },
  ],
  filters: (context) => [
    { name: "studentId", label: "Student", type: "select", options: optionsFrom(context.students, fullName) },
    { name: "feeId", label: "Fee", type: "select", options: optionsFrom(context.fees, (fee) => fee.name) },
  ],
  columns: (context) => [
    { key: "student_id", label: "Student", render: (item) => fullName(context.studentById[item.student_id]) },
    { key: "fee_id", label: "Fee", render: (item) => context.feeById[item.fee_id]?.name || "N/A" },
    { key: "amount", label: "Amount" },
    { key: "status", label: "Status", render: (item) => titleCase(item.status) },
    { key: "reference", label: "Reference", render: (item) => item.reference || "N/A" },
  ],
  fetchItems: (filters) => financeService.getPayments({ studentId: filters.studentId, feeId: filters.feeId }),
  createItem: (payload) => financeService.createPayment(payload),
  updateItem: (id, payload) => financeService.updatePayment(id, payload),
  deleteItem: (id) => financeService.deletePayment(id),
  buildPayload: (formData, editingItem) =>
    editingItem
      ? compactPayload({
          amount: formData.amount,
          paid_at: formData.paid_at,
          reference: formData.reference,
          status: formData.status,
        })
      : compactPayload(formData),
  mapItemToForm: (item) => ({
    student_id: item.student_id || "",
    fee_id: item.fee_id || "",
    amount: item.amount || "",
    paid_at: item.paid_at ? item.paid_at.slice(0, 16) : "",
    reference: item.reference || "",
    status: item.status || "pending",
  }),
};

export const summaryLoaders = {
  classes: () => classService.getClasses({ limit: 1 }),
  students: () => studentService.getStudents({ limit: 1 }),
  teachers: () => teacherService.getTeachers({ limit: 1 }),
  attendance: () => attendanceService.getAttendance({ limit: 1 }),
  exams: () => examService.getExams({ limit: 1 }),
  results: () => resultService.getResults({ limit: 1 }),
  fees: () => financeService.getFees({ limit: 1 }),
  payments: () => financeService.getPayments({ limit: 1 }),
};

export { className, fullName, labelFromMap, loadAcademicContext };
