import { useState } from "react";
import { X, Eye, EyeOff } from "lucide-react";
import { login } from "../lib/api";

export default function LoginModal({ open, onClose }) {
  const [role, setRole] = useState("customer");
  const [showPw, setShowPw] = useState(false);
  const [email, setEmail] = useState("");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState(null);

  if (!open) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setBusy(true);
    setErr(null);
    try {
      await login(email || `${role}@example.com`, role);
      const paths = { customer: "/portal", merchant: "/merchant", admin: "/admin" };
      window.location.href = paths[role] || "/portal";
    } catch (ex) {
      setErr(ex.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm">
      <div className="bg-white rounded-2xl shadow-modal w-full max-w-md overflow-hidden">
        <div className="px-6 py-4 border-b border-drs-border flex items-center justify-between">
          <span className="font-semibold text-drs-text">Sign in</span>
          <button onClick={onClose} className="text-drs-text-light hover:text-drs-text transition-colors">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-5">
          <div className="space-y-1.5">
            <label className="text-xs font-medium text-drs-text-secondary">Role</label>
            <div className="grid grid-cols-3 gap-2">
              {[
                { value: "customer", label: "Customer" },
                { value: "merchant", label: "Merchant" },
                { value: "admin", label: "Admin" },
              ].map(({ value, label }) => (
                <button
                  key={value}
                  type="button"
                  onClick={() => setRole(value)}
                  className={`px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                    role === value
                      ? "bg-drs-accent-subtle text-drs-accent-soft border border-drs-accent-soft/30"
                      : "bg-drs-card text-drs-text-secondary border border-transparent hover:border-drs-border"
                  }`}
                >
                  {label}
                </button>
              ))}
            </div>
          </div>

          <div className="space-y-1.5">
            <label className="text-xs font-medium text-drs-text-secondary">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder={role === "customer" ? "alice@example.com" : role === "merchant" ? "merchant@acme.com" : "admin@drs.com"}
              className="w-full px-3 py-2 rounded-lg border border-drs-border text-drs-text text-sm bg-drs-bg focus:outline-none focus:border-drs-accent-soft transition-colors"
            />
          </div>

          <div className="space-y-1.5">
            <label className="text-xs font-medium text-drs-text-secondary">Password (demo)</label>
            <div className="relative">
              <input
                type={showPw ? "text" : "password"}
                value="••••••••"
                readOnly
                className="w-full px-3 py-2 pr-10 rounded-lg border border-drs-border text-drs-text text-sm bg-drs-bg/50 focus:outline-none cursor-default"
              />
              <button type="button" onClick={() => setShowPw(!showPw)} className="absolute right-3 top-1/2 -translate-y-1/2 text-drs-text-light hover:text-drs-text-secondary">
                {showPw ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>

          {err && <div className="px-3 py-2 rounded-lg bg-semantic-red/5 border border-semantic-red/10 text-xs text-semantic-red">{err}</div>}

          <button type="submit" disabled={busy} className="w-full py-2.5 rounded-lg bg-drs-accent text-white font-medium text-sm hover:bg-drs-accent-soft transition-colors disabled:opacity-50">
            {busy ? "Signing in..." : "Sign in"}
          </button>

          <p className="text-xs text-drs-text-light text-center">Demo — enter any email or use the placeholder. Password not required.</p>
        </form>
      </div>
    </div>
  );
}
