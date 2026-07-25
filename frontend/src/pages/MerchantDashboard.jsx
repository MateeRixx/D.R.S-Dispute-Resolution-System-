import { useState, useEffect, useCallback } from "react";
import { Store, Search, FileText, ExternalLink } from "lucide-react";
import PortalLayout from "../components/PortalLayout";
import DisputeStepper from "../components/DisputeStepper";
import VerdictCard from "../components/VerdictCard";
import EvidenceInspector from "../components/EvidenceInspector";
import UploadZone from "../components/UploadZone";
import { fetchDisputes, fetchDispute, uploadEvidence, getAuth } from "../lib/api";
import { useDisputeSSE } from "../hooks/useDisputeSSE";
import { useToast } from "../components/Toast";

const STATUS_LABELS = {
  INITIATED: "Initiated", EVIDENCE_GATHERING: "Gathering evidence",
  UNDER_REVIEW: "Under review", DECISION_RENDERED: "Decision rendered", CLOSED: "Closed",
};

function Detail({ dispute, onBack }) {
  const toast = useToast();
  const [live, setLive] = useState(dispute);
  const update = useCallback((u) => setLive((p) => ({ ...p, ...u })), []);
  useDisputeSSE(dispute?.id, update, () => {});
  const d = live || dispute;
  if (!d) return null;

  const handleUpload = async (file) => {
    try {
      await uploadEvidence(d.id, file, "MERCHANT");
      toast?.("Defence evidence submitted");
      setLive(await fetchDispute(d.id));
    } catch (ex) { toast?.(ex.message, "error"); }
  };

  return (
    <div className="max-w-4xl mx-auto px-6 py-8 space-y-6">
      <button onClick={onBack} className="text-xs text-drs-text-light hover:text-drs-text-secondary">&larr; Back to dashboard</button>
      <div className="space-y-1">
        <div className="flex items-center gap-2">
          <h1 className="text-xl font-bold text-drs-text">#{d.transaction_id}</h1>
          <span className="text-[11px] px-1.5 py-0.5 rounded bg-drs-card text-drs-text-secondary border border-drs-border">{d.reason_code?.replace(/_/g, " ")}</span>
        </div>
        <p className="text-xs text-drs-text-secondary">{d.currency} {d.amount} &middot; {new Date(d.created_at).toLocaleDateString()}</p>
      </div>
      <DisputeStepper currentStatus={d.status} />
      {d.verdict && <VerdictCard verdict={d.verdict} confidenceScore={d.confidence_score} summary={d.verdict_summary} reasonCode={d.reason_code} />}
      <EvidenceInspector evidence={d.evidence || []} />
      {(!d.status || !["DECISION_RENDERED", "CLOSED"].includes(d.status)) && (
        <div className="space-y-2">
          <h3 className="text-xs font-semibold text-drs-text-secondary uppercase tracking-wider">Submit defence evidence</h3>
          <UploadZone onUpload={handleUpload} />
        </div>
      )}
    </div>
  );
}

export default function MerchantDashboard() {
  const auth = getAuth();
  const [disputes, setDisputes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState(null);
  const [query, setQuery] = useState("");

  useEffect(() => {
    (async () => {
      try { setDisputes(await fetchDisputes({ merchantId: auth?.merchant_id })); } catch (e) { console.error(e); } finally { setLoading(false); }
    })();
  }, [auth?.id]);

  const view = async (id) => {
    try { setSelected(await fetchDispute(id)); } catch (e) { console.error(e); }
  };

  const filtered = disputes.filter((d) =>
    d.transaction_id.toLowerCase().includes(query.toLowerCase()) || d.reason_code.toLowerCase().includes(query.toLowerCase())
  );

  if (selected) return <PortalLayout><Detail dispute={selected} onBack={() => setSelected(null)} /></PortalLayout>;

  const stats = [
    { label: "Total disputes", value: disputes.length, color: "text-drs-accent" },
    { label: "Pending response", value: disputes.filter((d) => d.status === "INITIATED" || d.status === "EVIDENCE_GATHERING").length, color: "text-semantic-amber" },
    { label: "Decided", value: disputes.filter((d) => d.status === "DECISION_RENDERED" || d.status === "CLOSED").length, color: "text-semantic-emerald" },
  ];

  return (
    <PortalLayout>
      <div className="max-w-5xl mx-auto px-4 sm:px-6 pb-20 sm:pb-8 space-y-6">
        <div className="flex items-center gap-2">
          <Store className="w-5 h-5 text-drs-accent-soft shrink-0" />
          <h1 className="text-xl font-bold text-drs-text">Merchant dashboard</h1>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {stats.map((s) => (
            <div key={s.label} className="bg-white rounded-xl border border-drs-border p-5 text-center">
              <p className={`text-2xl font-bold ${s.color}`}>{s.value}</p>
              <p className="text-xs text-drs-text-secondary mt-1">{s.label}</p>
            </div>
          ))}
        </div>

        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-drs-text-light" />
          <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search disputes..." className="w-full pl-9 pr-3 py-2 rounded-lg border border-drs-border text-drs-text text-sm bg-white focus:outline-none focus:border-drs-accent-soft transition-colors" />
        </div>

        {loading ? (
          <div className="space-y-2">
            {[1,2,3].map((i) => (
              <div key={i} className="bg-white rounded-xl border border-drs-border p-4 animate-pulse">
                <div className="h-4 bg-[#E3DFD8] rounded w-1/3 mb-2" />
                <div className="h-3 bg-[#E3DFD8] rounded w-1/2" />
              </div>
            ))}
          </div>
        ) : filtered.length === 0 ? (
          <div className="text-center py-16"><FileText className="w-8 h-8 text-drs-text-light mx-auto mb-2" /><p className="text-sm text-drs-text-secondary">No disputes assigned</p></div>
        ) : (
          <div className="space-y-2">
            {filtered.map((d) => (
              <button key={d.id} onClick={() => view(d.id)} className="w-full bg-white rounded-xl border border-drs-border p-4 text-left hover:shadow-card-hover transition-shadow">
                <div className="flex items-center justify-between gap-4">
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-medium text-drs-text truncate">#{d.transaction_id}</p>
                    <p className="text-xs text-drs-text-secondary mt-0.5">{d.reason_code?.replace(/_/g, " ")} &middot; {d.currency} {d.amount}</p>
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    <span className={`text-[11px] font-medium px-1.5 py-0.5 rounded ${
                      d.status === "INITIATED" ? "bg-drs-accent-subtle text-drs-accent-soft" :
                      d.status === "EVIDENCE_GATHERING" ? "bg-semantic-amber/5 text-semantic-amber" :
                      "bg-semantic-emerald/5 text-semantic-emerald"
                    }`}>{STATUS_LABELS[d.status] || d.status}</span>
                    <ExternalLink className="w-3.5 h-3.5 text-drs-text-light" />
                  </div>
                </div>
              </button>
            ))}
          </div>
        )}
      </div>
    </PortalLayout>
  );
}
