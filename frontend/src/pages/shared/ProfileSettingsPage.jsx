import DashboardLayout from "../../components/layout/DashboardLayout";
import Card from "../../components/ui/Card";
import Avatar from "../../components/ui/Avatar";
import ProfileCompletionForm from "../../components/shared/ProfileCompletionForm";
import { authSession } from "../../services/api";
import { getUserDisplayName } from "../../utils/user";

function ProfileSettingsPage() {
  const user = authSession.getUser();
  const role = String(user?.role || authSession.getRole() || "admin").toLowerCase();
  const displayName = getUserDisplayName(user);

  return (
    <DashboardLayout
      role={role}
      title="Profile Settings"
      description="Manage the same account details used during onboarding."
    >
      <Card className="mx-auto max-w-3xl p-5 sm:p-6">
        <div className="flex items-center gap-4">
          <Avatar name={displayName} user={user} size="lg" />
          <div>
            <h2 className="text-xl font-semibold">{displayName || "User profile"}</h2>
            <p className="text-sm text-text-muted">
              Update your personal details and role-specific profile information here.
            </p>
          </div>
        </div>

        <div className="mt-6">
          <ProfileCompletionForm
            role={role}
            submitLabel="Save changes"
          />
        </div>
      </Card>
    </DashboardLayout>
  );
}

export default ProfileSettingsPage;
