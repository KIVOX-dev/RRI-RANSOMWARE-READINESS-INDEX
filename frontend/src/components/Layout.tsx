import type { ReactNode } from "react";
import { Sidebar } from "@/components/Sidebar";
import { useAuth } from "@/lib/auth";

export function Layout({ children, title, subtitle }: { children: ReactNode; title?: string; subtitle?: string }) {
  const { logout } = useAuth();

  return (
    <div className="flex min-h-screen bg-bg">
      <Sidebar />
      <div className="flex-1 min-w-0">
        {title && (
          <header className="sticky top-0 z-10 bg-bg/95 backdrop-blur border-b border-border px-8 py-5 flex items-center justify-between">
            <div>
              <h1 className="text-xl font-semibold text-light">{title}</h1>
              {subtitle && <p className="text-sm text-muted mt-1">{subtitle}</p>}
            </div>
            <button onClick={logout} className="btn-secondary text-xs">
              Log out
            </button>
          </header>
        )}
        <main className="px-8 py-6 max-w-[1400px]">{children}</main>
      </div>
    </div>
  );
}
