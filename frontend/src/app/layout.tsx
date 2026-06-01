import "./globals.css";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <div>
          <main className="min-h-screen">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}