"use client";
import Image from "next/image";
import { FormEvent, ReactNode, useEffect, useState } from "react";

const nav = [
  ["Home", "home"],
  ["Reviews", "testimonials"],
  ["Services", "services"],
  ["Accreditations", "accreditations"],
  ["About", "about"],
  ["Service Area", "service-area"],
  ["FAQ", "faq"],
];
const WHATSAPP_NUMBER = "447503975004";

function EnquiryForm({ kind }: { kind: "quote" | "contact" }) {
  const [status, setStatus] = useState<"idle" | "submitting" | "success">("idle");

  function submit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const form = e.currentTarget;
    if (!form.reportValidity()) return;
    setStatus("submitting");
    const data = new FormData(form);
    const heading = kind === "quote" ? `Quote request: ${data.get("service")}` : "Website enquiry";
    const body = [heading, ...data.entries()]
      .map((entry) => (Array.isArray(entry) ? `${entry[0]}: ${entry[1]}` : entry))
      .join("\n");
    setTimeout(() => {
      window.open(`https://wa.me/${WHATSAPP_NUMBER}?text=${encodeURIComponent(body)}`, "_blank", "noopener,noreferrer");
      setStatus("success");
    }, 350);
  }

  if (status === "success") {
    return (
      <div className="form-success" role="status">
        <span>✓</span>
        <h3>Your enquiry is ready</h3>
        <p>WhatsApp should have opened with the details. Review and send the message to complete your enquiry.</p>
        <button className="text-link" onClick={() => setStatus("idle")}>
          Send another enquiry →
        </button>
      </div>
    );
  }

  return (
    <form onSubmit={submit} className="enquiry-form">
      <div className="field-row">
        <label>
          Your name
          <input name="name" autoComplete="name" required placeholder="e.g. Sam Taylor" />
        </label>
        <label>
          Phone number
          <input name="phone" type="tel" autoComplete="tel" required placeholder="e.g. 07123 456789" />
        </label>
      </div>
      {kind === "quote" && (
        <div className="field-row">
          <label>
            Service
            <select name="service" required defaultValue="">
              <option value="" disabled>
                Choose a service
              </option>
              <option>Indoor & Outdoor Lighting</option>
              <option>Smart Home Installations</option>
              <option>Installations & Rewiring</option>
              <option>EV Charger Installation</option>
              <option>EICR Reports</option>
              <option>Fire & Smoke Alarms</option>
              <option>Repairs & Fault Finding</option>
              <option>PAT Testing</option>
              <option>Other</option>
            </select>
          </label>
          <label>
            Preferred timing
            <select name="timing" defaultValue="Flexible">
              <option>As soon as possible</option>
              <option>Within a month</option>
              <option>1–3 months</option>
              <option>Flexible</option>
            </select>
          </label>
        </div>
      )}
      <label>
        Email address
        <input name="email" type="email" autoComplete="email" required placeholder="you@example.com" />
      </label>
      <label>
        {kind === "quote" ? "Tell us about the work" : "How can we help?"}
        <textarea name="message" required rows={4} placeholder="A few useful details, including your postcode…" />
      </label>
      <button className="button primary full" disabled={status === "submitting"}>
        {status === "submitting"
          ? "Preparing your enquiry…"
          : kind === "quote"
            ? "Prepare my quote request ↗"
            : "Prepare my message ↗"}
      </button>
      <p className="form-note">This opens WhatsApp—nothing is stored on this website.</p>
    </form>
  );
}

export function ContactExperience({ children, footer }: { children: ReactNode; footer?: ReactNode }) {
  const [open, setOpen] = useState(false);
  useEffect(() => {
    const close = (e: KeyboardEvent) => e.key === "Escape" && setOpen(false);
    window.addEventListener("keydown", close);
    return () => window.removeEventListener("keydown", close);
  }, []);

  return (
    <div className="site-shell">
      <header className="site-header">
        <div className="wrap header-inner">
          <a href="#home" className="brand">
            <Image src="/site-import/logo.png" alt="Wright Sparks Ltd home" width={176} height={63} priority />
          </a>
          <nav className="desktop-nav" aria-label="Primary navigation">
            {nav.map(([label, id]) => (
              <a href={`#${id}`} key={id}>
                {label}
              </a>
            ))}
          </nav>
          <div className="header-actions">
            <a className="phone" href="tel:+447503975004">
              <span aria-hidden="true">☎</span> 07503 975004
            </a>
            <a className="button small primary" href="#quote">
              Get a quote
            </a>
            <button className="menu" aria-expanded={open} aria-controls="mobile-menu" onClick={() => setOpen(!open)}>
              <span>{open ? "Close" : "Menu"}</span>
              <i aria-hidden="true">{open ? "×" : "☰"}</i>
            </button>
          </div>
        </div>
        <nav id="mobile-menu" className={`mobile-nav ${open ? "open" : ""}`} aria-label="Mobile navigation">
          {nav.map(([label, id]) => (
            <a href={`#${id}`} onClick={() => setOpen(false)} key={id}>
              {label}
              <span>→</span>
            </a>
          ))}
          <a href="tel:+447503975004" onClick={() => setOpen(false)}>
            ☎ 07503 975004 <span>→</span>
          </a>
          <a href="#quote" onClick={() => setOpen(false)}>
            Get a quote <span>↗</span>
          </a>
        </nav>
      </header>
      {children}
      <section className="contact-section" id="quote">
        <div className="wrap contact-grid">
          <div className="contact-intro">
            <p className="eyebrow light">
              <span /> Start a project
            </p>
            <h2>
              Let’s make your
              <br />
              <em>next idea shine.</em>
            </h2>
            <p>Tell us what you have in mind and we’ll help you find the right next step.</p>
            <div className="direct-contact">
              <p>Prefer to talk?</p>
              <a href="tel:+447503975004">07503 975004 →</a>
              <a
                href="https://wa.me/447503975004?text=Hi%20Wright%20Sparks%2C%20I%27d%20like%20to%20discuss%20some%20electrical%20work."
                target="_blank"
                rel="noreferrer"
              >
                Message on WhatsApp ↗
              </a>
            </div>
          </div>
          <div className="form-card">
            <div className="form-tabs">
              <span>Get a quote</span>
              <a href="#contact">General enquiry</a>
            </div>
            <EnquiryForm kind="quote" />
          </div>
        </div>
      </section>
      <section className="general-contact" id="contact">
        <div className="wrap contact-grid compact">
          <div>
            <p className="eyebrow">
              <span /> Contact us
            </p>
            <h2>
              Have a quick
              <br />
              <em>question?</em>
            </h2>
            <p>Send a general enquiry and we’ll prepare the details in WhatsApp.</p>
          </div>
          <div className="form-card light-card">
            <EnquiryForm kind="contact" />
          </div>
        </div>
      </section>
      {footer}
      <a
        className="whatsapp"
        href="https://wa.me/447503975004?text=Hi%20Wright%20Sparks%2C%20I%27d%20like%20to%20discuss%20some%20electrical%20work."
        target="_blank"
        rel="noreferrer"
        aria-label="Chat with Wright Sparks on WhatsApp"
      >
        <b aria-hidden="true">◉</b>
        <span>WhatsApp</span>
      </a>
    </div>
  );
}
