import { useState, useEffect } from "react";
import { Shield, Search, ChevronRight, FileText, AlertCircle, CheckCircle, Gavel } from "lucide-react";
import PortalLayout from "../components/PortalLayout";
import { fetchDisputes } from "../lib/api";

const ACTION_ICONS = {
  DISPUTE_CREATED: FileText, AUTO_FETCH_COMPLETED: AlertCircle,
  SCORING_COMPLETED: Shield, DECISION_RENDERED: Gavel, CLOSED: CheckCircle,
};

export default function AdminAuditLog() {
  const [disputes, setDisputes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState("");
  const [expanded, setExpanded] = useState({});

  useEffect(() => {
    (async () => {
      try { setDisputes(await fetchDisputes()); } catch (e) { console.error(e); } finally { setLoading(false); }
    })();
  }, []);

  const toggle = (id) => setExpanded((p) => ({ ...p, [id]: !p[id] }));

  const entries = disputes.flatMap((d) =>
    (d.audit_trail || []).map((e) => ({ ...e, tx: d.transaction_id, did: d.id, reason: d.reason_code, amount: d.amount, currency: d.currency }))
  ).sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

  const filtered = entries.filter((e) =>
    e.action_taken.toLowerCase().includes(query.toLowerCase()) ||
    e.tx.toLowerCase().includes(query.toLowerCase()) ||
    (e.performed_by || "").toLowerCase().includes(query.toLowerCase())
  );

  return (
    <PortalLayout>
      <div className="max-w-6xl mx-auto px-4 sm:px-6 pb-20 sm:pb-8 space-y-6">
        <div className="flex items-center gap-2">
          <Shield className="w-5 h-5 text-drs-accent-soft shrink-0" />
          <div>
            <h1 className="text-xl font-bold text-drs-text">Audit log</h1>
            <p className="text-xs text-drs-text-secondary">System-wide dispute activity</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-drs-text-light" />
            <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search entries..." className="w-full pl-9 pr-3 py-2 rounded-lg border border-drs-border text-drs-text text-sm bg-white focus:outline-none focus:border-drs-accent-soft transition-colors" />
          </div>
          <span className="text-xs text-drs-text-light">{filtered.length} entries</span>
        </div>

        {loading ? (
          <div className="text-center py-16 text-xs text-drs-text-light">Loading...</div>
        ) : filtered.length === 0 ? (
          <div className="text-center py-16"><Shield className="w-8 h-8 text-drs-text-light mx-auto mb-2" /><p className="text-sm text-drs-text-secondary">No entries found</p></div>
        ) : (
          <div className="space-y-1">
            {filtered.map((e, i) => {
              const Icon = ACTION_ICONS[e.action_taken] || Shield;
              const meta = e.metadata_json || {};
              return (
                <div key={e.id || i} className="bg-white rounded-xl border border-drs-border overflow-hidden">
                  <button onClick={() => toggle(e.id || i)} className="w-full flex items-center gap-3 p-4 text-left hover:bg-drs-bg/50 transition-colors">
                    <div className="p-1.5 rounded-lg bg-drs-card"><Icon className="w-3.5 h-3.5 text-drs-accent-soft" /></div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-medium text-drs-text">{e.action_taken.replace(/_/g, " ")}</span>
                        <span className="text-[11px] text-drs-text-light">#{e.tx}</span>
                      </div>
                      <div className="flex items-center gap-1.5 text-[11px] text-drs-text-light mt-0.5">
                        <span>{e.performed_by || "system"}</span>
                        <span>&middot;</span>
                        <span>{new Date(e.created_at).toLocaleString()}</span>
                      </div>
                    </div>
                    <ChevronRight className={`w-3.5 h-3.5 text-drs-text-light transition-transform ${expanded[e.id || i] ? "rotate-90" : ""}`} />
                  </button>
                  {expanded[e.id || i] && (
                    <div className="px-4 pb-4 border-t border-drs-border">
                      <div className="pt-3 grid grid-cols-2 sm:grid-cols-3 gap-3 text-xs">
                        {Object.entries(meta).map(([k, v]) => (
                          <div key={k} className="space-y-0.5">
                            <span className="text-drs-text-light uppercase tracking-wider text-[10px]">{k}</span>
                            <p className="text-drs-text font-mono truncate">{typeof v === "object" ? JSON.stringify(v) : String(v)}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </PortalLayout>
  );
}
