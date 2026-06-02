/** TOAST COMPONENT **/

/**
 * @param {message} the message to appear
 * @param {type} the type of the toast, can be "info", "success", or "error". Defaults to "info".
 * @returns
 */
export default function Toast({ message, type = "info" }) {
  const colors = {
    info: "bg-primary text-white",
    success: "bg-success text-white",
    error: "bg-error text-white",
  };

  const icons = {
    info: "ℹ️",
    success: "✅",
    error: "❌",
  };

  return (
    <div
      className={`
        fixed bottom-6 right-6 z-50
        flex items-center gap-3
        px-5 py-3 rounded-xl
        shadow-strong text-sm font-medium
        animate-fadein
        ${colors[type]}
      `}
    >
      <span>{icons[type]}</span>
      <span>{message}</span>
    </div>
  );
}