import  { useState } from "react";
import { Link } from "react-router-dom";
import AppIcon from "../../components/ui/AppIcon";

const features = [
  {
    title: "WhatsApp assistant",
    description:
      "Parents get instant answers about attendance, assignments, school updates, and academic records without waiting for staff responses.",
    stat: "24/7",
    icon: "whatsapp",
  },
  {
    title: "Academic workspace",
    description:
      "Teachers and school administrators manage exams, attendance, assignments, student records, and communication from one dashboard.",
    stat: "One hub",
    icon: "school",
  },
  {
    title: "Operations insight",
    description:
      "Track engagement, AI response quality, communication activity, and operational performance with live analytics.",
    stat: "Live data",
    icon: "chart",
  },
];

const modules = [
  "Attendance tracking",
  "Assignment updates",
  "Exam schedules",
  "Fee reminders",
  "Teacher access",
  "Announcement broadcasts",
  "Result management",
  "Parent engagement",
  "School analytics",
];

const pricingPlans = [
  {
    name: "Starter",
    price: "COMING SOON",
    description:
      "For schools beginning digital parent communication and workflow automation.",
    features: [
      "School onboarding",
      "WhatsApp AI assistant",
      "Attendance management",
      "Assignment updates",
      "Parent messaging",
    ],
  },
  {
    name: "Growth",
    price: "COMING SOON",
    description:
      "For growing schools that need deeper automation and operational visibility.",
    features: [
      "Everything in Starter",
      "AI analytics",
      "Teacher management",
      "Fee management",
      "Priority support",
      "Advanced reports",
    ],
    highlighted: true,
  },
  {
    name: "Enterprise",
    price: "Custom",
    description:
      "For large institutions and multi-campus schools with advanced workflows.",
    features: [
      "Custom integrations",
      "Dedicated onboarding",
      "Advanced infrastructure",
      "Custom reporting",
      "Priority support",
      "Multi-campus support",
    ],
  },
];

const steps = [
  "A parent sends a WhatsApp message",
  "Learnly AI understands the request",
  "The system checks school records instantly",
  "The parent receives a clear response",
];

function LandingPage() {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  return (
    <div className="min-h-screen overflow-x-hidden bg-background text-text">
      <header className="sticky top-0 z-50 border-b border-border bg-surface/90 backdrop-blur-lg">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
          <a
            href="/"
            className="flex items-center gap-3 transition-opacity duration-300 hover:opacity-90"
          >
            <img
              src="frontend/src/assets/images/favicon.png"
              alt="Learnly AI logo"
              className="h-11 w-11 rounded-xl  border-border bg-surface p-1.5 shadow-sm"
            />

            <div>
              <p className="text-lg font-extrabold tracking-tight text-text">
                Learnly AI
              </p>

              <p className="text-xs font-medium text-text-muted">
                AI school platform
              </p>
            </div>
          </a>

          <nav className="hidden items-center gap-7 md:flex">
            <a
              href="#features"
              className="text-sm font-semibold text-text-soft transition-colors duration-300 hover:text-primary"
            >
              Features
            </a>

            <a
              href="#pricing"
              className="text-sm font-semibold text-text-soft transition-colors duration-300 hover:text-primary"
            >
              Pricing
            </a>

            <Link
              to="/login"
              className="text-sm font-semibold text-text-soft transition-colors duration-300 hover:text-primary"
            >
              Log in
            </Link>

            <Link
              to="/register"
              className="btn-base rounded-xl bg-primary px-5 py-2.5 text-sm font-semibold text-text transition-all duration-300 hover:-translate-y-0.5 hover:bg-primary-hover hover:text-text-inverse hover:shadow-lg hover:shadow-primary/20"
            >
              Join Learnly
            </Link>
          </nav>

          <button
            className="md:hidden flex items-center justify-center p-2 text-text transition-colors hover:text-primary"
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            aria-label="Toggle menu"
          >
            <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              {isMobileMenuOpen ? (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              ) : (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              )}
            </svg>
          </button>
        </div>

        {isMobileMenuOpen && (
          <div className="md:hidden border-t border-border bg-surface px-6 py-5 shadow-xl animate-fadein">
            <nav className="flex flex-col gap-5">
              <a
                href="#features"
                className="text-base font-semibold text-text-soft transition-colors hover:text-primary"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                Features
              </a>

              <a
                href="#pricing"
                className="text-base font-semibold text-text-soft transition-colors hover:text-primary"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                Pricing
              </a>

              <Link
                to="/login"
                className="text-base font-semibold text-text-soft transition-colors hover:text-primary"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                Log in
              </Link>

              <Link
                to="/register"
                className="btn-base mt-2 w-full rounded-xl bg-primary px-5 py-3 text-base font-semibold text-text transition-all hover:bg-primary-hover hover:text-text-inverse shadow-sm block text-center"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                Join Learnly
              </Link>
            </nav>
          </div>
        )}
      </header>

      <main>
        <section className="relative overflow-hidden border-b border-border">
          <div className="absolute inset-0 opacity-40">
            <div className="absolute left-[-100px] top-[-100px] h-72 w-72 rounded-full bg-primary/20 blur-3xl" />

            <div className="absolute bottom-[-120px] right-[-100px] h-80 w-80 rounded-full bg-accent/20 blur-3xl" />
          </div>

          <div className="relative mx-auto grid max-w-7xl gap-14 px-4 py-20 sm:px-6 lg:grid-cols-[1.05fr_0.95fr] lg:px-8 lg:py-28">
            <div className="flex flex-col justify-center">
              <p className="w-fit rounded-full border border-primary/20 bg-primary-soft px-4 py-1.5 text-sm font-semibold text-primary shadow-sm">
                AI-powered school communication
              </p>

              <h1 className="mt-6 max-w-4xl text-5xl font-extrabold leading-[1.05] tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-primary via-accent to-primary animate-text-gradient sm:text-6xl">
                Your school operations and parent communication in one AI
                workspace.
              </h1>

              <p className="mt-6 max-w-2xl text-lg leading-8 text-text-muted">
                Learnly AI automates repetitive school communication, helps
                parents get instant answers, and gives administrators one
                centralized system for academic operations.
              </p>

              <div className="mt-9 flex flex-col gap-4 sm:flex-row">
                <Link
                  to="/register"
                  className="btn-base rounded-2xl bg-primary px-7 py-4 text-base font-semibold text-text transition-all duration-300 hover:-translate-y-1 hover:bg-primary-hover hover:text-text-inverse hover:shadow-xl hover:shadow-primary/30"
                >
                  Join Learnly AI
                </Link>

                <a
                  href="#features"
                  className="btn-base rounded-2xl border border-border bg-surface px-7 py-4 text-base font-semibold text-text-soft transition-all duration-300 hover:-translate-y-1 hover:bg-surface-muted hover:text-text hover:shadow-lg"
                >
                  Explore platform
                </a>
              </div>

              <div className="mt-12 grid gap-4 sm:grid-cols-3">
                <div className="rounded-2xl border border-border bg-surface px-5 py-5 shadow-sm transition-all duration-300 hover:-translate-y-1 hover:shadow-xl">
                  <p className="text-3xl font-extrabold text-text">Fast</p>

                  <p className="mt-1 text-sm font-medium text-text-muted">
                    Response time
                  </p>
                </div>

                <div className="rounded-2xl border border-border bg-surface px-5 py-5 shadow-sm transition-all duration-300 hover:-translate-y-1 hover:shadow-xl">
                  <p className="text-3xl font-extrabold text-text">100%</p>

                  <p className="mt-1 text-sm font-medium text-text-muted">
                    Automated updates
                  </p>
                </div>

                <div className="rounded-2xl border border-border bg-surface px-5 py-5 shadow-sm transition-all duration-300 hover:-translate-y-1 hover:shadow-xl">
                  <p className="text-3xl font-extrabold text-text">Zero</p>

                  <p className="mt-1 text-sm font-medium text-text-muted">
                    Learning curve
                  </p>
                </div>
              </div>
            </div>

            <div className="relative">
              <div className="card-base overflow-hidden rounded-3xl border border-border shadow-2xl">
                <div className="border-b border-border bg-secondary p-6 text-text-inverse">
                  <div className="flex items-start justify-between gap-4 rounded-2xl border border-white/10 bg-white/10 p-4 shadow-inner-soft">
                    <div className="flex items-center gap-3">
                      <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-primary text-text shadow-sm">
                        <AppIcon name="spark" className="h-5 w-5" />
                      </span>

                      <div>
                        <p className="text-sm font-semibold text-primary-soft">
                          Live assistant
                        </p>

                        <h2 className="mt-1 text-2xl font-bold text-white">
                          Parent conversation
                        </h2>
                      </div>
                    </div>

                    <span className="rounded-full border border-success/20 bg-success-soft px-3 py-1 text-xs font-bold text-success">
                      Online
                    </span>
                  </div>

                  <div className="mt-8 space-y-5 text-sm">
                    <div className="ml-auto max-w-[82%] rounded-2xl bg-slate-700 px-4 py-3 transition-transform duration-300 hover:scale-[1.02] animate-chat-1 origin-bottom-right">
                      What assignment does Ada have today?
                    </div>

                    <div className="max-w-[86%] rounded-2xl bg-primary px-4 py-3 font-medium text-text shadow-lg shadow-primary/20 transition-transform duration-300 hover:scale-[1.02] animate-chat-2 origin-bottom-left">
                      Mathematics: page 24, exercises 1 to 10. Due Friday.
                    </div>

                    <div className="ml-auto max-w-[82%] rounded-2xl bg-slate-700 px-4 py-3 transition-transform duration-300 hover:scale-[1.02] animate-chat-3 origin-bottom-right">
                      Was she marked present?
                    </div>

                    <div className="max-w-[86%] rounded-2xl bg-primary px-4 py-3 font-medium text-text shadow-lg shadow-primary/20 transition-transform duration-300 hover:scale-[1.02] animate-chat-4 origin-bottom-left">
                      Yes. Ada was marked present at 8:05 AM today.
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4 bg-surface p-5">
                  <div className="metric-card metric-card-lavender transition-all duration-300 hover:-translate-y-1 hover:shadow-lg">
                    <p className="text-2xl font-bold text-text">120+</p>
                    <p className="mt-1 text-xs font-semibold text-text-muted">
                      Schools
                    </p>
                  </div>

                  <div className="metric-card metric-card-peach transition-all duration-300 hover:-translate-y-1 hover:shadow-lg">
                    <p className="text-2xl font-bold text-text">50K+</p>
                    <p className="mt-1 text-xs font-semibold text-text-muted">
                      Messages
                    </p>
                  </div>

                  <div className="metric-card metric-card-peach transition-all duration-300 hover:-translate-y-1 hover:shadow-lg">
                    <p className="text-2xl font-bold text-text">24/7</p>
                    <p className="mt-1 text-xs font-semibold text-text-muted">
                      Support
                    </p>
                  </div>

                  <div className="metric-card metric-card-lavender transition-all duration-300 hover:-translate-y-1 hover:shadow-lg">
                    <p className="text-2xl font-bold text-text">98%</p>
                    <p className="mt-1 text-xs font-semibold text-text-muted">
                      Parent satisfaction
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section
          id="features"
          className="mx-auto max-w-7xl px-4 py-20 sm:px-6 lg:px-8"
        >
          <div className="max-w-3xl">
            <p className="text-sm font-bold uppercase tracking-wide text-primary">
              Features
            </p>

            <h2 className="mt-4 text-4xl font-extrabold tracking-tight text-text sm:text-5xl">
              Built around the workflows schools repeat every day.
            </h2>

            <p className="mt-5 text-lg leading-8 text-text-muted">
              Learnly AI centralizes communication, academic operations, and
              reporting so school teams can move faster with less manual work.
            </p>
          </div>

          <div className="mt-12 grid gap-6 md:grid-cols-3">
            {features.map((feature) => (
              <article
                key={feature.title}
                className="group rounded-3xl border border-border bg-surface p-7 shadow-sm transition-all duration-300 hover:-translate-y-2 hover:border-primary/20 hover:shadow-2xl"
              >
                <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-primary-soft text-primary transition-transform duration-300 group-hover:scale-110">
                  <AppIcon name={feature.icon} className="h-7 w-7" />
                </div>

                <p className="mt-6 text-sm font-bold text-primary">
                  {feature.stat}
                </p>

                <h3 className="mt-3 text-2xl font-bold text-text">
                  {feature.title}
                </h3>

                <p className="mt-4 leading-7 text-text-muted">
                  {feature.description}
                </p>
              </article>
            ))}
          </div>

          <div className="mt-10 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {modules.map((module) => (
              <div
                key={module}
                className="flex items-center gap-3 rounded-2xl border border-border bg-surface px-5 py-4 text-sm font-semibold text-text-soft shadow-sm transition-all duration-300 hover:-translate-y-1 hover:border-primary/20 hover:bg-primary-soft/30 hover:shadow-lg"
              >
                <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-accent-soft text-accent">
                  <AppIcon name="check" className="h-4 w-4" />
                </span>
                {module}
              </div>
            ))}
          </div>
        </section>

        <section className="border-y border-border bg-surface">
          <div className="mx-auto grid max-w-7xl gap-12 px-4 py-20 sm:px-6 lg:grid-cols-2 lg:px-8">
            <div>
              <p className="text-sm font-bold uppercase tracking-wide text-primary">
                How it works
              </p>

              <h2 className="mt-4 text-4xl font-extrabold tracking-tight text-text sm:text-5xl">
                The AI handles routine parent communication automatically.
              </h2>

              <p className="mt-5 text-lg leading-8 text-text-muted">
                Learnly AI connects WhatsApp conversations directly to the
                school data already managed by teachers and administrators.
              </p>
            </div>

            <div className="space-y-4">
              {steps.map((step, index) => (
                <div
                  key={step}
                  className="flex gap-5 rounded-3xl border border-border bg-surface-raised p-5 shadow-sm transition-all duration-300 hover:-translate-y-1 hover:border-primary/20 hover:shadow-xl"
                >
                  <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-primary text-sm font-bold text-text shadow-md">
                    {index + 1}
                  </span>

                  <p className="self-center text-base font-semibold text-text-soft">
                    {step}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section
          id="pricing"
          className="mx-auto max-w-7xl px-4 py-20 sm:px-6 lg:px-8"
        >
          <div className="mx-auto max-w-3xl text-center">
            <p className="text-sm font-bold uppercase tracking-wide text-primary">
              Pricing
            </p>

            <h2 className="mt-4 text-4xl font-extrabold tracking-tight text-text sm:text-5xl">
              Flexible plans built for modern schools.
            </h2>

            <p className="mt-5 text-lg leading-8 text-text-muted">
              Start with essential communication tools and scale into advanced
              automation and reporting as your institution grows.
            </p>
          </div>

          <div className="mt-14 grid gap-6 lg:grid-cols-3">
            {pricingPlans.map((plan) => (
              <article
                key={plan.name}
                className={`relative overflow-hidden rounded-3xl border border-border bg-surface p-7 shadow-sm transition-all duration-300 hover:-translate-y-2 hover:shadow-2xl ${
                  plan.highlighted
                    ? "scale-[1.02] border-primary bg-primary-soft/20 ring-2 ring-primary/20"
                    : ""
                }`}
              >
                {plan.highlighted && (
                  <p className="mb-5 w-fit rounded-full bg-primary px-3 py-1 text-xs font-bold text-text">
                    Most selected
                  </p>
                )}

                <h3 className="text-3xl font-extrabold text-text">
                  {plan.name}
                </h3>

                <p className="mt-4 min-h-[70px] text-sm leading-7 text-text-muted">
                  {plan.description}
                </p>

                <p className="mt-7 text-4xl font-extrabold text-text">
                  {plan.price}
                </p>

                {plan.price !== "Custom" && (
                  <p className="mt-1 text-sm font-medium text-text-muted">
                    per month
                  </p>
                )}

                <ul className="mt-7 space-y-4">
                  {plan.features.map((feature) => (
                    <li
                      key={feature}
                      className="flex gap-3 text-sm font-medium text-text-soft"
                    >
                      <span className="mt-1.5 h-2 w-2 rounded-full bg-accent" />

                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>

                {plan.name === "Enterprise" ? (
                  <a
                    href="mailto:hello@learnly.ai"
                    className={`btn-base mt-9 flex w-full items-center justify-center rounded-2xl px-5 py-3.5 text-sm font-bold transition-all duration-300 hover:-translate-y-1 hover:shadow-xl ${
                      plan.highlighted
                        ? "bg-primary text-text hover:bg-primary-hover hover:text-text-inverse hover:shadow-primary/20"
                        : "bg-secondary text-text-inverse hover:bg-secondary-hover"
                    }`}
                  >
                    CONTACT SALES
                  </a>
                ) : (
                  <Link
                    to="/register"
                    className={`btn-base mt-9 flex w-full items-center justify-center rounded-2xl px-5 py-3.5 text-sm font-bold transition-all duration-300 hover:-translate-y-1 hover:shadow-xl ${
                      plan.highlighted
                        ? "bg-primary text-text hover:bg-primary-hover hover:text-text-inverse hover:shadow-primary/20"
                        : "bg-secondary text-text-inverse hover:bg-secondary-hover"
                    }`}
                  >
                    GET STARTED
                  </Link>
                )}
              </article>
            ))}
          </div>
        </section>

        <section className="border-t border-border bg-secondary">
          <div className="mx-auto max-w-5xl px-4 py-24 text-center sm:px-6 lg:px-8">
            <p className="text-sm font-bold uppercase tracking-wide text-accent">
              Ready to modernize your school?
            </p>

            <h2 className="mt-5 text-4xl font-extrabold tracking-tight text-text-inverse sm:text-5xl">
              Give parents instant answers with Learnly AI.
            </h2>

            <p className="mx-auto mt-6 max-w-2xl text-lg leading-8 text-slate-300">
              Reduce repetitive communication, improve operational visibility,
              and centralize school management in one powerful AI platform.
            </p>

            <Link
              to="/register"
              className="btn-base mt-9 inline-flex rounded-2xl bg-primary px-7 py-4 text-base font-semibold text-text transition-all duration-300 hover:-translate-y-1 hover:bg-primary-hover hover:text-text-inverse hover:shadow-2xl hover:shadow-primary/30"
            >
              Join us now
            </Link>
          </div>
        </section>
      </main>

      <footer className="border-t border-border bg-surface">
        <div className="mx-auto flex max-w-7xl flex-col gap-5 px-4 py-10 sm:px-6 md:flex-row md:items-center md:justify-between lg:px-8">
          <div>
            <p className="text-lg font-extrabold text-text">Learnly AI</p>

            <p className="mt-2 text-sm text-text-muted">
              AI-powered school management and parent communication platform.
            </p>
          </div>

          <div className="flex gap-6 text-sm font-semibold text-text-muted">
            <a
              href="#features"
              className="transition-colors duration-300 hover:text-primary"
            >
              Features
            </a>

            <a
              href="#pricing"
              className="transition-colors duration-300 hover:text-primary"
            >
              Pricing
            </a>

            <a
              href="mailto:hello@learnly.ai"
              className="transition-colors duration-300 hover:text-primary"
            >
              Contact
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default LandingPage;
