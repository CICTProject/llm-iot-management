"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useSession } from "next-auth/react";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  Warehouse,
  Cpu,
  Activity,
  Bell,
  BarChart3,
  Settings,
  Network,
} from "lucide-react";

const navigation = [
  { name: "Dashboard", href: "/", icon: LayoutDashboard },
  { name: "Hospitals", href: "/hospitals", icon: Warehouse },
  { name: "Devices", href: "/devices", icon: Cpu },
  { name: "Sensors", href: "/sensors", icon: Activity },
  { name: "Alerts", href: "/alerts", icon: Bell },
  { name: "Analytics", href: "/analytics", icon: BarChart3 },
  { name: "Network Management", href: "/network", icon: Network, adminOnly: true },
  { name: "Settings", href: "/settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();
  const { data: session } = useSession();
  const isAdmin = session?.user?.email === "admin@hospital.io";

  return (
    <aside className="hidden md:flex md:w-64 md:flex-col border-r bg-card">
      <div className="flex h-16 items-center gap-3 border-b px-4">
        <img src="/logo.png" alt="We bare bears Logo" className="w-10 h-10 rounded-lg object-cover flex-shrink-0" />
        <span className="font-semibold text-lg truncate">Hospital</span>
      </div>
      <nav className="flex-1 space-y-1 p-3">
        {navigation
          .filter((item) => !item.adminOnly || isAdmin)
          .map((item) => {
            const isActive =
              item.href === "/"
                ? pathname === "/"
                : pathname.startsWith(item.href);
            return (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                  isActive
                    ? "bg-primary text-primary-foreground"
                    : "text-muted-foreground hover:bg-muted hover:text-foreground"
                )}
              >
                <item.icon className="h-4 w-4" />
                {item.name}
              </Link>
            );
          })}
      </nav>
    </aside>
  );
}
