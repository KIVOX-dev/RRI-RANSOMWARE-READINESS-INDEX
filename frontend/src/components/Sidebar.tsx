import clsx from "clsx";
import { NavLink } from "react-router-dom";
import { useAuth } from "@/lib/auth";

interface NavItem {
  label: string;
  to: string;
}

interface NavGroup {
  title: string;
  items: NavItem[];
}

const GROUPS: NavGroup[] = [
  {
    title: "Assessment",
    items: [
      { label: "Overview", to: "/overview" },
      { label: "Assessment", to: "/assessment" },
      { label: "Evidence", to: "/evidence" },
      { label: "Verification", to: "/verification" },
      { label: "Backup Resilience", to: "/backup-resilience" },
    ],
  },
  {
    title: "Readiness",
    items: [
      { label: "Detection Matrix", to: "/detection-matrix" },
      { label: "Log Gaps", to: "/log-gaps" },
      { label: "Canary Tripwire", to: "/canary" },
      { label: "Dwell-Time", to: "/dwell-time" },
      { label: "Regulatory Compliance", to: "/regulatory-compliance" },
    ],
  },
  {
    title: "Insights",
    items: [
      { label: "Dashboard", to: "/dashboard" },
      { label: "Remediation", to: "/remediation" },
      { label: "Trends", to: "/trends" },
      { label: "Benchmarking", to: "/benchmarking" },
      { label: "Reports", to: "/reports" },
    ],
  },
  {
    title: "Oversight",
    items: [
      { label: "Regulator Console", to: "/oversight" },
      { label: "Integrity Ledger", to: "/ledger" },
    ],
  },
  {
    title: "System",
    items: [
      { label: "Settings", to: "/settings" },
      { label: "Profile", to: "/profile" },
    ],
  },
];

export function Sidebar() {
  const { user } = useAuth();

  return (
    <aside className="w-64 shrink-0 h-screen sticky top-0 border-r border-border bg-bg flex flex-col">
      <div className="px-5 py-6 border-b border-border">
        <div className="text-accent-ink font-bold text-lg tracking-tight">RRI</div>
        <div className="text-[10px] text-muted uppercase tracking-widest mt-1">Ransomware Readiness Index</div>
      </div>

      <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-6">
        {GROUPS.map((group) => {
          if (group.title === "Oversight" && user?.role !== "platform_admin") return null;
          return (
            <div key={group.title}>
              <div className="label-text px-2 mb-2">{group.title}</div>
              <div className="space-y-0.5">
                {group.items.map((item) => (
                  <NavLink
                    key={item.to}
                    to={item.to}
                    className={({ isActive }) =>
                      clsx(
                        "block px-3 py-2 rounded-md text-sm transition-colors",
                        isActive
                          ? "bg-accent text-ink font-medium"
                          : "text-light/80 hover:bg-bg-raised hover:text-light"
                      )
                    }
                  >
                    {item.label}
                  </NavLink>
                ))}
              </div>
            </div>
          );
        })}
      </nav>

      <div className="px-5 py-4 border-t border-border text-xs text-muted">
        {user && (
          <>
            <div className="text-light">{user.name}</div>
            <div className="uppercase tracking-wider text-[10px] mt-0.5">{user.role.replace("_", " ")}</div>
          </>
        )}
      </div>
    </aside>
  );
}
