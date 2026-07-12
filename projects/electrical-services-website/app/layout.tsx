import "./globals.css";

export const metadata = {
  title: "Wright Sparks | Electrical Services",
  description: "Dependable electrical installations, testing, inspection and fault finding for homes and businesses.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
