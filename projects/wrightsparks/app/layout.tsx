import "./globals.css";

export const metadata = {
  metadataBase: new URL("https://wrightsparks.vercel.app"),
  title: "Wright Sparks Ltd | Electricians in Reading",
  description: "Trusted electrical services for homes across Reading. Lighting, rewires, consumer units, EV charging, solar and fault finding.",
  openGraph: { title: "Wright Sparks Ltd — Reading Electricians", description: "Bright ideas. Expertly wired.", type: "website" },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en-GB">
      <body>{children}</body>
    </html>
  );
}
