import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import Card from "../../components/ui/Card";
import Button from "../../components/ui/Button";
import Input from "../../components/ui/Input";
import { userService } from "../../services/user.service";
import { getErrorMessage } from "../../services/api";

const INITIAL_FORM = {
  firstname: "",
  lastname: "",
  email: "",
  phone_number: "",
  whatsapp_id: "",
  role: "teacher",
};

function UserManagementPage() {
  const [users, setUsers] = useState([]);
  const [formData, setFormData] = useState(INITIAL_FORM);
  const [isLoadingUsers, setIsLoadingUsers] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [resendingUserId, setResendingUserId] = useState(null);
  const [deletingUserId, setDeletingUserId] = useState(null);
  const [error, setError] = useState(null);
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
    const timeoutId = window.setTimeout(() => {
      loadUsers();
    }, 0);

    return () => window.clearTimeout(timeoutId);
  }, [loadUsers]);

  const handleChange = (event) => {
    setFormData((prev) => ({
      ...prev,
      [event.target.name]: event.target.value,
    }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setIsSubmitting(true);
    setError(null);
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
      setError(getErrorMessage(err, "Failed to create user invite."));
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

    if (!window.confirm(`Delete ${label}? This cannot be undone.`)) {
      return;
    }

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
    <div className="min-h-screen bg-background text-text p-6 md:p-8">
      <div className="mx-auto max-w-6xl space-y-6">
        <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <div>
            <h1 className="text-3xl font-bold">User management</h1>
            <p className="text-sm text-text-muted mt-1">
              Invite normal users into your school workspace and resend setup links when needed.
            </p>
          </div>
          <Link to="/admin/dashboard">
            <Button variant="outline">Back to dashboard</Button>
          </Link>
        </div>

        {error && (
          <div className="rounded-md border border-red-500/40 bg-red-500/10 px-4 py-3 text-sm text-red-600">
            {error}
          </div>
        )}

        {successMessage && (
          <div className="rounded-md border border-green-500/40 bg-green-500/10 px-4 py-3 text-sm text-green-700">
            {successMessage}
          </div>
        )}

        <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.3fr)]">
          <Card className="p-6">
            <h2 className="text-xl font-semibold">Invite a user</h2>
            <p className="mt-1 text-sm text-text-muted">
              The user will receive an email link to confirm the same email address and set their password.
            </p>

            <form onSubmit={handleSubmit} className="mt-6 space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <Input
                  label="First name"
                  name="firstname"
                  value={formData.firstname}
                  onChange={handleChange}
                  required
                />
                <Input
                  label="Last name"
                  name="lastname"
                  value={formData.lastname}
                  onChange={handleChange}
                  required
                />
              </div>

              <Input
                label="Email"
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                required
              />

              <div className="grid gap-4 md:grid-cols-2">
                <Input
                  label="Phone number"
                  name="phone_number"
                  value={formData.phone_number}
                  onChange={handleChange}
                  placeholder="+2348012345678"
                  required
                />
                <Input
                  label="WhatsApp ID"
                  name="whatsapp_id"
                  value={formData.whatsapp_id}
                  onChange={handleChange}
                  placeholder="+2348012345678"
                />
              </div>

              <div>
                <label className="mb-1.5 block text-sm font-medium text-text-soft">
                  Role
                </label>
                <select
                  name="role"
                  value={formData.role}
                  onChange={handleChange}
                  className="input-base"
                >
                  <option value="teacher">Teacher</option>
                  <option value="student">Student</option>
                  <option value="parent">Parent</option>
                </select>
              </div>

              <Button type="submit" className="w-full" disabled={isSubmitting}>
                {isSubmitting ? "Sending invite..." : "Create user and send invite"}
              </Button>
            </form>
          </Card>

          <Card className="p-6">
            <div className="flex items-center justify-between gap-3">
              <div>
                <h2 className="text-xl font-semibold">Current users</h2>
                <p className="mt-1 text-sm text-text-muted">
                  Pending users can receive a fresh invite link.
                </p>
              </div>
              <Button variant="outline" onClick={loadUsers} disabled={isLoadingUsers}>
                Refresh
              </Button>
            </div>

            <div className="mt-6 overflow-x-auto">
              <table className="min-w-full text-left text-sm">
                <thead className="border-b border-border text-text-muted">
                  <tr>
                    <th className="py-3 pr-4 font-medium">Name</th>
                    <th className="py-3 pr-4 font-medium">Role</th>
                    <th className="py-3 pr-4 font-medium">Status</th>
                    <th className="py-3 pr-4 font-medium">Email</th>
                    <th className="py-3 font-medium">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {isLoadingUsers ? (
                    <tr>
                      <td colSpan="5" className="py-6 text-text-muted">
                        Loading users...
                      </td>
                    </tr>
                  ) : users.length === 0 ? (
                    <tr>
                      <td colSpan="5" className="py-6 text-text-muted">
                        No users found yet.
                      </td>
                    </tr>
                  ) : (
                    users.map((user) => {
                      const fullName = [user.firstname, user.lastname]
                        .filter(Boolean)
                        .join(" ");
                      const canResend =
                        user.account_status === "pending" &&
                        user.role !== "admin" &&
                        user.role !== "superadmin";

                      return (
                        <tr key={user.id} className="border-b border-border/60">
                          <td className="py-4 pr-4">
                            {fullName || "No name"}
                          </td>
                          <td className="py-4 pr-4 capitalize">{user.role}</td>
                          <td className="py-4 pr-4 capitalize">
                            {user.account_status}
                          </td>
                          <td className="py-4 pr-4">{user.email}</td>
                          <td className="py-4">
                            <div className="flex flex-wrap items-center gap-2">
                            {canResend ? (
                              <Button
                                variant="outline"
                                size="small"
                                onClick={() => handleResendInvite(user.id)}
                                disabled={resendingUserId === user.id}
                              >
                                {resendingUserId === user.id
                                  ? "Sending..."
                                  : "Resend invite"}
                              </Button>
                            ) : (
                              <span className="text-text-muted">
                                {user.account_status === "active" ? "Active" : "Not available"}
                              </span>
                            )}
                            {user.role !== "admin" && user.role !== "superadmin" && (
                              <Button
                                variant="danger"
                                size="small"
                                onClick={() => handleDeleteUser(user)}
                                disabled={deletingUserId === user.id}
                              >
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
      </div>
    </div>
  );
}

export default UserManagementPage;
