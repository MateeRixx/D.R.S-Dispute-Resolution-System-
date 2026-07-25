import { AlertTriangle, ThumbsUp, ThumbsDown, HelpCircle } from "lucide-react";

const CONFIG = {
  REFUND_USER: {
    label: "Refund user", color: "text-semantic-emerald", bg: "bg-semantic-emerald/5", border: "border-semantic-emerald/20", icon: ThumbsUp,
  },
  REJECT_CLAIM: {
    label: "Claim rejected", color: "text-semantic-red", bg: "bg-semantic-red/5", border: "border-semantic-red/20", icon: ThumbsDown,
  },
  PARTIAL_REFUND: {
    label: "Partial refund", color: "text-semantic-amber", bg: "bg-semantic-amber/5", border: "border-semantic-amber/20", icon: AlertTriangle,
  },
  NEEDS_HUMAN_INTERVENTION: {
    label: "Needs review", color: "text-drs-accent-soft", bg: "bg-drs-accent-subtle", border: "border-drs-accent-soft/20", icon: HelpCircle,
  },
};

export default function VerdictCard({ verdict, confidenceScore, summary, reasonCode }) {
  if (!verdict) return null;
  const c = CONFIG[verdict] || CONFIG.NEEDS_HUMAN_INTERVENTION;
  const Icon = c.icon;
  const pct = confidenceScore ? Math.round(confidenceScore * 100) : null;

  return (
    <div className={`rounded-xl border ${c.border} ${c.bg} p-5`}>
      <div className="flex items-start gap-3">
        <div className={`p-2 rounded-lg ${c.bg}`}>
          <Icon className={`w-5 h-5 ${c.color}`} />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <h3 className={`text-sm font-semibold ${c.color}`}>{c.label}</h3>
            {pct !== null && (
              <span className="text-[11px] font-medium px-1.5 py-0.5 rounded bg-white/80 text-drs-text-secondary border border-drs-border">
                {pct}% confidence
              </span>
            )}
          </div>
          {reasonCode && <p className="text-xs text-drs-text-secondary mt-0.5">{reasonCode.replace(/_/g, " ")}</p>}
          {summary && <p className="text-sm text-drs-text mt-3 leading-relaxed">{summary}</p>}
        </div>
      </div>
    </div>
  );
}
