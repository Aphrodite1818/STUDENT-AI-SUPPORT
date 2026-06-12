import { useCallback, useEffect, useState } from "react";
import { RefreshCw, Send, Trash2, UserPlus } from "lucide-react";
import DashboardLayout from "../../components/layout/DashboardLayout";
import Card from "../../components/ui/Card";
import Button from "../../components/ui/Button";
import Input from "../../components/ui/Input";
import Badge from "../../components/ui/Badge";
import { userService } from "../../services/user.service";
import { getErrorMessage, parseApiError } from "../../services/api";

const INITIAL_FORM = {
  firstname: "",
  lastname: "",
  email: "",
  phone_number: "",
  whatsapp_id: "",
  role: "teacher",
};

const statusVariant = (status) => {
  if (status === "active") return "success";
  if (status === "pending") return "warning";
  return "default";
};

function UserManagementPage() {
  const [users, setUsers] = useState([]);
  const [formData, setFormData] = useState(INITIAL_FORM);
  const [isLoadingUsers, setIsLoadingUsers] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [resendingUserId, setResendingUserId] = useState(null);
  const [deletingUserId, setDeletingUserId] = useState(null);
  const [error, setError] = useState(null);
  const [fieldErrors, setFieldErrors] = useState({});
  const [successMessage, setSuccessMessage] = useState(null);

  const loadUsers = useCallback(async () => {
    setIsLoadingUsers(true);
    try {
      const result = await userService.getUsers();
      setUsers(Array.isArray(result) ? result : []);
    } catch (err) {
      setError(getErrorMessage(err, "Failed to load users."));
    } finally {
      setIsLoadingUsers(false);
    }
  }, []);

  useEffect(() => {
    const timeoutId = window.setTimeout(loadUsers, 0);
    return () => window.clearTimeout(timeoutId);
  }, [loadUsers]);

  const handleChange = (event) => {
    setFormData((prev) => ({ ...prev, [event.target.name]: event.target.value }));
    setFieldErrors((prev) => ({ ...prev, [event.target.name]: undefined }));
    setError(null);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setIsSubmitting(true);
    setError(null);
    setFieldErrors({});
    setSuccessMessage(null);

    try {
      await userService.inviteUser({
        ...formData,
        whatsapp_id: formData.whatsapp_id || null,
      });
      setFormData(INITIAL_FORM);
      setSuccessMessage("Invite created and emailed successfully.");
      await loadUsers();
    } catch (err) {
      const apiError = parseApiError(err, "Failed to create user invite.");
      if (Object.keys(apiError.fieldErrors).length > 0) {
        setFieldErrors(apiError.fieldErrors);
      }
      setError(apiError.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleResendInvite = async (userId) => {
    setResendingUserId(userId);
    setError(null);
    setSuccessMessage(null);

    try {
      const result = await userService.resendInvite(userId);
      setSuccessMessage(result?.detail || "Invite resent successfully.");
      await loadUsers();
    } catch (err) {
      setError(getErrorMessage(err, "Failed to resend invite."));
    } finally {
      setResendingUserId(null);
    }
  };

  const handleDeleteUser = async (user) => {
    const fullName = [user.firstname, user.lastname].filter(Boolean).join(" ");
    const label = fullName || user.email || "this user";

    if (!window.confirm(`Delete ${label}? This cannot be undone.`)) return;

    setDeletingUserId(user.id);
    setError(null);
    setSuccessMessage(null);

    try {
      await userService.deleteUser(user.id);
      setSuccessMessage("User deleted successfully.");
      await loadUsers();
    } catch (err) {
      setError(getErrorMessage(err, "Failed to delete user."));
    } finally {
      setDeletingUserId(null);
    }
  };

  return (
    <DashboardLayout
      role="admin"
      title="User Management"
      description="Invite staff, students, and parents into the tenant workspace and resend setup links when needed."
      actions={
        <Button variant="outline" onClick={loadUsers} disabled={isLoadingUsers}>
          <RefreshCw className="h-4 w-4" />
          Refresh
        </Button>
      }
    >
      {error && (
        <div className="rounded-2xl border border-error/20 bg-error-soft px-4 py-3 text-sm font-medium text-error">
          {error}
        </div>
      )}
      {successMessage && (
        <div className="rounded-2xl border border-success/20 bg-success-soft px-4 py-3 text-sm font-medium text-emerald-700">
          {successMessage}
        </div>
      )}

      <div className="grid gap-6 xl:grid-cols-[390px_minmax(0,1fr)]">
        <Card className="p-5">
          <div className="flex items-start gap-3">
            <span className="flex h-11 w-11 items-center justify-center rounded-2xl bg-primary-soft text-primary">
              <UserPlus className="h-5 w-5" />
            </span>
            <div>
              <h2 className="text-lg font-semibold">Invite a user</h2>
              <p className="mt-1 text-sm text-text-muted">
                The user receives an email link to confirm their address and set a password.
              </p>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="mt-6 space-y-4">
            <div className="grid gap-4 sm:grid-cols-2">
              <Input label="First name" name="firstname" value={formData.firstname} onChange={handleChange} error={fieldErrors.firstname} required />
              <Input label="Last name" name="lastname" value={formData.lastname} onChange={handleChange} error={fieldErrors.lastname} required />
            </div>
            <Input label="Email" type="email" name="email" value={formData.email} onChange={handleChange} error={fieldErrors.email} required />
            <div className="grid gap-4 sm:grid-cols-2">
              <Input label="Phone number" name="phone_number" value={formData.phone_number} onChange={handleChange} placeholder="+2348012345678" error={fieldErrors.phone_number} required />
              <Input label="WhatsApp ID" name="whatsapp_id" value={formData.whatsapp_id} onChange={handleChange} placeholder="+2348012345678" error={fieldErrors.whatsapp_id} />
            </div>
            <div>
              <label className="mb-1.5 block text-sm font-medium text-text-soft">Role</label>
              <select name="role" value={formData.role} onChange={handleChange} className="input-base">
                <option value="teacher">Teacher</option>
                <option value="student">Student</option>
                <option value="parent">Parent</option>
              </select>
              {fieldErrors.role && <p className="mt-1.5 text-xs font-medium text-error">{fieldErrors.role}</p>}
            </div>
            <Button type="submit" className="w-full" disabled={isSubmitting}>
              <Send className="h-4 w-4" />
              {isSubmitting ? "Sending invite..." : "Create user and send invite"}
            </Button>
          </form>
        </Card>

        <Card className="p-5">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h2 className="text-lg font-semibold">Current users</h2>
              <p className="text-sm text-text-muted">Pending users can receive a fresh invite link.</p>
            </div>
            <Badge variant="primary">{users.length} users</Badge>
          </div>

          <div className="mt-5 table-wrap">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Role</th>
                  <th>Status</th>
                  <th>Email</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {isLoadingUsers ? (
                  <tr><td colSpan="5" className="text-text-muted">Loading users...</td></tr>
                ) : users.length === 0 ? (
                  <tr><td colSpan="5" className="text-text-muted">No users found yet.</td></tr>
                ) : (
                  users.map((user) => {
                    const fullName = [user.firstname, user.lastname].filter(Boolean).join(" ");
                    const canResend =
                      user.account_status === "pending" &&
                      user.role !== "admin" &&
                      user.role !== "superadmin";

                    return (
                      <tr key={user.id}>
                        <td className="font-semibold">{fullName || "No name"}</td>
                        <td className="capitalize">{user.role}</td>
                        <td>
                          <Badge variant={statusVariant(user.account_status)}>
                            {user.account_status || "unknown"}
                          </Badge>
                        </td>
                        <td>{user.email}</td>
                        <td>
                          <div className="flex flex-wrap gap-2">
                            {canResend ? (
                              <Button variant="outline" size="sm" onClick={() => handleResendInvite(user.id)} disabled={resendingUserId === user.id}>
                                {resendingUserId === user.id ? "Sending..." : "Resend"}
                              </Button>
                            ) : (
                              <span className="text-xs font-medium text-text-muted">
                                {user.account_status === "active" ? "Active" : "Not available"}
                              </span>
                            )}
                            {user.role !== "admin" && user.role !== "superadmin" && (
                              <Button variant="danger" size="sm" onClick={() => handleDeleteUser(user)} disabled={deletingUserId === user.id}>
                                <Trash2 className="h-4 w-4" />
                                {deletingUserId === user.id ? "Deleting..." : "Delete"}
                              </Button>
                            )}
                          </div>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </Card>
      </div>
    </DashboardLayout>
  );
}

export default UserManagementPage;
