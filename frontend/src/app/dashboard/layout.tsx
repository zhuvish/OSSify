import Sidebar from "@/src/components/Sidebar";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen bg-slate-100">
      <Sidebar />

      <main className="flex-1 overflow-x-hidden">
        <div className="max-w-[1700px] mx-auto p-8">
          {children}
        </div>
      </main>
    </div>
  );
}