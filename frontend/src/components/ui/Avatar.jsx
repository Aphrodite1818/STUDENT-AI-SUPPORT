import { cn } from "../../utils/cn";
import { getUserAvatarSrc, getUserDisplayName } from "../../utils/user";

const getInitial = (name = "") =>
  String(name).trim().charAt(0).toUpperCase() || "U";

const sizes = {
  sm: "h-8 w-8 text-xs",
  md: "h-10 w-10 text-sm",
  lg: "h-12 w-12 text-base",
  xl: "h-16 w-16 text-lg",
};

function Avatar({ name, src, size = "md", className = "", user }) {
  const displayName = name || (user ? getUserDisplayName(user) : "User");
  const imageSrc = src || (user ? getUserAvatarSrc(user) : undefined);

  return (
    <span
      className={cn(
        "inline-flex shrink-0 items-center justify-center overflow-hidden rounded-full bg-primary-soft font-bold text-primary ring-1 ring-border",
        sizes[size] || sizes.md,
        className
      )}
      aria-label={displayName}
      title={displayName}
    >
      {imageSrc ? (
        <img src={imageSrc} alt="" className="h-full w-full object-cover" />
      ) : (
        getInitial(displayName)
      )}
    </span>
  );
}

export default Avatar;
