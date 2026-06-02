import Sidebar from "@/src/components/Sidebar";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex">
      <Sidebar />

      <main className="flex-1 bg-slate-100">
      <div className="max-w-7xl mx-auto p-8">
        {children}
      </div>
    </main>
    </div>
  );
}