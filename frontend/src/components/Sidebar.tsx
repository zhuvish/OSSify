"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import {
  LayoutDashboard,
  FolderGit2,
  Users,
  Network,
  Bot,
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
    name: "Contributors",
    href: "/contributors",
    icon: Users,
  },
  {
    name: "Graph Explorer",
    href: "/graph",
    icon: Network,
  },
  {
    name: "Ask AI",
    href: "/chat",
    icon: Bot,
  },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 min-h-screen bg-slate-950 border-r border-slate-800">
      <div className="p-6">
        <h1 className="text-2xl font-bold text-white">
          OSSify
        </h1>
      </div>

      <nav className="px-3 space-y-2">
        {items.map((item) => {
          const Icon = item.icon;

          const active = pathname === item.href;

          return (
            <Link
              key={item.name}
              href={item.href}
              className={`
                flex items-center gap-3
                rounded-xl px-4 py-2 transition
                ${
                  active
                    ? "bg-slate-800 text-white"
                    : "text-slate-400 hover:bg-slate-900 hover:text-white"
                }
              `}
            >
              <Icon size={18} />
              {item.name}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}