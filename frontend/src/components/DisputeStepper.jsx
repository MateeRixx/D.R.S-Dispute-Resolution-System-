import { Check, FileText, Clock, Shield, Gavel, Scale } from "lucide-react";

const STEPS = [
  { key: "INITIATED", label: "Initiated", icon: FileText },
  { key: "EVIDENCE_GATHERING", label: "Gathering evidence", icon: Clock },
  { key: "UNDER_REVIEW", label: "Under review", icon: Shield },
  { key: "DECISION_RENDERED", label: "Decision", icon: Gavel },
  { key: "CLOSED", label: "Closed", icon: Scale },
];

const ORDER = {
  INITIATED: 0, EVIDENCE_GATHERING: 1, UNDER_REVIEW: 2,
  DECISION_RENDERED: 3, CLOSED: 4,
};

export default function DisputeStepper({ currentStatus }) {
  const current = ORDER[currentStatus] ?? 0;

  return (
    <div className="w-full">
      <div className="flex items-center justify-between">
        {STEPS.map((s, i) => {
          const done = i < current;
          const active = i === current;
          const Icon = s.icon;

          return (
            <div key={s.key} className="flex items-center flex-1 last:flex-none">
              <div className="flex flex-col items-center gap-1.5">
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center text-xs transition-all ${
                    done
                      ? "bg-semantic-emerald/10 text-semantic-emerald"
                      : active
                      ? "bg-drs-accent-subtle text-drs-accent-soft ring-2 ring-drs-accent-soft/20"
                      : "bg-drs-card text-drs-text-light"
                  }`}
                >
                  {done ? <Check className="w-4 h-4" /> : <Icon className="w-4 h-4" />}
                </div>
                <span className={`text-[11px] font-medium text-center hidden sm:block ${
                  active ? "text-drs-accent" : done ? "text-semantic-emerald" : "text-drs-text-light"
                }`}>
                  {s.label}
                </span>
              </div>
              {i < STEPS.length - 1 && (
                <div className={`flex-1 h-[2px] mx-2 rounded-full ${i < current ? "bg-semantic-emerald/30" : "bg-drs-border"}`} />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
