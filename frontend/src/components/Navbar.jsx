import { Link, useLocation } from "react-router-dom";
import { User, Store, Shield, LogOut, BarChart3 } from "lucide-react";
import { getAuth, clearAuth } from "../lib/api";

const ITEMS = [
  { to: "/portal", label: "Portal", icon: User },
  { to: "/merchant", label: "Merchant", icon: Store },
  { to: "/admin", label: "Admin", icon: Shield },
  { to: "/admin/analytics", label: "Analytics", icon: BarChart3 },
];

export default function Navbar() {
  const { pathname } = useLocation();
  const auth = getAuth();

  const handleLogout = () => {
    clearAuth();
    window.location.href = "/";
  };

  return (
    <>
      <nav className="fixed top-0 inset-x-0 z-40 h-14 bg-white/90 backdrop-blur-md border-b border-drs-border">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 h-full flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2 shrink-0">
            <div className="w-6 h-6 rounded bg-drs-accent flex items-center justify-center">
              <span className="text-white text-[10px] font-bold">D</span>
            </div>
            <span className="text-sm font-semibold text-drs-text hidden sm:inline">DRS</span>
          </Link>

          <div className="flex items-center gap-1 overflow-x-auto scrollbar-none">
            {ITEMS.map(({ to, label, icon: Icon }) => {
              const active = pathname.startsWith(to);
              return (
                <Link
                  key={to}
                  to={to}
                  className={`flex items-center gap-1.5 px-2 sm:px-3 py-1.5 rounded-lg text-xs font-medium transition-colors active:scale-95 touch-manipulation whitespace-nowrap ${
                    active ? "bg-drs-accent-subtle text-drs-accent-soft" : "text-drs-text-secondary hover:text-drs-text hover:bg-drs-card"
                  }`}
                >
                  <Icon className="w-3.5 h-3.5 shrink-0" />
                  <span className="hidden sm:inline">{label}</span>
                </Link>
              );
            })}

            {auth && (
              <>
                <span className="mx-2 text-xs text-drs-text-light hidden sm:inline truncate max-w-[120px]">{auth.name}</span>
                <button onClick={handleLogout} className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-xs text-drs-text-light hover:text-drs-text hover:bg-drs-card transition-colors active:scale-95 touch-manipulation">
                  <LogOut className="w-3.5 h-3.5" />
                </button>
              </>
            )}
          </div>
        </div>
      </nav>

      <nav className="fixed bottom-0 inset-x-0 z-40 h-16 bg-white/90 backdrop-blur-md border-t border-drs-border sm:hidden">
        <div className="flex items-center justify-around h-full px-2">
          {ITEMS.map(({ to, label, icon: Icon }) => {
            const active = pathname.startsWith(to);
            return (
              <Link
                key={to}
                to={to}
                className={`flex flex-col items-center gap-0.5 px-3 py-1.5 rounded-lg transition-colors active:scale-95 touch-manipulation ${
                  active ? "text-drs-accent-soft" : "text-drs-text-light"
                }`}
              >
                <Icon className="w-5 h-5" />
                <span className="text-[10px] font-medium">{label}</span>
              </Link>
            );
          })}
          {auth && (
            <button onClick={handleLogout} className="flex flex-col items-center gap-0.5 px-3 py-1.5 text-drs-text-light active:scale-95 touch-manipulation">
              <LogOut className="w-5 h-5" />
              <span className="text-[10px] font-medium">Logout</span>
            </button>
          )}
        </div>
      </nav>
    </>
  );
}
