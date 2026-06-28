import { useEffect, useState } from "react";
import { CheckCircle2, AlertCircle, Info, X } from "lucide-react";
import { cn } from "../../utils/cn";
import { toastBus } from "../../hooks/useToast";

const toneClasses = {
  info: "border-primary/25 bg-surface text-text",
  success: "border-success/25 bg-surface text-text",
  error: "border-error/25 bg-surface text-text",
};

const iconClasses = {
  info: "text-primary",
  success: "text-success",
  error: "text-error",
};

const icons = {
  info: Info,
  success: CheckCircle2,
  error: AlertCircle,
};

function ToastCard({ toast, onClose }) {
  const Icon = icons[toast.type] || icons.info;

  useEffect(() => {
    const timeoutId = window.setTimeout(() => onClose(toast.id), toast.duration);
    return () => window.clearTimeout(timeoutId);
  }, [onClose, toast.duration, toast.id]);

  return (
    <div
      className={cn(
        "pointer-events-auto flex min-w-[280px] max-w-sm items-start gap-3 rounded-2xl border px-4 py-3 shadow-premium animate-fadein",
        toneClasses[toast.type] || toneClasses.info
      )}
      role="status"
      aria-live="polite"
    >
      <Icon className={cn("mt-0.5 h-5 w-5 shrink-0", iconClasses[toast.type] || iconClasses.info)} />
      <p className="min-w-0 flex-1 text-sm font-medium text-text-soft">{toast.message}</p>
      <button
        type="button"
        onClick={() => onClose(toast.id)}
        className="rounded-lg p-1 text-text-faint transition hover:bg-surface-muted hover:text-text"
        aria-label="Dismiss notification"
      >
        <X className="h-4 w-4" />
      </button>
    </div>
  );
}

export default function ToastHost() {
  const [toasts, setToasts] = useState([]);

  useEffect(() => {
    return toastBus.subscribe((nextToast) => {
      setToasts((current) => [...current, nextToast]);
    });
  }, []);

  const closeToast = (id) => {
    setToasts((current) => current.filter((toast) => toast.id !== id));
  };

  if (toasts.length === 0) return null;

  return (
    <div className="pointer-events-none fixed bottom-4 right-4 z-[80] flex w-[calc(100vw-2rem)] max-w-sm flex-col gap-3 sm:bottom-6 sm:right-6">
      {toasts.map((toast) => (
        <ToastCard key={toast.id} toast={toast} onClose={closeToast} />
      ))}
    </div>
  );
}
