const AVATAR_SRC_KEYS = [
  "profile_image_url",
  "avatar_url",
  "image_url",
  "photo_url",
  "passport_photo_url",
];

export function getUserDisplayName(user) {
  return (
    [user?.firstname, user?.lastname].filter(Boolean).join(" ") ||
    user?.email ||
    "User"
  );
}

export function getUserAvatarSrc(user) {
  if (!user) return undefined;

  for (const key of AVATAR_SRC_KEYS) {
    const value = user[key];
    if (typeof value === "string" && value.trim()) {
      return value.trim();
    }
  }

  return undefined;
}
