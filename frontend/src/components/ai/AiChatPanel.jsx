import { Sparkles, X } from "lucide-react";
import Button from "../ui/Button";

function AiChatPanel({ open, onClose }) {
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-end bg-slate-950/20 p-4 backdrop-blur-sm sm:items-end">
      <div className="w-full max-w-md rounded-3xl border border-border bg-surface shadow-premium">
        <div className="flex items-center justify-between border-b border-border px-5 py-4">
          <div>
            <p className="text-sm font-semibold text-text">AI Assistant</p>
            <p className="mt-1 text-xs text-text-muted">Placeholder panel for future assistant workflows.</p>
          </div>
          <Button type="button" variant="ghost" size="icon" onClick={onClose} aria-label="Close AI assistant">
            <X className="h-4 w-4" />
          </Button>
        </div>

        <div className="space-y-4 px-5 py-5">
          <div className="rounded-2xl border border-primary/15 bg-primary-subtle px-4 py-4 text-sm text-text-soft">
            <div className="flex items-center gap-2 font-semibold text-primary">
              <Sparkles className="h-4 w-4" />
              AI assistant coming soon.
            </div>
            <p className="mt-2 text-sm text-text-soft">
              This launcher is wired so we can connect a real assistant API later without changing every dashboard.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default AiChatPanel;
