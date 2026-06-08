import { useCallback, useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import Card from "../../components/ui/Card";
import Button from "../../components/ui/Button";
import Input from "../../components/ui/Input";
import { authService } from "../../services/auth.service";
import { getErrorMessage } from "../../services/api";
import { tenantService } from "../../services/tenant.service";
import { userService } from "../../services/user.service";

const STATUS_OPTIONS = ["active", "inactive", "suspended", "trial", "expired"];
const PLAN_OPTIONS = ["free", "starter", "pro", "enterprise"];

const INITIAL_TENANT_FORM = {
  school_name: "",
  email: "",
  phone: "",
  school_bot_whatssap_number: "",
  plan: "free",
  max_students: 500,
  max_teachers: 50,
};

const toNullable = (value) => {
  const trimmed = String(value || "").trim();
  return trimmed ? trimmed : null;
};

function SuperadminDashboardPage() {
  const navigate = useNavigate();
  const [tenants, setTenants] = useState([]);
  const [users, setUsers] = useState([]);
  const [formData, setFormData] = useState(INITIAL_TENANT_FORM);
  const [restoreTenantId, setRestoreTenantId] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isCreating, setIsCreating] = useState(false);
  const [isRestoringById, setIsRestoringById] = useState(false);
  const [activeTenantAction, setActiveTenantAction] = useState(null);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);

  const loadDashboardData = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const [tenantResult, userResult] = await Promise.all([
        tenantService.getAllTenants(),
        userService.getUsers(0, 100),
      ]);

      setTenants(Array.isArray(tenantResult) ? tenantResult : []);
      setUsers(Array.isArray(userResult) ? userResult : []);
    } catch (err) {
      setError(getErrorMessage(err, "Failed to load superadmin data."));
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    const timeoutId = window.setTimeout(() => {
      loadDashboardData();
    }, 0);

    return () => window.clearTimeout(timeoutId);
  }, [loadDashboardData]);

  const handleLogout = () => {
    authService.logout();
    navigate("/login", { replace: true });
  };

  const handleFormChange = (event) => {
    const { name, value } = event.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleCreateTenant = async (event) => {
    event.preventDefault();
    setIsCreating(true);
    setError(null);
    setSuccessMessage(null);

    try {
      await tenantService.createTenant({
        school_name: formData.school_name,
        email: formData.email,
        phone: toNullable(formData.phone),
        school_bot_whatssap_number: toNullable(
          formData.school_bot_whatssap_number
        ),
        plan: formData.plan,
        max_students: Number(formData.max_students),
        max_teachers: Number(formData.max_teachers),
      });

      setFormData(INITIAL_TENANT_FORM);
      setSuccessMessage("Tenant created and activation email queued.");
      await loadDashboardData();
    } catch (err) {
      setError(getErrorMessage(err, "Failed to create tenant."));
    } finally {
      setIsCreating(false);
    }
  };

  const handleStatusChange = async (tenantId, status) => {
    setActiveTenantAction(`${tenantId}:status`);
    setError(null);
    setSuccessMessage(null);

    try {
      await tenantService.updateTenantStatus(tenantId, {
        status,
        reason: "Updated from the superadmin dashboard.",
      });
      setSuccessMessage("Tenant status updated.");
      await loadDashboardData();
    } catch (err) {
      setError(getErrorMessage(err, "Failed to update tenant status."));
    } finally {
      setActiveTenantAction(null);
    }
  };

  const handleDeleteTenant = async (tenant) => {
    if (!window.confirm(`Delete ${tenant.school_name}? This is a soft delete.`)) {
      return;
    }

    setActiveTenantAction(`${tenant.id}:delete`);
    setError(null);
    setSuccessMessage(null);

    try {
      await tenantService.deleteTenant(tenant.id);
      setSuccessMessage("Tenant deleted.");
      await loadDashboardData();
    } catch (err) {
      setError(getErrorMessage(err, "Failed to delete tenant."));
    } finally {
      setActiveTenantAction(null);
    }
  };

  const handleRestoreTenant = async (tenant) => {
    setActiveTenantAction(`${tenant.id}:restore`);
    setError(null);
    setSuccessMessage(null);

    try {
      await tenantService.restoreTenant(tenant.id);
      setSuccessMessage("Tenant restored.");
      await loadDashboardData();
    } catch (err) {
      setError(getErrorMessage(err, "Failed to restore tenant."));
    } finally {
      setActiveTenantAction(null);
    }
  };

  const handleRestoreTenantById = async (event) => {
    event.preventDefault();
    setIsRestoringById(true);
    setError(null);
    setSuccessMessage(null);

    try {
      await tenantService.restoreTenant(restoreTenantId.trim());
      setRestoreTenantId("");
      setSuccessMessage("Tenant restored.");
      await loadDashboardData();
    } catch (err) {
      setError(getErrorMessage(err, "Failed to restore tenant."));
    } finally {
      setIsRestoringById(false);
    }
  };

  const activeTenants = tenants.filter(
    (tenant) => tenant.status === "active" && !tenant.is_deleted
  ).length;
  const pendingTenants = tenants.filter(
    (tenant) => tenant.verification_status === "pending_verification"
  ).length;

  return (
    <div className="min-h-screen bg-background text-text md:flex">
      <aside className="border-b border-border bg-surface md:min-h-screen md:w-64 md:border-b-0 md:border-r">
        <div className="h-16 flex items-center justify-between px-4 border-b border-border">
          <Link to="/" className="flex items-center gap-3">
            <span className="font-bold text-lg">Learnly AI</span>
          </Link>
        </div>
        <nav className="p-4 space-y-2">
          <Link
            to="/superadmin/dashboard"
            className="flex items-center gap-3 rounded-lg bg-primary/10 px-3 py-2.5 text-primary"
          >
            <span>Dashboard</span>
          </Link>
        </nav>
      </aside>

      <main className="flex-1 p-6 md:p-8">
        <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl font-bold">Superadmin Dashboard</h1>
            <p className="mt-1 text-sm text-text-muted">
              Manage tenants already exposed by the platform API.
            </p>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <Button
              variant="outline"
              size="small"
              onClick={loadDashboardData}
              disabled={isLoading}
            >
              Refresh
            </Button>
            <Button variant="secondary" size="small" onClick={handleLogout}>
              Logout
            </Button>
          </div>
        </div>

        {error && (
          <div className="mb-4 rounded-md border border-red-500/40 bg-red-500/10 px-4 py-3 text-sm text-red-600">
            {error}
          </div>
        )}

        {successMessage && (
          <div className="mb-4 rounded-md border border-green-500/40 bg-green-500/10 px-4 py-3 text-sm text-green-700">
            {successMessage}
          </div>
        )}

        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <Card className="p-5">
            <p className="text-sm text-text-muted">Total tenants</p>
            <p className="mt-2 text-3xl font-bold">{tenants.length}</p>
          </Card>
          <Card className="p-5">
            <p className="text-sm text-text-muted">Active tenants</p>
            <p className="mt-2 text-3xl font-bold">{activeTenants}</p>
          </Card>
          <Card className="p-5">
            <p className="text-sm text-text-muted">Pending verification</p>
            <p className="mt-2 text-3xl font-bold">{pendingTenants}</p>
          </Card>
          <Card className="p-5">
            <p className="text-sm text-text-muted">Platform users</p>
            <p className="mt-2 text-3xl font-bold">{users.length}</p>
          </Card>
        </div>

        <div className="mt-6 grid gap-6 xl:grid-cols-[minmax(320px,0.75fr)_minmax(0,1.5fr)]">
          <div className="space-y-6">
            <Card className="p-6">
              <h2 className="text-xl font-semibold">Create tenant</h2>
              <p className="mt-1 text-sm text-text-muted">
                Creates an inactive school tenant and sends its admin activation link.
              </p>

              <form onSubmit={handleCreateTenant} className="mt-5 space-y-4">
                <Input
                  label="School name"
                  name="school_name"
                  value={formData.school_name}
                  onChange={handleFormChange}
                  required
                />
                <Input
                  label="Admin email"
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleFormChange}
                  required
                />
                <Input
                  label="Phone"
                  name="phone"
                  value={formData.phone}
                  onChange={handleFormChange}
                  placeholder="+2348012345678"
                />
                <Input
                  label="Bot WhatsApp number"
                  name="school_bot_whatssap_number"
                  value={formData.school_bot_whatssap_number}
                  onChange={handleFormChange}
                  placeholder="+2348012345678"
                />

                <div>
                  <label className="mb-1.5 block text-sm font-medium text-text-soft">
                    Plan
                  </label>
                  <select
                    name="plan"
                    value={formData.plan}
                    onChange={handleFormChange}
                    className="input-base"
                  >
                    {PLAN_OPTIONS.map((plan) => (
                      <option key={plan} value={plan}>
                        {plan}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="grid gap-4 sm:grid-cols-2">
                  <Input
                    label="Max students"
                    type="number"
                    min="1"
                    name="max_students"
                    value={formData.max_students}
                    onChange={handleFormChange}
                    required
                  />
                  <Input
                    label="Max teachers"
                    type="number"
                    min="1"
                    name="max_teachers"
                    value={formData.max_teachers}
                    onChange={handleFormChange}
                    required
                  />
                </div>

                <Button type="submit" className="w-full" disabled={isCreating}>
                  {isCreating ? "Creating..." : "Create tenant"}
                </Button>
              </form>
            </Card>

            <Card className="p-6">
              <h2 className="text-xl font-semibold">Restore tenant</h2>
              <p className="mt-1 text-sm text-text-muted">
                Soft-deleted tenants are not returned by the tenant list, so restore requires the tenant ID.
              </p>
              <form onSubmit={handleRestoreTenantById} className="mt-5 space-y-4">
                <Input
                  label="Tenant ID"
                  name="restoreTenantId"
                  value={restoreTenantId}
                  onChange={(event) => setRestoreTenantId(event.target.value)}
                  placeholder="00000000-0000-0000-0000-000000000000"
                  required
                />
                <Button
                  type="submit"
                  variant="outline"
                  className="w-full"
                  disabled={isRestoringById || !restoreTenantId.trim()}
                >
                  {isRestoringById ? "Restoring..." : "Restore tenant"}
                </Button>
              </form>
            </Card>
          </div>

          <Card className="p-6">
            <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <h2 className="text-xl font-semibold">Tenants</h2>
                <p className="mt-1 text-sm text-text-muted">
                  List, status update, soft delete, and restore are backed by real endpoints.
                </p>
              </div>
            </div>

            <div className="mt-5 overflow-x-auto">
              <table className="min-w-full text-left text-sm">
                <thead className="border-b border-border text-text-muted">
                  <tr>
                    <th className="py-3 pr-4 font-medium">School</th>
                    <th className="py-3 pr-4 font-medium">Status</th>
                    <th className="py-3 pr-4 font-medium">Plan</th>
                    <th className="py-3 pr-4 font-medium">Limits</th>
                    <th className="py-3 pr-4 font-medium">Verification</th>
                    <th className="py-3 font-medium">Action</th>
                  </tr>
                </thead>
                <tbody>
                  {isLoading ? (
                    <tr>
                      <td colSpan="6" className="py-6 text-text-muted">
                        Loading tenants...
                      </td>
                    </tr>
                  ) : tenants.length === 0 ? (
                    <tr>
                      <td colSpan="6" className="py-6 text-text-muted">
                        No tenants found.
                      </td>
                    </tr>
                  ) : (
                    tenants.map((tenant) => {
                      const isDeleted = Boolean(tenant.is_deleted);

                      return (
                        <tr key={tenant.id} className="border-b border-border/60">
                          <td className="py-4 pr-4">
                            <p className="font-medium">{tenant.school_name}</p>
                            <p className="text-xs text-text-muted">{tenant.email}</p>
                          </td>
                          <td className="py-4 pr-4">
                            <select
                              value={tenant.status}
                              onChange={(event) =>
                                handleStatusChange(tenant.id, event.target.value)
                              }
                              disabled={
                                isDeleted ||
                                activeTenantAction === `${tenant.id}:status`
                              }
                              className="input-base min-w-32 py-1.5 text-xs capitalize"
                            >
                              {STATUS_OPTIONS.map((status) => (
                                <option key={status} value={status}>
                                  {status}
                                </option>
                              ))}
                            </select>
                          </td>
                          <td className="py-4 pr-4 capitalize">{tenant.plan}</td>
                          <td className="py-4 pr-4 text-text-muted">
                            {tenant.max_students} students / {tenant.max_teachers} teachers
                          </td>
                          <td className="py-4 pr-4 capitalize">
                            {tenant.verification_status?.replace(/_/g, " ")}
                          </td>
                          <td className="py-4">
                            {isDeleted ? (
                              <Button
                                variant="outline"
                                size="small"
                                onClick={() => handleRestoreTenant(tenant)}
                                disabled={activeTenantAction === `${tenant.id}:restore`}
                              >
                                {activeTenantAction === `${tenant.id}:restore`
                                  ? "Restoring..."
                                  : "Restore"}
                              </Button>
                            ) : (
                              <Button
                                variant="danger"
                                size="small"
                                onClick={() => handleDeleteTenant(tenant)}
                                disabled={activeTenantAction === `${tenant.id}:delete`}
                              >
                                {activeTenantAction === `${tenant.id}:delete`
                                  ? "Deleting..."
                                  : "Delete"}
                              </Button>
                            )}
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

        <Card className="mt-6 p-6">
          <h2 className="text-xl font-semibold">Recent platform users</h2>
          <div className="mt-4 overflow-x-auto">
            <table className="min-w-full text-left text-sm">
              <thead className="border-b border-border text-text-muted">
                <tr>
                  <th className="py-3 pr-4 font-medium">Name</th>
                  <th className="py-3 pr-4 font-medium">Role</th>
                  <th className="py-3 pr-4 font-medium">Status</th>
                  <th className="py-3 font-medium">Email</th>
                </tr>
              </thead>
              <tbody>
                {isLoading ? (
                  <tr>
                    <td colSpan="4" className="py-6 text-text-muted">
                      Loading users...
                    </td>
                  </tr>
                ) : users.length === 0 ? (
                  <tr>
                    <td colSpan="4" className="py-6 text-text-muted">
                      No users found.
                    </td>
                  </tr>
                ) : (
                  users.slice(0, 8).map((user) => (
                    <tr key={user.id} className="border-b border-border/60">
                      <td className="py-4 pr-4">
                        {[user.firstname, user.lastname].filter(Boolean).join(" ") ||
                          "No name"}
                      </td>
                      <td className="py-4 pr-4 capitalize">{user.role}</td>
                      <td className="py-4 pr-4 capitalize">{user.account_status}</td>
                      <td className="py-4">{user.email}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </Card>
      </main>
    </div>
  );
}

export default SuperadminDashboardPage;
