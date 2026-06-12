import { Link } from "react-router-dom";
import {
  BarChart3,
  BookOpen,
  CalendarDays,
  CheckCircle2,
  ClipboardCheck,
  GraduationCap,
  ShieldCheck,
  Sparkles,
  Users,
} from "lucide-react";
import Navbar from "../../components/layout/Navbar";
import Button from "../../components/ui/Button";
import Badge from "../../components/ui/Badge";
import previewImage from "../../assets/images/academic-workspace-preview.png";

const features = [
  { title: "Student Management", description: "Centralized student profiles, guardians, class history, and academic status.", icon: GraduationCap },
  { title: "Teacher Management", description: "Profiles, qualifications, subjects, schedules, and assignment visibility.", icon: Users },
  { title: "Attendance", description: "Daily attendance marking with summaries for staff and parents.", icon: ClipboardCheck },
  { title: "Grades", description: "Score entry, performance tracking, report-card-ready academic records.", icon: BookOpen },
  { title: "Timetable", description: "Structured class schedules that make the school day easier to operate.", icon: CalendarDays },
  { title: "Analytics", description: "Operational dashboards for attendance, enrollment, notices, and AI activity.", icon: BarChart3 },
];

const benefits = [
  "Role-specific workspaces for admins, teachers, students, parents, and platform admins.",
  "Clean service boundaries so frontend pages do not own backend API logic.",
  "Mobile-friendly screens that stack naturally while staying optimized for desktop use.",
];

const testimonials = [
  {
    quote: "The dashboard gives our admin team the daily picture without forcing them into giant tables.",
    name: "Anita Sharma",
    role: "School Administrator",
  },
  {
    quote: "Attendance, notices, and class context finally live in one place that teachers can scan quickly.",
    name: "David Mensah",
    role: "Academic Lead",
  },
  {
    quote: "It feels calm and professional, which matters when parents and staff use the system every day.",
    name: "Ada Okafor",
    role: "Parent Liaison",
  },
];

function LandingPage() {
  return (
    <div className="min-h-screen overflow-x-hidden bg-background text-text">
      <Navbar />

      <main>
        <section className="relative min-h-[680px] overflow-hidden border-b border-border bg-slate-950 text-white sm:min-h-[760px] lg:min-h-[820px]">
          <img
            src={previewImage}
            alt="Learnly AI dashboard preview"
            className="absolute inset-0 h-full w-full object-cover opacity-35"
          />
          <div className="absolute inset-0 bg-slate-950/70" />
          <div className="section-container relative flex min-h-[620px] flex-col justify-center py-16 sm:min-h-[700px] lg:min-h-[760px]">
            <div className="max-w-3xl">
              <Badge variant="primary" className="bg-white/10 text-white ring-white/15">
                <Sparkles className="h-3.5 w-3.5" />
                Premium school management SaaS
              </Badge>
              <h1 className="mt-6 text-5xl font-semibold leading-tight tracking-tight text-white sm:text-6xl lg:text-7xl">
                Learnly AI
              </h1>
              <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-200 sm:text-xl">
                A modern workspace for school operations, attendance, classes, teachers, grades, notices, and parent communication.
              </p>
              <div className="mt-8 flex flex-col gap-3 sm:flex-row">
                <Link to="/register">
                  <Button size="large" className="w-full sm:w-auto">
                    Start your school workspace
                  </Button>
                </Link>
                <Link to="/login">
                  <Button variant="outline" size="large" className="w-full border-white/20 bg-white/10 text-white hover:bg-white/15 sm:w-auto">
                    Log in
                  </Button>
                </Link>
              </div>
            </div>

            <div className="absolute bottom-6 left-4 right-4 hidden rounded-2xl border border-white/10 bg-white/10 p-3 backdrop-blur-xl sm:left-6 sm:right-6 md:block lg:left-auto lg:w-[560px]">
              <div className="grid grid-cols-3 gap-3 text-sm">
                {[
                  ["92%", "Attendance rate"],
                  ["1,248", "Students tracked"],
                  ["24/7", "AI-ready operations"],
                ].map(([value, label]) => (
                  <div key={label} className="rounded-xl bg-white/10 px-4 py-3">
                    <p className="text-2xl font-semibold text-white">{value}</p>
                    <p className="mt-1 text-xs text-slate-300">{label}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        <section id="features" className="section-container py-20">
          <div className="max-w-3xl">
            <p className="text-sm font-bold uppercase tracking-wide text-primary">Features</p>
            <h2 className="mt-3 text-4xl font-semibold tracking-tight sm:text-5xl">
              Built around the workflows schools repeat every day.
            </h2>
            <p className="mt-4 text-base leading-7 text-text-muted">
              The platform keeps operational visibility high without burying teams in old-style admin templates.
            </p>
          </div>
          <div className="mt-10 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {features.map((feature) => {
              const Icon = feature.icon;
              return (
                <article key={feature.title} className="rounded-2xl border border-border bg-surface p-6 shadow-soft-card">
                  <span className="flex h-12 w-12 items-center justify-center rounded-2xl bg-primary-soft text-primary">
                    <Icon className="h-5 w-5" />
                  </span>
                  <h3 className="mt-5 text-lg font-semibold">{feature.title}</h3>
                  <p className="mt-2 text-sm leading-6 text-text-muted">{feature.description}</p>
                </article>
              );
            })}
          </div>
        </section>

        <section id="benefits" className="border-y border-border bg-surface">
          <div className="section-container grid gap-10 py-20 lg:grid-cols-[0.9fr_1.1fr] lg:items-center">
            <div>
              <p className="text-sm font-bold uppercase tracking-wide text-primary">Benefits</p>
              <h2 className="mt-3 text-4xl font-semibold tracking-tight sm:text-5xl">
                Calm software for busy school teams.
              </h2>
              <p className="mt-4 text-base leading-7 text-text-muted">
                Learnly AI is designed for repeated daily use: scanning, acting, reviewing, and moving on.
              </p>
            </div>
            <div className="grid gap-3">
              {benefits.map((benefit) => (
                <div key={benefit} className="flex gap-3 rounded-2xl border border-border bg-background px-5 py-4">
                  <CheckCircle2 className="mt-0.5 h-5 w-5 shrink-0 text-success" />
                  <p className="text-sm font-medium leading-6 text-text-soft">{benefit}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="section-container py-20">
          <div className="grid gap-6 lg:grid-cols-3">
            {testimonials.map((testimonial) => (
              <article key={testimonial.name} className="rounded-2xl border border-border bg-surface p-6 shadow-soft-card">
                <p className="text-base leading-7 text-text-soft">"{testimonial.quote}"</p>
                <div className="mt-6 flex items-center gap-3">
                  <span className="flex h-10 w-10 items-center justify-center rounded-full bg-primary-soft font-bold text-primary">
                    {testimonial.name.split(" ").map((part) => part[0]).join("")}
                  </span>
                  <div>
                    <p className="font-semibold">{testimonial.name}</p>
                    <p className="text-sm text-text-muted">{testimonial.role}</p>
                  </div>
                </div>
              </article>
            ))}
          </div>
        </section>

        <section id="pricing" className="border-y border-border bg-surface">
          <div className="section-container py-20">
            <div className="mx-auto max-w-3xl text-center">
              <p className="text-sm font-bold uppercase tracking-wide text-primary">Pricing</p>
              <h2 className="mt-3 text-4xl font-semibold tracking-tight sm:text-5xl">
                Future-ready plans for growing schools.
              </h2>
              <p className="mt-4 text-base leading-7 text-text-muted">
                Pricing is prepared for staged rollout while the platform modules continue to mature.
              </p>
            </div>
            <div className="mt-10 grid gap-4 lg:grid-cols-3">
              {[
                ["Starter", "Coming soon", "Core school management and communication workflows."],
                ["Growth", "Coming soon", "Advanced analytics, staff workflows, and parent engagement."],
                ["Enterprise", "Custom", "Multi-campus support, integrations, and dedicated onboarding."],
              ].map(([name, price, description], index) => (
                <article key={name} className={`rounded-2xl border bg-surface p-6 shadow-soft-card ${index === 1 ? "border-primary ring-4 ring-primary/10" : "border-border"}`}>
                  {index === 1 && <Badge variant="primary">Most selected</Badge>}
                  <h3 className="mt-4 text-2xl font-semibold">{name}</h3>
                  <p className="mt-3 text-3xl font-semibold">{price}</p>
                  <p className="mt-3 text-sm leading-6 text-text-muted">{description}</p>
                  <Button variant={index === 1 ? "primary" : "outline"} className="mt-6 w-full">
                    {name === "Enterprise" ? "Contact sales" : "Get started"}
                  </Button>
                </article>
              ))}
            </div>
          </div>
        </section>

        <section className="section-container py-20">
          <div className="rounded-2xl border border-border bg-slate-950 px-6 py-12 text-center text-white shadow-premium sm:px-10">
            <ShieldCheck className="mx-auto h-10 w-10 text-primary-soft" />
            <h2 className="mt-5 text-4xl font-semibold tracking-tight text-white">
              Modernize school operations without losing control.
            </h2>
            <p className="mx-auto mt-4 max-w-2xl text-base leading-7 text-slate-300">
              Give every role a cleaner workspace while preserving your backend model, tenant boundaries, and authentication flows.
            </p>
            <Link to="/register" className="mt-8 inline-flex">
              <Button size="large">Create workspace</Button>
            </Link>
          </div>
        </section>
      </main>

      <footer className="border-t border-border bg-surface">
        <div className="section-container flex flex-col gap-4 py-8 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="font-bold">Learnly AI</p>
            <p className="mt-1 text-sm text-text-muted">Premium school management and AI-ready operations.</p>
          </div>
          <div className="flex flex-wrap gap-4 text-sm font-semibold text-text-muted">
            <a href="#features" className="hover:text-primary">Features</a>
            <a href="#benefits" className="hover:text-primary">Benefits</a>
            <a href="#pricing" className="hover:text-primary">Pricing</a>
            <Link to="/login" className="hover:text-primary">Log in</Link>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default LandingPage;
