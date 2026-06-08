"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import {
  LayoutDashboard,
  FolderGit2,
  Users,
  PlusCircle,
  Rocket,
} from "lucide-react";

const items = [
  {
    name: "Dashboard",
    href: "/dashboard",
    icon: LayoutDashboard,
  },
  {
    name: "Repositories",
    href: "/repositories",
    icon: FolderGit2,
  },
  {
    name: "Add Repository",
    href: "/",
    icon: PlusCircle,
  },
  {
    name: "Contributors",
    href: "/contributors",
    icon: Users,
  },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-[260px] min-h-screen bg-gradient-to-b from-[#020617] to-[#0f172a] text-white flex flex-col">

      <div className="px-8 py-8">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          OSSify 🚀
        </h1>
      </div>

      <nav className="px-4 space-y-3">
        {items.map((item) => {
          const Icon = item.icon;
          const active = pathname === item.href;

          return (
            <Link
              key={item.name}
              href={item.href}
              className={`
                flex items-center gap-4
                px-5 py-3 rounded-2xl
                transition-all
                ${
                  active
                    ? "bg-white/10 text-white"
                    : "text-slate-300 hover:bg-white/5"
                }
              `}
            >
              <Icon size={20} />
              <span className="text-md">{item.name}</span>
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}