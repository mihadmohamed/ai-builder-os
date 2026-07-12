export type Service = {
  number: string;
  title: string;
  description: string;
  detail: string;
};

export const services: Service[] = [
  { number: "01", title: "Electrical installations", description: "Safe, considered electrical work for new spaces, refurbishments and everyday upgrades.", detail: "Homes · Offices · Retail" },
  { number: "02", title: "Testing & inspection", description: "Clear, methodical checks to help keep your property compliant and your people protected.", detail: "EICR · Landlords · Commercial" },
  { number: "03", title: "Fault finding", description: "Practical diagnosis when something is not working as it should, with the next step explained plainly.", detail: "Diagnosis · Repairs · Advice" },
];

export const projects = [
  { title: "Commercial fit-out", category: "Installation", tone: "blue" },
  { title: "Residential upgrade", category: "Rewiring", tone: "amber" },
  { title: "Safety inspection", category: "Testing", tone: "slate" },
  { title: "Lighting project", category: "Installation", tone: "red" },
];

export const testimonials = [
  { quote: "Professional from the first conversation to the final check. The work was tidy, clearly explained and completed with care.", name: "Residential customer", service: "Electrical installation" },
  { quote: "Wright Sparks made the inspection process straightforward and gave us a clear view of what needed attention.", name: "Property manager", service: "Testing & inspection" },
  { quote: "A calm, efficient response and a practical fix. We always knew what was happening and why.", name: "Local business", service: "Fault finding" },
];
