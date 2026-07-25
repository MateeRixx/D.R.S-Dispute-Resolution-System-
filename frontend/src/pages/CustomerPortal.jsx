import { useState, useEffect, useCallback } from "react";
import { Search, Plus, FileText, Scale, AlertCircle } from "lucide-react";
import PortalLayout from "../components/PortalLayout";
import DisputeStepper from "../components/DisputeStepper";
import VerdictCard from "../components/VerdictCard";
import EvidenceInspector from "../components/EvidenceInspector";
import UploadZone from "../components/UploadZone";
import { fetchDisputes, fetchDispute, createDispute, uploadEvidence, getAuth } from "../lib/api";
import { useDisputeSSE } from "../hooks/useDisputeSSE";
import { useToast } from "../components/Toast";

const STATUS_LABELS = {
  INITIATED: "Initiated", EVIDENCE_GATHERING: "Gathering evidence",
  UNDER_REVIEW: "Under review", DECISION_RENDERED: "Decision rendered", CLOSED: "Closed",
};

function CreateModal({ onClose, onCreated }) {
  const toast = useToast();
  const auth = getAuth();
  const [form, setForm] = useState({ transaction_id: "", user_id: auth?.id || "", merchant_id: "", amount: "", currency: "INR", reason_code: "ITEM_NOT_RECEIVED", user_narrative: "" });
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState(null);
  const [errors, setErrors] = useState({});

  const validate = () => {
    const e = {};
    if (!form.transaction_id.trim()) e.transaction_id = "Required";
    if (!form.merchant_id.trim()) e.merchant_id = "Required";
    if (!form.amount || parseFloat(form.amount) <= 0) e.amount = "Must be > 0";
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const handle = async (e) => {
    e.preventDefault();
    if (!validate()) return;
    setBusy(true);
    setErr(null);
    try {
      await createDispute({ ...form, amount: parseFloat(form.amount) });
      toast?.("Dispute filed successfully");
      onCreated();
      onClose();
    } catch (ex) { setErr(ex.message); } finally { setBusy(false); }
  };

  const inp = (field) => ({
    value: form[field],
    onChange: (e) => { setForm({ ...form, [field]: e.target.value }); if (errors[field]) setErrors({ ...errors, [field]: null }); },
    className: `w-full px-3 py-2 rounded-lg border text-drs-text text-sm bg-drs-bg focus:outline-none focus:border-drs-accent-soft transition-colors ${errors[field] ? "border-semantic-red" : "border-drs-border"}`,
  });

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm">
      <div className="bg-white rounded-2xl shadow-modal w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <div className="px-6 py-4 border-b border-drs-border flex items-center justify-between">
          <h2 className="text-sm font-semibold text-drs-text">File new dispute</h2>
          <button onClick={onClose} className="text-drs-text-light hover:text-drs-text"><AlertCircle className="w-4 h-4 rotate-45" /></button>
        </div>
        <form onSubmit={handle} className="p-6 space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="space-y-1"><label className="text-[11px] font-medium text-drs-text-secondary uppercase tracking-wider">Transaction ID</label><input required {...inp("transaction_id")} /></div>
            <div className="space-y-1"><label className="text-[11px] font-medium text-drs-text-secondary uppercase tracking-wider">Amount</label><input required type="number" step="0.01" {...inp("amount")} /></div>
          </div>
          <div className="space-y-1">
            <input type="hidden" {...inp("user_id")} />
            <label className="text-[11px] font-medium text-drs-text-secondary uppercase tracking-wider">Merchant ID</label>
            <input required placeholder="e.g. a UUID from your merchant list" {...inp("merchant_id")} />
          </div>
          <div className="space-y-1">
            <label className="text-[11px] font-medium text-drs-text-secondary uppercase tracking-wider">Reason</label>
            <select {...inp("reason_code")}>
              <option value="ITEM_NOT_RECEIVED">Item Not Received</option>
              <option value="ITEM_DEFECTIVE">Item Defective</option>
              <option value="INCORRECT_AMOUNT">Incorrect Amount</option>
              <option value="UNAUTHORIZED_TRANSACTION">Unauthorized Transaction</option>
              <option value="SUBSCRIPTION_CANCELLED">Subscription Cancelled</option>
            </select>
          </div>
          <div className="space-y-1"><label className="text-[11px] font-medium text-drs-text-secondary uppercase tracking-wider">Narrative</label><textarea rows={3} {...inp("user_narrative")} className={`${inp("user_narrative").className} resize-none`} /></div>
          {err && <div className="px-3 py-2 rounded-lg bg-semantic-red/5 border border-semantic-red/10 text-xs text-semantic-red">{err}</div>}
          <button type="submit" disabled={busy} className="w-full py-2.5 rounded-lg bg-drs-accent text-white font-medium text-sm hover:bg-drs-accent-soft transition-colors disabled:opacity-50">
            {busy ? "Filing..." : "File dispute"}
          </button>
        </form>
      </div>
    </div>
  );
}

function Detail({ dispute, onBack }) {
  const toast = useToast();
  const [live, setLive] = useState(dispute);
  const update = useCallback((u) => setLive((p) => ({ ...p, ...u })), []);
  useDisputeSSE(dispute?.id, update, () => {});
  const d = live || dispute;
  if (!d) return null;

  const handleUpload = async (file) => {
    try {
      await uploadEvidence(d.id, file, "USER");
      toast?.("Evidence uploaded successfully");
      setLive(await fetchDispute(d.id));
    } catch (ex) { toast?.(ex.message, "error"); }
  };

  return (
    <div className="max-w-4xl mx-auto px-6 py-8 space-y-6">
      <button onClick={onBack} className="text-xs text-drs-text-light hover:text-drs-text-secondary transition-colors">&larr; Back to disputes</button>
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
          <h3 className="text-xs font-semibold text-drs-text-secondary uppercase tracking-wider">Upload evidence</h3>
          <UploadZone onUpload={handleUpload} />
        </div>
      )}
    </div>
  );
}

export default function CustomerPortal() {
  const auth = getAuth();
  const [disputes, setDisputes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState(null);
  const [showCreate, setShowCreate] = useState(false);
  const [query, setQuery] = useState("");

  const load = async () => {
    try { setDisputes(await fetchDisputes({ userId: auth?.id })); } catch (e) { console.error(e); } finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const view = async (id) => {
    try { setSelected(await fetchDispute(id)); } catch (e) { console.error(e); }
  };

  const filtered = disputes.filter((d) =>
    d.transaction_id.toLowerCase().includes(query.toLowerCase()) ||
    d.reason_code.toLowerCase().includes(query.toLowerCase())
  );

  if (selected) return <PortalLayout><Detail dispute={selected} onBack={() => setSelected(null)} /></PortalLayout>;

  return (
    <PortalLayout>
      <div className="max-w-5xl mx-auto px-4 sm:px-6 pb-20 sm:pb-8 space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h1 className="text-xl font-bold text-drs-text">My disputes</h1>
            <p className="text-xs text-drs-text-secondary mt-0.5">Track and manage your chargeback disputes</p>
          </div>
          <button onClick={() => setShowCreate(true)} className="flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg bg-drs-accent text-white font-medium text-xs hover:bg-drs-accent-soft transition-colors active:scale-95 touch-manipulation">
            <Plus className="w-3.5 h-3.5" /> New dispute
          </button>
        </div>

        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-drs-text-light" />
          <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search..." className="w-full pl-9 pr-3 py-2 rounded-lg border border-drs-border text-drs-text text-sm bg-white focus:outline-none focus:border-drs-accent-soft transition-colors" />
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
          <div className="text-center py-16 space-y-2">
            <Scale className="w-8 h-8 text-drs-text-light mx-auto" />
            <p className="text-sm text-drs-text-secondary">No disputes found</p>
            <button onClick={() => setShowCreate(true)} className="text-xs text-drs-accent-soft hover:underline">File your first dispute</button>
          </div>
        ) : (
          <div className="space-y-2">
            {filtered.map((d) => (
              <button key={d.id} onClick={() => view(d.id)} className="w-full bg-white rounded-xl border border-drs-border p-4 text-left hover:shadow-card-hover transition-shadow">
                <div className="flex items-center justify-between gap-4">
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      <FileText className="w-3.5 h-3.5 text-drs-accent-soft shrink-0" />
                      <span className="text-sm font-medium text-drs-text truncate">#{d.transaction_id}</span>
                    </div>
                    <p className="text-xs text-drs-text-secondary mt-0.5">{d.reason_code?.replace(/_/g, " ")} &middot; {d.currency} {d.amount}</p>
                  </div>
                  <span className={`text-[11px] font-medium px-1.5 py-0.5 rounded shrink-0 ${
                    d.status === "INITIATED" ? "bg-drs-accent-subtle text-drs-accent-soft" :
                    d.status === "EVIDENCE_GATHERING" ? "bg-semantic-amber/5 text-semantic-amber" :
                    d.status === "UNDER_REVIEW" ? "bg-drs-accent-subtle text-drs-accent-soft" :
                    "bg-semantic-emerald/5 text-semantic-emerald"
                  }`}>{STATUS_LABELS[d.status] || d.status}</span>
                </div>
              </button>
            ))}
          </div>
        )}
      </div>

      {showCreate && <CreateModal onClose={() => setShowCreate(false)} onCreated={load} />}
    </PortalLayout>
  );
}
