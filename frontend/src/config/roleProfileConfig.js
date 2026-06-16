import { parentService } from "../services/parentService";
import { studentService } from "../services/studentService";
import { teacherService } from "../services/teacherService";
import { tenantService } from "../services/tenant.service";

const COMMON_USER_FIELDS = [
  { source: "user", name: "firstname", label: "First name", required: true },
  { source: "user", name: "lastname", label: "Last name", required: true },
  { source: "user", name: "email", label: "Email", type: "email", required: true },
  {
    source: "user",
    name: "phone_number",
    label: "Phone number",
    placeholder: "+2348012345678",
    required: true,
  },
  {
    source: "user",
    name: "whatsapp_id",
    label: "WhatsApp ID",
    placeholder: "+2348012345678",
  },
];

const STUDENT_GENDER_OPTIONS = [
  { value: "male", label: "Male" },
  { value: "female", label: "Female" },
];

const getTenantContext = async (user) => {
  if (!user?.tenant_id) return null;
  if (user?.tenant?.id === user.tenant_id) return user.tenant;
  return tenantService.getTenant(user.tenant_id);
};

const ROLE_PROFILE_CONFIG = {
  admin: {
    sections: [
      {
        key: "user",
        title: "Personal details",
        description: "These fields belong to the core user account.",
        fields: COMMON_USER_FIELDS,
      },
      {
        key: "tenant",
        title: "School details",
        description: "These fields are stored on the tenant record and managed by administrators.",
        fields: [
          { source: "tenant", name: "school_name", label: "School name", required: true },
          { source: "tenant", name: "email", label: "School email", type: "email", required: true },
          { source: "tenant", name: "phone", label: "School phone" },
          { source: "tenant", name: "admission_number_prefix", label: "Admission prefix" },
          { source: "tenant", name: "address", label: "Address", type: "textarea" },
          { source: "tenant", name: "city", label: "City" },
          { source: "tenant", name: "state", label: "State" },
          { source: "tenant", name: "country", label: "Country" },
        ],
      },
    ],
    loadContext: async (user) => ({
      tenant: await getTenantContext(user),
      roleProfile: null,
    }),
    saveRoleProfile: null,
    isRoleIncomplete: () => false,
  },
  teacher: {
    sections: [
      {
        key: "user",
        title: "Personal details",
        description: "These fields belong to the core user account.",
        fields: COMMON_USER_FIELDS,
      },
      {
        key: "roleProfile",
        title: "Teacher profile",
        description: "Teacher-specific fields come from the teacher profile endpoint.",
        fields: [
          { source: "roleProfile", name: "staff_id", label: "Staff ID" },
          { source: "roleProfile", name: "qualification", label: "Qualification" },
          { source: "roleProfile", name: "specialization", label: "Specialization" },
        ],
      },
    ],
    loadContext: async () => ({
      tenant: null,
      roleProfile: await teacherService.getMyTeacher(),
    }),
    saveRoleProfile: (payload) => teacherService.updateMyTeacherProfile(payload),
    isRoleIncomplete: () => false,
  },
  student: {
    sections: [
      {
        key: "user",
        title: "Personal details",
        description: "These fields belong to the core user account.",
        fields: COMMON_USER_FIELDS,
      },
      {
        key: "roleProfile",
        title: "Student profile",
        description:
          "Some student fields are managed by the school. You can only update the self-service fields exposed by the backend.",
        fields: [
          {
            source: "roleProfile",
            name: "admission_number",
            label: "Admission number",
            readOnly: true,
            emptyLabel: "Pending school assignment",
          },
          {
            source: "roleProfile",
            name: "class_id",
            label: "Assigned class",
            readOnly: true,
            emptyLabel: "Pending school assignment",
          },
          {
            source: "roleProfile",
            name: "profile_status",
            label: "Profile status",
            readOnly: true,
            emptyLabel: "incomplete",
          },
          {
            source: "roleProfile",
            name: "gender",
            label: "Gender",
            type: "select",
            required: true,
            options: STUDENT_GENDER_OPTIONS,
          },
          {
            source: "roleProfile",
            name: "date_of_birth",
            label: "Date of birth",
            type: "date",
            required: true,
          },
          {
            source: "roleProfile",
            name: "passport_photo_url",
            label: "Passport photo URL",
          },
        ],
      },
    ],
    loadContext: async () => ({
      tenant: null,
      roleProfile: await studentService.getMyStudent(),
    }),
    saveRoleProfile: (payload) => studentService.updateMyStudentProfile(payload),
    isRoleIncomplete: ({ roleProfile }) => roleProfile?.profile_status !== "complete",
  },
  parent: {
    sections: [
      {
        key: "user",
        title: "Personal details",
        description: "These fields belong to the core user account.",
        fields: COMMON_USER_FIELDS,
      },
      {
        key: "roleProfile",
        title: "Parent profile",
        description: "Parent-specific fields come from the parent profile endpoint.",
        fields: [
          { source: "roleProfile", name: "occupation", label: "Occupation" },
          { source: "roleProfile", name: "address", label: "Address", type: "textarea" },
          { source: "roleProfile", name: "emergency_phone", label: "Emergency phone" },
        ],
      },
    ],
    loadContext: async () => ({
      tenant: null,
      roleProfile: await parentService.getMyParent(),
    }),
    saveRoleProfile: (payload) => parentService.updateMyParentProfile(payload),
    isRoleIncomplete: () => false,
  },
  superadmin: {
    sections: [
      {
        key: "user",
        title: "Personal details",
        description: "These fields belong to the core platform administrator account.",
        fields: COMMON_USER_FIELDS,
      },
    ],
    loadContext: async () => ({
      tenant: null,
      roleProfile: null,
    }),
    saveRoleProfile: null,
    isRoleIncomplete: () => false,
  },
};

export const getRoleProfileConfig = (role) =>
  ROLE_PROFILE_CONFIG[String(role || "").toLowerCase()] || ROLE_PROFILE_CONFIG.admin;

export async function loadRoleProfileContext(role, user) {
  const config = getRoleProfileConfig(role);
  if (!config.loadContext) {
    return { tenant: null, roleProfile: null };
  }
  return config.loadContext(user);
}

export function evaluateOnboardingState(role, user, context = {}) {
  const config = getRoleProfileConfig(role);
  const missingBaseFields = COMMON_USER_FIELDS.filter((field) => field.required).map((field) => field.name).filter((fieldName) => !user?.[fieldName]);
  const roleIncomplete = Boolean(config.isRoleIncomplete?.({ user, ...context }));

  return {
    missingBaseFields,
    hasMissingBaseFields: missingBaseFields.length > 0,
    roleIncomplete,
    incomplete: missingBaseFields.length > 0 || roleIncomplete,
  };
}
