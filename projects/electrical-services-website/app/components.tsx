"use client";

import { useState } from "react";
import { testimonials } from "./content";

export function Header() {
  const [open, setOpen] = useState(false);
  const close = () => setOpen(false);
  return <header className="site-header">
    <a className="wordmark" href="#home" aria-label="Wright Sparks home"><span>WRIGHT</span><strong>SPARKS</strong></a>
    <button className="menu-button" type="button" aria-expanded={open} aria-controls="primary-navigation" onClick={() => setOpen(!open)}><span className="sr-only">Toggle navigation</span><i /><i /></button>
    <nav id="primary-navigation" className={open ? "nav open" : "nav"} aria-label="Primary navigation">
      <a href="#services" onClick={close}>Services</a><a href="#work" onClick={close}>Our work</a><a href="#about" onClick={close}>About</a><a href="#contact" onClick={close}>Contact</a>
    </nav>
    <a className="header-cta" href="tel:+440000000000">Call us <span aria-hidden="true">↗</span></a>
  </header>;
}

export function Testimonials() {
  const [index, setIndex] = useState(0);
  if (!testimonials.length) return <SurfaceState title="No testimonials yet" message="Customer stories will appear here when available." />;
  const current = testimonials[index];
  const move = (step: number) => setIndex((index + step + testimonials.length) % testimonials.length);
  return <div className="testimonial-shell" aria-live="polite">
    <div className="quote-mark" aria-hidden="true">“</div>
    <blockquote><p>{current.quote}</p><footer><strong>{current.name}</strong><span>{current.service}</span></footer></blockquote>
    <div className="testimonial-controls">
      <span>{String(index + 1).padStart(2, "0")} / {String(testimonials.length).padStart(2, "0")}</span>
      <div><button type="button" onClick={() => move(-1)} aria-label="Previous testimonial">←</button><button type="button" onClick={() => move(1)} aria-label="Next testimonial">→</button></div>
    </div>
  </div>;
}

export function SurfaceState({ title, message, busy = false }: { title: string; message: string; busy?: boolean }) {
  return <div className="surface-state" role={busy ? "status" : "note"} aria-busy={busy}><span className={busy ? "spinner" : "state-dot"} aria-hidden="true" /><div><strong>{title}</strong><p>{message}</p></div></div>;
}

export function MobileActions() {
  return <div className="mobile-actions" aria-label="Quick contact actions"><a href="tel:+440000000000">Call now</a><a href="mailto:hello@wrightsparks.co.uk?subject=Quote%20request">Get a quote</a></div>;
}
