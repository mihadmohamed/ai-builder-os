import Image from "next/image";
import { ContactExperience } from "../components/contact-experience";

const serviceCategories = [
  {
    title: "Home Improvements",
    icon: "⌂",
    services: [
      {
        title: "Indoor & Outdoor Lighting",
        copy: "Transform your home with thoughtfully designed lighting, from feature walls and kitchens to gardens and outdoor entertaining spaces.",
        bullets: ["Indoor lighting", "Outdoor lighting", "Garden lighting"],
        image: "/site-import/services/wright-sparks-ltd_facebook_gallery_40.webp",
        labelTitle: "Outdoor Lighting Design",
        labelCopy: "Feature garden lighting with layered ambience and safe path illumination.",
        labelLocation: "Reading",
      },
      {
        title: "Smart Home Installations",
        copy: "Modern home automation including smart lighting, heating controls and energy management.",
        bullets: ["Smart lighting", "Heating controls", "Energy management"],
        image: "/site-import/services/garden-studio-lighting.webp",
        labelTitle: "Garden Studio Upgrade",
        labelCopy: "Smart switching and lighting controls for a modern detached workspace.",
        labelLocation: "Woodley",
      },
    ],
  },
  {
    title: "Electrical Installations",
    icon: "⚡",
    services: [
      {
        title: "Installations & Rewiring",
        copy: "Complete electrical installations for extensions, renovations, kitchens, bathrooms and full or partial rewires.",
        bullets: ["Extensions", "Renovations", "Full & partial rewires"],
        image: "/site-import/services/wright-sparks-ltd_facebook_gallery_34-400x284.webp",
        labelTitle: "Family Home Extension",
        labelCopy: "Full first and second fix wiring with feature lighting throughout.",
        labelLocation: "Caversham",
      },
      {
        title: "EV Charger Installation",
        copy: "Professional installation of home EV chargers compatible with all major manufacturers.",
        bullets: ["Home chargers", "Major brands", "Safe installation"],
        image: "/site-import/services/constr-projects-4.jpg",
        labelTitle: "Consumer Unit Upgrade",
        labelCopy: "Prepared for safe new circuits, modern protection and future EV charging.",
        labelLocation: "Reading",
      },
    ],
  },
  {
    title: "Safety & Compliance",
    icon: "✓",
    services: [
      {
        title: "EICR Reports",
        copy: "Professional Electrical Installation Condition Reports for homeowners, landlords and home buyers.",
        bullets: ["Homeowners", "Landlords", "Home buyers"],
        image: "/site-import/services/constr-projects-3.jpg",
        labelTitle: "Bathroom Renovation Check",
        labelCopy: "Inspection and certification of electrical work in wet areas.",
        labelLocation: "Berkshire",
      },
      {
        title: "Fire & Smoke Alarms",
        copy: "Installation and testing of smoke alarms and heat detectors to help protect your family and meet current regulations.",
        bullets: ["Smoke alarms", "Heat detectors", "Current regulations"],
        image: "/site-import/services/constr-projects-1.jpg",
        labelTitle: "Protected Living Spaces",
        labelCopy: "Careful installation work supporting safe, compliant family homes.",
        labelLocation: "Reading",
      },
    ],
  },
  {
    title: "Repairs & Maintenance",
    icon: "⌕",
    services: [
      {
        title: "Repairs & Fault Finding",
        copy: "Fast diagnosis and reliable repairs when your electrics aren&apos;t working as they should.",
        bullets: ["Fast diagnosis", "Reliable repairs", "Clear next steps"],
        image: "/site-import/services/constr-projects-6.jpg",
        labelTitle: "Lighting Fault Resolution",
        labelCopy: "Diagnosis and repair work restoring lighting circuits and fittings.",
        labelLocation: "Reading",
      },
      {
        title: "PAT Testing",
        copy: "Portable Appliance Testing for landlords, businesses and commercial properties.",
        bullets: ["Landlords", "Businesses", "Commercial properties"],
        image: "/site-import/services/wright-sparks-ltd_facebook_gallery_37-400x284.webp",
        labelTitle: "Rental Property Ready",
        labelCopy: "Testing support for safely maintained lets and managed properties.",
        labelLocation: "Berkshire",
      },
    ],
  },
];

const credentials = [
  ["mcs.png", "MCS certified"],
  ["city-and-guilds.png", "City & Guilds qualified"],
  ["niceic-domestic.png", "NICEIC Domestic Installer"],
  ["recc.png", "RECC member"],
  ["part-p.png", "Part P registered"],
  ["niceic-approved.png", "NICEIC Approved Contractor"],
];

export default function Home() {
  return (
    <ContactExperience
      footer={
        <footer>
          <div className="wrap footer-grid">
            <div>
              <Image src="/site-import/logo.png" alt="Wright Sparks Ltd" width={200} height={72} />
              <p>
                Reading&apos;s expert electricians.
                <br />
                Carefully planned. Properly finished.
              </p>
            </div>
            <nav aria-label="Footer navigation">
              <h3>Explore</h3>
              {[
                ["Reviews", "testimonials"],
                ["Services", "services"],
                ["Accreditations", "accreditations"],
                ["About", "about"],
                ["Service Area", "service-area"],
                ["FAQ", "faq"],
              ].map(([label, id]) => (
                <a href={`#${id}`} key={id}>
                  {label}
                </a>
              ))}
            </nav>
            <div>
              <h3>Contact</h3>
              <a href="tel:+447503975004">07503 975004</a>
              <a href="#contact">Send an enquiry</a>
              <a href="https://wa.me/447503975004" target="_blank" rel="noreferrer">
                WhatsApp ↗
              </a>
            </div>
          </div>
          <div className="wrap footer-base">
            <p>© {new Date().getFullYear()} Wright Sparks Ltd. All rights reserved.</p>
            <p>Electrical services in Reading, Berkshire</p>
          </div>
        </footer>
      }
    >
      <main>
        <section className="hero" id="home">
          <div className="wrap hero-grid">
            <div className="hero-copy reveal">
              <p className="eyebrow">
                <span /> TRUSTED ELECTRICIANS • READING &amp; BERKSHIRE
              </p>
              <h1>
                Electrical Work Done Right.
                <br />
                <em className="hero-tagline">First Time. Every Time.</em>
              </h1>
              <p className="hero-lead">
                From emergency repairs to complete installations, Wright Sparks delivers safe, certified electrical work with clear communication, quality workmanship, and respect for your home.
              </p>
              <div className="button-row">
                <a className="button primary" href="#quote">
                  Get a free quote <span aria-hidden="true">↗</span>
                </a>
                <a className="button ghost" href="tel:+447503975004">
                  Call 07503 975004
                </a>
              </div>
              <div className="micro-proof" aria-label="Trust signals">
                <p className="micro-proof-rating">
                  <span aria-hidden="true">★★★★★</span> <strong>10/10 Checkatrade</strong> <em>(41 Reviews)</em>
                </p>
                <ul className="micro-proof-list">
                  <li>
                    <span aria-hidden="true">✓</span> NAPIT Approved
                  </li>
                  <li>
                    <span aria-hidden="true">✓</span> Fully Insured
                  </li>
                </ul>
              </div>
            </div>
            <div className="hero-media reveal">
              <Image
                src="/site-import/garden-lighting-hero-user-provided.png"
                alt="Evening garden lighting installation with feature wall lights, fire feature, and illuminated path"
                fill
                priority
                sizes="(max-width: 800px) 100vw, 48vw"
              />
            </div>
          </div>
        </section>

        <section className="proof-band" aria-label="Why choose Wright Sparks">
          <div className="wrap proof-grid">
            <article>
              <b>01</b>
              <div>
                <h3>Reliable</h3>
                <p>
                  <strong>We do what we say we&apos;ll do.</strong>
                  We arrive when promised, communicate clearly throughout the job and complete the work to the agreed standard.
                </p>
              </div>
            </article>
            <article>
              <b>02</b>
              <div>
                <h3>Safe</h3>
                <p>
                  <strong>Electrical work you can depend on.</strong>
                  NAPIT approved and completed to British Standard BS 7671, giving you confidence your installation is safe and compliant.
                </p>
              </div>
            </article>
            <article>
              <b>03</b>
              <div>
                <h3>Respectful</h3>
                <p>
                  <strong>Your home treated with care.</strong>
                  We work neatly, protect your property and leave every space clean and tidy when the job is complete.
                </p>
              </div>
            </article>
          </div>
        </section>

        <section className="section reviews" id="testimonials">
          <div className="wrap review-shell">
            <div className="review-intro">
              <div className="stars" aria-hidden="true">
                ★★★★★
              </div>
              <h2>
                Homeowners recommend
                <br />
                <em>Wright Sparks.</em>
              </h2>
              <p>Independent reviews from Google and Checkatrade.</p>
            </div>
            <div className="review-panels">
              <div className="review-snippets">
                <article>
                  <div className="review-snippet-stars" aria-hidden="true">
                    ★★★★★
                  </div>
                  <p>&ldquo;Aaron arrived exactly on time...&rdquo;</p>
                </article>
                <article>
                  <div className="review-snippet-stars" aria-hidden="true">
                    ★★★★★
                  </div>
                  <p>&ldquo;Very professional...&rdquo;</p>
                </article>
                <article>
                  <div className="review-snippet-stars" aria-hidden="true">
                    ★★★★★
                  </div>
                  <p>&ldquo;Would highly recommend...&rdquo;</p>
                </article>
              </div>
              <div className="review-summary">
                <div className="review-sources">
                  <p>
                    ★★★★★ <strong>10/10</strong>
                    <span>Checkatrade</span>
                  </p>
                  <p>
                    ★★★★★ <strong>5.0</strong>
                    <span>Google</span>
                  </p>
                </div>
                <div className="review-praise">
                  <h3>Repeatedly praised for:</h3>
                  <ul>
                    <li>Reliability</li>
                    <li>Clear communication</li>
                    <li>Quality workmanship</li>
                    <li>Leaving homes clean and tidy</li>
                  </ul>
                </div>
                <a className="button dark" href="https://www.checkatrade.com/trades/wrightsparks991862/reviews" target="_blank" rel="noreferrer">
                  View on Checkatrade ↗
                </a>
              </div>
            </div>
          </div>
        </section>

        <section className="section services" id="services">
          <div className="wrap">
            <div className="section-head services-head">
              <div>
                <p className="eyebrow">
                  <span /> What we do
                </p>
                <h2>
                  Electrical Services,
                  <br />
                  <em>done properly.</em>
                </h2>
              </div>
              <p>
                Whether you need a quick repair, a safety inspection or complete electrical installation, every job is completed with the same care, professionalism and attention to detail.
              </p>
            </div>

            <div className="service-categories">
              {serviceCategories.map((category) => (
                <section className="service-category" key={category.title}>
                  <div className="service-category-head">
                    <p className="service-category-label">
                      <span aria-hidden="true">{category.icon}</span>
                      {category.title}
                    </p>
                  </div>

                  <div className="service-category-grid">
                    {category.services.map((service) => (
                      <article className="service-uniform-card" key={service.title}>
                        <div className="service-uniform-media">
                          <Image src={service.image} alt={service.title} fill sizes="(max-width: 800px) 100vw, 44vw" />
                          <div className="service-image-label">
                            <strong>{service.labelTitle}</strong>
                            <span>{service.labelCopy}</span>
                            <em>{service.labelLocation}</em>
                          </div>
                        </div>
                        <div className="service-uniform-copy">
                          <h3>{service.title}</h3>
                          <p>{service.copy}</p>
                          <ul>
                            {service.bullets.map((bullet) => (
                              <li key={bullet}>
                                <span aria-hidden="true">✓</span>
                                {bullet}
                              </li>
                            ))}
                          </ul>
                          <a href="#quote" aria-label={`Get a quote for ${service.title}`}>
                            Discuss this service →
                          </a>
                        </div>
                      </article>
                    ))}
                  </div>
                </section>
              ))}
            </div>

            <div className="services-cta">
              <div>
                <p className="eyebrow">
                  <span /> Need a hand deciding?
                </p>
                <h3>Not sure which service you need?</h3>
                <p>If you&apos;re experiencing an electrical problem or planning a project, get in touch and we&apos;ll recommend the right solution.</p>
              </div>
              <div className="services-cta-actions">
                <a className="button primary" href="#quote">
                  Get a free quote
                </a>
                <a className="button ghost" href="tel:+447503975004">
                  Call 07503 975004
                </a>
                <a className="button ghost" href="https://wa.me/447503975004" target="_blank" rel="noreferrer">
                  WhatsApp
                </a>
              </div>
            </div>
          </div>
        </section>

        <section className="section credentials" id="accreditations">
          <div className="wrap">
            <div className="center-head">
              <p className="eyebrow">
                <span /> Qualified & accountable
              </p>
              <h2>
                Standards you can <em>trust.</em>
              </h2>
              <p>Recognised industry credentials, backed by careful work and comprehensive insurance.</p>
            </div>
            <div className="credential-grid">
              {credentials.map(([src, alt]) => (
                <div key={src}>
                  <Image src={`/site-import/${src}`} alt={alt} width={180} height={126} />
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="section about" id="about">
          <div className="wrap split">
            <div className="work-image">
              <Image src="/site-import/garden-studio-lighting.png" alt="Exterior lighting installed on a garden studio" fill sizes="(max-width: 800px) 100vw, 45vw" />
              <p>
                Recent work <span>Reading, Berkshire</span>
              </p>
            </div>
            <div className="about-copy">
              <p className="eyebrow">
                <span /> About Wright Sparks
              </p>
              <h2>
                Reliable people.
                <br />
                <em className="about-nowrap">Reliable workmanship.</em>
              </h2>
              <p>
                At Wright Sparks, we believe good electrical work is about more than technical expertise. It&apos;s about being dependable from the moment you get in touch until the job is complete. We arrive when promised, explain your options clearly, work safely and leave your home clean and tidy.
              </p>
              <p>
                Whether it&apos;s a small repair or a complete rewire, you&apos;ll receive the same care, professionalism and attention to detail every time.
              </p>
              <ul className="about-checklist">
                <li>
                  <span aria-hidden="true">✓</span> 10+ Years Experience
                </li>
                <li>
                  <span aria-hidden="true">✓</span> NAPIT Approved
                </li>
                <li>
                  <span aria-hidden="true">✓</span> British Standard BS 7671
                </li>
                <li>
                  <span aria-hidden="true">✓</span> Fully Insured
                </li>
                <li>
                  <span aria-hidden="true">✓</span> Reading &amp; Berkshire
                </li>
              </ul>
            </div>
          </div>
        </section>

        <section className="section area" id="service-area">
          <div className="wrap area-grid">
            <div>
              <p className="eyebrow">
                <span /> Our service area
              </p>
              <h2>
                Proudly serving
                <br />
                <em>Reading & nearby.</em>
              </h2>
              <p>Based in Reading and working across the surrounding Berkshire area. Not sure whether we cover your postcode? Send us a quick message and we’ll let you know.</p>
              <a className="button primary" href="https://wa.me/447503975004?text=Hi%20Wright%20Sparks%2C%20do%20you%20cover%20my%20postcode%3F" target="_blank" rel="noreferrer">
                Ask on WhatsApp ↗
              </a>
            </div>
            <div className="map">
              <iframe
                title="Map showing the Wright Sparks service area around Reading"
                src="https://www.google.com/maps?q=Reading%2C%20Berkshire&output=embed"
                loading="lazy"
                referrerPolicy="no-referrer-when-downgrade"
              />
              <span>Reading, Berkshire</span>
            </div>
          </div>
        </section>

        <section className="section faq" id="faq">
          <div className="wrap narrow">
            <div className="center-head">
              <p className="eyebrow">
                <span /> Helpful answers
              </p>
              <h2>
                Frequently asked <em>questions.</em>
              </h2>
            </div>
            <div className="faq-list">
              {[
                ["Do you offer free quotes?", "Yes. Tell us about the work and we can discuss the next step and arrange a quote where appropriate."],
                ["What areas do you cover?", "We serve Reading and nearby parts of Berkshire. Message us with your postcode and we’ll confirm availability."],
                ["Are you qualified and insured?", "Wright Sparks presents NICEIC, City & Guilds, MCS, RECC and Part P credentials and comprehensive insurance."],
                ["Can I contact you on WhatsApp?", "Yes. Use the WhatsApp button anywhere on this page to start a conversation with the published business number."],
                ["What information helps with a quote?", "Include the type of work, your postcode, preferred timing and any useful details about the property or existing installation."],
              ].map(([question, answer]) => (
                <details key={question}>
                  <summary>
                    {question}
                    <span>+</span>
                  </summary>
                  <p>{answer}</p>
                </details>
              ))}
            </div>
          </div>
        </section>
      </main>
    </ContactExperience>
  );
}
