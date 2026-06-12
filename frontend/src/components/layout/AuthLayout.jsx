import { Link } from "react-router-dom";
import { CheckCircle2, ShieldCheck, Sparkles } from "lucide-react";
import logoImage from "../../assets/images/favicon.png";
import Card from "../ui/Card";

function AuthLayout({
  title,
  description,
  children,
  footer,
  stepLabel = "Secure school workspace",
}) {
  return (
    <div className="min-h-screen bg-background px-4 py-8 text-text sm:px-6 lg:grid lg:grid-cols-[minmax(0,0.95fr)_minmax(420px,0.65fr)] lg:px-0 lg:py-0">
      <section className="hidden border-r border-border bg-surface lg:flex lg:flex-col lg:justify-between lg:px-12 lg:py-10">
        <Link to="/" className="flex items-center gap-3">
          <img src={logoImage} alt="Learnly AI" className="h-11 w-11 rounded-2xl border border-border bg-white p-1" />
          <div>
            <p className="text-lg font-bold">Learnly AI</p>
            <p className="text-xs font-medium text-text-muted">School Management</p>
          </div>
        </Link>

        <div className="max-w-xl">
          <span className="inline-flex items-center gap-2 rounded-full border border-border bg-primary-subtle px-3 py-1.5 text-sm font-semibold text-primary">
            <Sparkles className="h-4 w-4" />
            Premium school operations
          </span>
          <h1 className="mt-6 text-5xl font-semibold leading-tight tracking-tight">
            Calm, secure access for every school role.
          </h1>
          <p className="mt-5 max-w-lg text-base leading-7 text-text-muted">
            One workspace for administrators, teachers, parents, and learners to manage daily school operations.
          </p>
        </div>

        <div className="grid gap-3">
          {[
            "Role-based access control",
            "Tenant-aware school workspaces",
            "Mobile-friendly authentication",
          ].map((item) => (
            <div key={item} className="flex items-center gap-3 rounded-2xl border border-border bg-background px-4 py-3 text-sm font-semibold text-text-soft">
              <CheckCircle2 className="h-4 w-4 text-success" />
              {item}
            </div>
          ))}
        </div>
      </section>

      <main className="flex min-h-[calc(100vh-4rem)] items-center justify-center lg:min-h-screen">
        <div className="w-full max-w-md">
          <Link to="/" className="mb-7 flex items-center justify-center gap-3 lg:hidden">
            <img src={logoImage} alt="Learnly AI" className="h-10 w-10 rounded-2xl border border-border bg-white p-1" />
            <div>
              <p className="font-bold">Learnly AI</p>
              <p className="text-xs text-text-muted">School Management</p>
            </div>
          </Link>

          <Card className="p-6 sm:p-8">
            <div className="mb-7 text-center">
              <span className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-primary-soft text-primary">
                <ShieldCheck className="h-5 w-5" />
              </span>
              <p className="mt-4 text-xs font-bold uppercase tracking-wide text-primary">
                {stepLabel}
              </p>
              <h1 className="mt-2 text-2xl font-semibold">{title}</h1>
              {description && (
                <p className="mt-2 text-sm leading-6 text-text-muted">{description}</p>
              )}
            </div>
            {children}
            {footer}
          </Card>
        </div>
      </main>
    </div>
  );
}

export default AuthLayout;
