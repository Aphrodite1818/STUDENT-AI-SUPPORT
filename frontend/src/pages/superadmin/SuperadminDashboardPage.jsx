import { useCallback, useEffect, useState } from "react";
import { Building2, CheckCircle2, Clock3, RefreshCw, Shield, Trash2, Undo2, UserPlus } from "lucide-react";
import DashboardLayout from "../../components/layout/DashboardLayout";
import Card from "../../components/ui/Card";
import Button from "../../components/ui/Button";
import Input from "../../components/ui/Input";
import Badge from "../../components/ui/Badge";
import StatCard from "../../components/shared/StatCard";
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

const INITIAL_SUPERADMIN_FORM = { email: "" };

const toNullable = (value) => {
  const trimmed = String(value || "").trim();
  return trimmed ? trimmed : null;
};

const statusVariant = (status) => {
  if (status === "active") return "success";
  if (status === "suspended" || status === "expired") return "error";
  if (status === "trial") return "warning";
  return "default";
};

function SuperadminDashboardPage() {
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
    const timeoutId = window.setTimeout(loadDashboardData, 0);
    return () => window.clearTimeout(timeoutId);
  }, [loadDashboardData]);

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
        school_bot_whatssap_number: toNullable(tenantFormData.school_bot_whatssap_number),
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
    if (!window.confirm(`Delete ${tenant.school_name}? This is a soft delete.`)) return;

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

  const activeTenants = tenants.filter((tenant) => tenant.status === "active" && !tenant.is_deleted).length;
  const pendingTenants = tenants.filter((tenant) => tenant.verification_status === "pending_verification").length;
  const suspendedTenants = tenants.filter((tenant) => tenant.status === "suspended").length;

  return (
    <DashboardLayout
      role="superadmin"
      title="Platform Dashboard"
      description="Manage school tenants, verification activity, and platform-level administrator access."
      actions={
        <Button variant="outline" onClick={loadDashboardData} disabled={isLoading}>
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

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Total Schools" value={tenants.length} icon={Building2} tone="primary" description="registered tenants" />
        <StatCard label="Active Schools" value={activeTenants} icon={CheckCircle2} tone="success" description="currently active" />
        <StatCard label="Pending Schools" value={pendingTenants} icon={Clock3} tone="warning" description="awaiting verification" />
        <StatCard label="Suspended Schools" value={suspendedTenants} icon={Shield} tone="error" description="restricted tenants" />
      </section>

      <section className="grid gap-6 xl:grid-cols-[380px_minmax(0,1fr)]">
        <div className="space-y-6">
          <Card className="p-5">
            <h2 className="text-lg font-semibold">Create tenant</h2>
            <p className="mt-1 text-sm text-text-muted">
              Create a school tenant and queue an activation email for its admin.
            </p>
            <form onSubmit={handleCreateTenant} className="mt-5 space-y-4">
              <Input label="School name" name="school_name" value={tenantFormData.school_name} onChange={handleTenantFormChange} required />
              <Input label="Admin email" type="email" name="email" value={tenantFormData.email} onChange={handleTenantFormChange} required />
              <Input label="Phone" name="phone" value={tenantFormData.phone} onChange={handleTenantFormChange} placeholder="+2348012345678" />
              <Input label="Bot WhatsApp number" name="school_bot_whatssap_number" value={tenantFormData.school_bot_whatssap_number} onChange={handleTenantFormChange} placeholder="+2348012345678" />
              <div>
                <label className="mb-1.5 block text-sm font-medium text-text-soft">Plan</label>
                <select name="plan" value={tenantFormData.plan} onChange={handleTenantFormChange} className="input-base">
                  {PLAN_OPTIONS.map((plan) => (
                    <option key={plan} value={plan}>{plan}</option>
                  ))}
                </select>
              </div>
              <div className="grid gap-4 sm:grid-cols-2">
                <Input label="Max students" type="number" min="1" name="max_students" value={tenantFormData.max_students} onChange={handleTenantFormChange} required />
                <Input label="Max teachers" type="number" min="1" name="max_teachers" value={tenantFormData.max_teachers} onChange={handleTenantFormChange} required />
              </div>
              <Button type="submit" className="w-full" disabled={isCreatingTenant}>
                {isCreatingTenant ? "Creating..." : "Create tenant"}
              </Button>
            </form>
          </Card>

          <Card className="p-5">
            <h2 className="text-lg font-semibold">Invite superadmin</h2>
            <form onSubmit={handleInviteSuperadmin} className="mt-5 space-y-4">
              <Input label="Superadmin email" type="email" name="email" value={superadminFormData.email} onChange={handleSuperadminFormChange} error={superadminFieldErrors.email} required />
              <Button type="submit" className="w-full" disabled={isInvitingSuperadmin}>
                <UserPlus className="h-4 w-4" />
                {isInvitingSuperadmin ? "Sending invite..." : "Invite superadmin"}
              </Button>
            </form>
          </Card>

          <Card className="p-5">
            <h2 className="text-lg font-semibold">Restore tenant</h2>
            <form onSubmit={handleRestoreTenantById} className="mt-5 space-y-4">
              <Input label="Tenant ID" name="restoreTenantId" value={restoreTenantId} onChange={(event) => setRestoreTenantId(event.target.value)} placeholder="00000000-0000-0000-0000-000000000000" required />
              <Button type="submit" variant="outline" className="w-full" disabled={isRestoringById || !restoreTenantId.trim()}>
                {isRestoringById ? "Restoring..." : "Restore tenant"}
              </Button>
            </form>
          </Card>
        </div>

        <div className="space-y-6">
          <Card className="p-5">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <h2 className="text-lg font-semibold">Tenant Management</h2>
                <p className="text-sm text-text-muted">Status, plan, verification, and deletion controls.</p>
              </div>
              <Badge variant="primary">{tenants.length} schools</Badge>
            </div>
            <div className="mt-5 table-wrap">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>School</th>
                    <th>Status</th>
                    <th>Plan</th>
                    <th>Verification</th>
                    <th>Deleted</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {isLoading ? (
                    <tr><td colSpan="6" className="text-text-muted">Loading tenants...</td></tr>
                  ) : tenants.length === 0 ? (
                    <tr><td colSpan="6" className="text-text-muted">No tenants found.</td></tr>
                  ) : (
                    tenants.map((tenant) => {
                      const isDeleted = Boolean(tenant.is_deleted);
                      return (
                        <tr key={tenant.id}>
                          <td>
                            <p className="font-semibold">{tenant.school_name}</p>
                            <p className="text-xs text-text-muted">{tenant.email}</p>
                          </td>
                          <td>
                            <select
                              value={tenant.status}
                              onChange={(event) => handleStatusChange(tenant.id, event.target.value)}
                              disabled={isDeleted || activeTenantAction === `${tenant.id}:status`}
                              className="input-base min-w-32 py-1.5 text-xs capitalize"
                            >
                              {STATUS_OPTIONS.map((status) => (
                                <option key={status} value={status}>{status}</option>
                              ))}
                            </select>
                          </td>
                          <td className="capitalize">{tenant.plan}</td>
                          <td>
                            <Badge variant={tenant.verification_status === "verified" ? "success" : "warning"}>
                              {tenant.verification_status?.replace(/_/g, " ") || "pending"}
                            </Badge>
                          </td>
                          <td>{isDeleted ? <Badge variant="error">Yes</Badge> : <Badge variant={statusVariant(tenant.status)}>No</Badge>}</td>
                          <td>
                            {isDeleted ? (
                              <Button variant="outline" size="sm" onClick={() => handleRestoreTenant(tenant)} disabled={activeTenantAction === `${tenant.id}:restore`}>
                                <Undo2 className="h-4 w-4" />
                                Restore
                              </Button>
                            ) : (
                              <Button variant="danger" size="sm" onClick={() => handleDeleteTenant(tenant)} disabled={activeTenantAction === `${tenant.id}:delete`}>
                                <Trash2 className="h-4 w-4" />
                                Delete
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

          <Card className="p-5">
            <h2 className="text-lg font-semibold">Platform Activity</h2>
            <div className="mt-5 table-wrap">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Email</th>
                    <th>Status</th>
                    <th>Last login</th>
                    <th>Created</th>
                  </tr>
                </thead>
                <tbody>
                  {isLoading ? (
                    <tr><td colSpan="4" className="text-text-muted">Loading superadmins...</td></tr>
                  ) : superadmins.length === 0 ? (
                    <tr><td colSpan="4" className="text-text-muted">No superadmin accounts found.</td></tr>
                  ) : (
                    superadmins.map((superadmin) => (
                      <tr key={superadmin.id}>
                        <td>{superadmin.email}</td>
                        <td><Badge variant={superadmin.is_active ? "success" : "default"}>{superadmin.is_active ? "active" : "inactive"}</Badge></td>
                        <td>{superadmin.last_login_at || "Never"}</td>
                        <td>{superadmin.created_at}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </Card>
        </div>
      </section>
    </DashboardLayout>
  );
}

export default SuperadminDashboardPage;
