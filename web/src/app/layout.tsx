import '@/app/globals.css';

export const metadata = {
  title: 'DemoPilot – AI‑Powered Pitch Rehearsal',
  description: 'Transform your pitch with AI‑driven rehearsal and feedback.'
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="bg-background text-foreground">
      <body className="min-h-screen flex flex-col" suppressHydrationWarning={true}>
        {children}
      </body>
    </html>
  );
}
