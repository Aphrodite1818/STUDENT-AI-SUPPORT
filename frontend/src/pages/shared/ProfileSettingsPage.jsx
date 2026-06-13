import { useState } from "react";
import { UserRound } from "lucide-react";
import DashboardLayout from "../../components/layout/DashboardLayout";
import Card from "../../components/ui/Card";
import Input from "../../components/ui/Input";
import Button from "../../components/ui/Button";
import Avatar from "../../components/ui/Avatar";
import { authSession, parseApiError } from "../../services/api";
import { userService } from "../../services/user.service";
import { getUserDisplayName } from "../../utils/user";

function ProfileSettingsPage() {
  const user = authSession.getUser();
  const role = String(user?.role || authSession.getRole() || "admin").toLowerCase();
  const [formData, setFormData] = useState({
    firstname: user?.firstname || "",
    lastname: user?.lastname || "",
    email: user?.email || "",
    phone_number: user?.phone_number || "",
    whatsapp_id: user?.whatsapp_id || "",
  });
  const [fieldErrors, setFieldErrors] = useState({});
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const displayName = getUserDisplayName({ ...user, ...formData });

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormData((current) => ({ ...current, [name]: value }));
    setFieldErrors((current) => ({ ...current, [name]: undefined }));
    setError(null);
    setSuccessMessage(null);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!user?.id) return;

    setIsSubmitting(true);
    setFieldErrors({});
    setError(null);
    setSuccessMessage(null);

    try {
      const updatedUser = await userService.updateProfile(user.id, {
        firstname: formData.firstname,
        lastname: formData.lastname,
        email: formData.email,
        phone_number: formData.phone_number,
        whatsapp_id: formData.whatsapp_id || null,
      });

      authSession.setUser({ ...user, ...updatedUser });
      setSuccessMessage("Profile updated successfully.");
    } catch (err) {
      const parsed = parseApiError(err, "Failed to update profile.");
      setFieldErrors(parsed.fieldErrors || {});
      setError(parsed.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <DashboardLayout
      role={role}
      title="Profile Settings"
      description="Manage your personal account details."
    >
      <Card className="mx-auto max-w-3xl p-5 sm:p-6">
        <div className="flex items-center gap-4">
          <Avatar name={displayName} user={user} size="lg" />
          <div>
            <h2 className="text-xl font-semibold">{displayName || "User profile"}</h2>
            <p className="text-sm text-text-muted">Profile image upload will be available when the backend exposes file storage.</p>
          </div>
        </div>

        {error && (
          <div className="mt-5 rounded-2xl border border-error/30 bg-error-soft px-4 py-3 text-sm font-medium text-error">
            {error}
          </div>
        )}
        {successMessage && (
          <div className="mt-5 rounded-2xl border border-success/30 bg-success-soft px-4 py-3 text-sm font-medium text-emerald-700">
            {successMessage}
          </div>
        )}

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
          <Button type="submit" disabled={isSubmitting}>
            <UserRound className="h-4 w-4" />
            {isSubmitting ? "Saving..." : "Save changes"}
          </Button>
        </form>
      </Card>
    </DashboardLayout>
  );
}

export default ProfileSettingsPage;
