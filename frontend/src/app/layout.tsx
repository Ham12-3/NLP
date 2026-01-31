import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Text Corrector",
  description:
    "Correct grammar and convert between British and American English.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen">{children}</body>
    </html>
  );
}
