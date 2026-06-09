import { useCallback, useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import Card from "../../components/ui/Card";
import Button from "../../components/ui/Button";
import Input from "../../components/ui/Input";
import { authService } from "../../services/auth.service";
import { getErrorMessage, parseApiError } from "../../services/api";
import { superadminService } from "../../services/superadmin.service";

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

const INITIAL_SUPERADMIN_FORM = {
  email: "",
};

const toNullable = (value) => {
  const trimmed = String(value || "").trim();
  return trimmed ? trimmed : null;
};

function SuperadminDashboardPage() {
  const navigate = useNavigate();
  const [tenants, setTenants] = useState([]);
  const [superadmins, setSuperadmins] = useState([]);
  const [tenantFormData, setTenantFormData] = useState(INITIAL_TENANT_FORM);
  const [superadminFormData, setSuperadminFormData] = useState(INITIAL_SUPERADMIN_FORM);
  const [restoreTenantId, setRestoreTenantId] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isCreatingTenant, setIsCreatingTenant] = useState(false);
  const [isInvitingSuperadmin, setIsInvitingSuperadmin] = useState(false);
  const [isRestoringById, setIsRestoringById] = useState(false);
  const [activeTenantAction, setActiveTenantAction] = useState(null);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);
  const [superadminFieldErrors, setSuperadminFieldErrors] = useState({});

  const loadDashboardData = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const [tenantResult, superadminResult] = await Promise.all([
        superadminService.getTenants(),
        superadminService.getSuperadmins(),
      ]);

      setTenants(Array.isArray(tenantResult) ? tenantResult : []);
      setSuperadmins(Array.isArray(superadminResult) ? superadminResult : []);
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

  const handleTenantFormChange = (event) => {
    const { name, value } = event.target;
    setTenantFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSuperadminFormChange = (event) => {
    const { name, value } = event.target;
    setSuperadminFormData((prev) => ({ ...prev, [name]: value }));
    setSuperadminFieldErrors((prev) => ({ ...prev, [name]: undefined }));
  };

  const handleCreateTenant = async (event) => {
    event.preventDefault();
    setIsCreatingTenant(true);
    setError(null);
    setSuccessMessage(null);

    try {
      await superadminService.createTenant({
        school_name: tenantFormData.school_name,
        email: tenantFormData.email,
        phone: toNullable(tenantFormData.phone),
        school_bot_whatssap_number: toNullable(
          tenantFormData.school_bot_whatssap_number
        ),
        plan: tenantFormData.plan,
        max_students: Number(tenantFormData.max_students),
        max_teachers: Number(tenantFormData.max_teachers),
      });

      setTenantFormData(INITIAL_TENANT_FORM);
      setSuccessMessage("Tenant created and activation email queued.");
      await loadDashboardData();
    } catch (err) {
      setError(getErrorMessage(err, "Failed to create tenant."));
    } finally {
      setIsCreatingTenant(false);
    }
  };

  const handleInviteSuperadmin = async (event) => {
    event.preventDefault();
    setIsInvitingSuperadmin(true);
    setError(null);
    setSuccessMessage(null);
    setSuperadminFieldErrors({});

    try {
      const result = await superadminService.inviteSuperadmin(superadminFormData);
      setSuperadminFormData(INITIAL_SUPERADMIN_FORM);
      setSuccessMessage(result?.detail || "Superadmin invite created and emailed successfully.");
      await loadDashboardData();
    } catch (err) {
      const apiError = parseApiError(err, "Failed to invite superadmin.");
      if (Object.keys(apiError.fieldErrors).length > 0) {
        setSuperadminFieldErrors(apiError.fieldErrors);
      }
      setError(apiError.message);
    } finally {
      setIsInvitingSuperadmin(false);
    }
  };

  const handleStatusChange = async (tenantId, status) => {
    setActiveTenantAction(`${tenantId}:status`);
    setError(null);
    setSuccessMessage(null);

    try {
      await superadminService.updateTenantStatus(tenantId, {
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
      await superadminService.deleteTenant(tenant.id);
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
      await superadminService.restoreTenant(tenant.id);
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
      await superadminService.restoreTenant(restoreTenantId.trim());
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
        <div className="flex h-16 items-center justify-between border-b border-border px-4">
          <Link to="/" className="flex items-center gap-3">
            <span className="text-lg font-bold">Learnly AI</span>
          </Link>
        </div>
        <nav className="space-y-2 p-4">
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
              Manage platform tenants and invite other superadmins without passing through tenant-scoped user flows.
            </p>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <Button variant="outline" size="small" onClick={loadDashboardData} disabled={isLoading}>
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
            <p className="text-sm text-text-muted">Superadmin accounts</p>
            <p className="mt-2 text-3xl font-bold">{superadmins.length}</p>
          </Card>
        </div>

        <div className="mt-6 grid gap-6 xl:grid-cols-[minmax(320px,0.8fr)_minmax(0,1.4fr)]">
          <div className="space-y-6">
            <Card className="p-6">
              <h2 className="text-xl font-semibold">Create tenant</h2>
              <p className="mt-1 text-sm text-text-muted">
                Creates an inactive school tenant and emails an activation link to its tenant-scoped admin.
              </p>

              <form onSubmit={handleCreateTenant} className="mt-5 space-y-4">
                <Input
                  label="School name"
                  name="school_name"
                  value={tenantFormData.school_name}
                  onChange={handleTenantFormChange}
                  required
                />
                <Input
                  label="Admin email"
                  type="email"
                  name="email"
                  value={tenantFormData.email}
                  onChange={handleTenantFormChange}
                  required
                />
                <Input
                  label="Phone"
                  name="phone"
                  value={tenantFormData.phone}
                  onChange={handleTenantFormChange}
                  placeholder="+2348012345678"
                />
                <Input
                  label="Bot WhatsApp number"
                  name="school_bot_whatssap_number"
                  value={tenantFormData.school_bot_whatssap_number}
                  onChange={handleTenantFormChange}
                  placeholder="+2348012345678"
                />

                <div>
                  <label className="mb-1.5 block text-sm font-medium text-text-soft">
                    Plan
                  </label>
                  <select
                    name="plan"
                    value={tenantFormData.plan}
                    onChange={handleTenantFormChange}
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
                    value={tenantFormData.max_students}
                    onChange={handleTenantFormChange}
                    required
                  />
                  <Input
                    label="Max teachers"
                    type="number"
                    min="1"
                    name="max_teachers"
                    value={tenantFormData.max_teachers}
                    onChange={handleTenantFormChange}
                    required
                  />
                </div>

                <Button type="submit" className="w-full" disabled={isCreatingTenant}>
                  {isCreatingTenant ? "Creating..." : "Create tenant"}
                </Button>
              </form>
            </Card>

            <Card className="p-6">
              <h2 className="text-xl font-semibold">Invite superadmin</h2>
              <p className="mt-1 text-sm text-text-muted">
                This creates a platform-level invite record only. The actual account is created or activated when the invite is accepted.
              </p>

              <form onSubmit={handleInviteSuperadmin} className="mt-5 space-y-4">
                <Input
                  label="Superadmin email"
                  type="email"
                  name="email"
                  value={superadminFormData.email}
                  onChange={handleSuperadminFormChange}
                  error={superadminFieldErrors.email}
                  required
                />

                <Button type="submit" className="w-full" disabled={isInvitingSuperadmin}>
                  {isInvitingSuperadmin ? "Sending invite..." : "Invite superadmin"}
                </Button>
              </form>
            </Card>

            <Card className="p-6">
              <h2 className="text-xl font-semibold">Restore tenant</h2>
              <p className="mt-1 text-sm text-text-muted">
                Deleted tenants appear in the table, but you can also restore directly by tenant ID.
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

          <div className="space-y-6">
            <Card className="p-6">
              <h2 className="text-xl font-semibold">Tenants</h2>
              <p className="mt-1 text-sm text-text-muted">
                Superadmins manage tenant records here. Tenant-user management stays inside tenant-admin flows.
              </p>

              <div className="mt-5 overflow-x-auto">
                <table className="min-w-full text-left text-sm">
                  <thead className="border-b border-border text-text-muted">
                    <tr>
                      <th className="py-3 pr-4 font-medium">School</th>
                      <th className="py-3 pr-4 font-medium">Status</th>
                      <th className="py-3 pr-4 font-medium">Plan</th>
                      <th className="py-3 pr-4 font-medium">Verification</th>
                      <th className="py-3 pr-4 font-medium">Deleted</th>
                      <th className="py-3 font-medium">Actions</th>
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
                            <td className="py-4 pr-4 capitalize">
                              {tenant.verification_status?.replace(/_/g, " ")}
                            </td>
                            <td className="py-4 pr-4">{isDeleted ? "Yes" : "No"}</td>
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

            <Card className="p-6">
              <h2 className="text-xl font-semibold">Superadmin accounts</h2>
              <p className="mt-1 text-sm text-text-muted">
                Active platform-level accounts live outside the tenant user table.
              </p>

              <div className="mt-4 overflow-x-auto">
                <table className="min-w-full text-left text-sm">
                  <thead className="border-b border-border text-text-muted">
                    <tr>
                      <th className="py-3 pr-4 font-medium">Email</th>
                      <th className="py-3 pr-4 font-medium">Status</th>
                      <th className="py-3 pr-4 font-medium">Last login</th>
                      <th className="py-3 font-medium">Created</th>
                    </tr>
                  </thead>
                  <tbody>
                    {isLoading ? (
                      <tr>
                        <td colSpan="4" className="py-6 text-text-muted">
                          Loading superadmins...
                        </td>
                      </tr>
                    ) : superadmins.length === 0 ? (
                      <tr>
                        <td colSpan="4" className="py-6 text-text-muted">
                          No superadmin accounts found.
                        </td>
                      </tr>
                    ) : (
                      superadmins.map((superadmin) => (
                        <tr key={superadmin.id} className="border-b border-border/60">
                          <td className="py-4 pr-4">{superadmin.email}</td>
                          <td className="py-4 pr-4">
                            {superadmin.is_active ? "active" : "inactive"}
                          </td>
                          <td className="py-4 pr-4">
                            {superadmin.last_login_at || "Never"}
                          </td>
                          <td className="py-4">{superadmin.created_at}</td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </Card>
          </div>
        </div>
      </main>
    </div>
  );
}

export default SuperadminDashboardPage;
