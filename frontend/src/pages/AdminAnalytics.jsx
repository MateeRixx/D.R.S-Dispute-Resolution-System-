import { useState, useEffect } from "react";
import { BarChart3, TrendingUp, Shield, Gavel, Download, Calendar } from "lucide-react";
import PortalLayout from "../components/PortalLayout";


const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

function getToken() {
  return localStorage.getItem("drs_token");
}

function StatCard({ icon: Icon, label, value, sub, color }) {
  return (
    <div className="bg-white rounded-xl border border-drs-border p-4 sm:p-5">
      <div className="flex items-center gap-3">
        <div className={`p-2 rounded-lg ${color || "bg-drs-accent-subtle"}`}>
          <Icon className={`w-4 h-4 ${color ? "text-white" : "text-drs-accent-soft"}`} />
        </div>
        <div className="min-w-0">
          <p className="text-2xl sm:text-3xl font-bold text-drs-text">{value}</p>
          <p className="text-xs text-drs-text-secondary truncate">{label}</p>
          {sub && <p className="text-[11px] text-drs-text-light">{sub}</p>}
        </div>
      </div>
    </div>
  );
}

function BarChart({ data, labelKey, valueKey, color = "bg-drs-accent-soft" }) {
  const max = Math.max(...data.map((d) => d[valueKey]), 1);
  return (
    <div className="space-y-2">
      {data.map((d, i) => (
        <div key={i} className="flex items-center gap-3">
          <span className="text-xs text-drs-text-secondary w-24 sm:w-32 truncate shrink-0 text-right">{d[labelKey]}</span>
          <div className="flex-1 bg-drs-card rounded-full h-5 overflow-hidden">
            <div
              className={`h-full rounded-full ${color} transition-all duration-500`}
              style={{ width: `${(d[valueKey] / max) * 100}%` }}
            />
          </div>
          <span className="text-xs font-medium text-drs-text w-8 text-left shrink-0">{d[valueKey]}</span>
        </div>
      ))}
    </div>
  );
}

function PieChart({ data, labelKey, valueKey, colors }) {
  const total = data.reduce((s, d) => s + d[valueKey], 0) || 1;
  let offset = 0;
  return (
    <div className="flex flex-col sm:flex-row items-center gap-6">
      <svg width="120" height="120" viewBox="0 0 120 120" className="shrink-0">
        {data.map((d, i) => {
          const pct = d[valueKey] / total;
          const r = 50;
          const circumference = 2 * Math.PI * r;
          const length = pct * circumference;
          if (length === 0) return null;
          const dash = `${length} ${circumference - length}`;
          const rotate = (offset / circumference) * 360;
          offset += length;
          return (
            <circle
              key={i}
              cx="60" cy="60" r={r}
              fill="none"
              stroke={colors?.[i] || "#1A3C5E"}
              strokeWidth="16"
              strokeDasharray={dash}
              transform={`rotate(${rotate} 60 60)`}
              className="transition-all duration-500"
            />
          );
        })}
        <circle cx="60" cy="60" r="38" fill="white" />
        <text x="60" y="56" textAnchor="middle" className="text-lg font-bold" fill="#1C1917">{total}</text>
        <text x="60" y="70" textAnchor="middle" className="text-[9px]" fill="#6B6560">total</text>
      </svg>
      <div className="space-y-1.5">
        {data.map((d, i) => (
          <div key={i} className="flex items-center gap-2">
            <div className="w-2.5 h-2.5 rounded-full shrink-0" style={{ backgroundColor: colors?.[i] || "#1A3C5E" }} />
            <span className="text-xs text-drs-text-secondary">{d[labelKey]}</span>
            <span className="text-xs font-medium text-drs-text ml-auto">{(d[valueKey] / total * 100).toFixed(0)}%</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function exportCSV(stats) {
  const rows = [["Metric", "Value"]];
  rows.push(["Total Disputes", stats.total_disputes]);
  rows.push(["Resolution Rate", `${stats.resolution_rate}%`]);
  rows.push(["Avg Confidence", stats.avg_confidence]);
  for (const [k, v] of Object.entries(stats.by_status || {})) rows.push([`Status: ${k}`, v]);
  for (const [k, v] of Object.entries(stats.by_verdict || {})) rows.push([`Verdict: ${k}`, v]);
  for (const [k, v] of Object.entries(stats.by_reason_code || {})) rows.push([`Reason: ${k}`, v]);
  const csv = rows.map((r) => r.join(",")).join("\n");
  const blob = new Blob([csv], { type: "text/csv" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url; a.download = "drs-analytics.csv"; a.click();
  URL.revokeObjectURL(url);
}

export default function AdminAnalytics() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [dateRange, setDateRange] = useState({ start: "", end: "" });

  const fetch = async () => {
    setLoading(true);
    try {
      const token = getToken();
      const params = new URLSearchParams();
      if (dateRange.start) params.set("start_date", dateRange.start);
      if (dateRange.end) params.set("end_date", dateRange.end);
      const qs = params.toString();
      const res = await fetch(`${BASE_URL}/admin/stats${qs ? `?${qs}` : ""}`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (!res.ok) throw new Error("Failed to load stats");
      setStats(await res.json());
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetch(); }, []);

  const statusColors = {
    INITIATED: "#9C958E", EVIDENCE_GATHERING: "#B45309",
    UNDER_REVIEW: "#2E5C8A", DECISION_RENDERED: "#059669", CLOSED: "#1A3C5E",
  };
  const verdictColors = ["#059669", "#DC2626", "#B45309", "#2E5C8A"];


  return (
    <PortalLayout>
      <div className="max-w-6xl mx-auto px-4 sm:px-6 pb-24 sm:pb-8 space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-drs-accent-soft shrink-0" />
            <h1 className="text-xl font-bold text-drs-text">Analytics</h1>
          </div>
          <div className="flex items-center gap-2">
            <div className="flex items-center gap-1.5 text-xs text-drs-text-light">
              <Calendar className="w-3.5 h-3.5" />
              <input type="date" value={dateRange.start} onChange={(e) => setDateRange({ ...dateRange, start: e.target.value })} className="bg-drs-card rounded px-2 py-1 border border-drs-border text-drs-text w-28 sm:w-auto" />
              <span>—</span>
              <input type="date" value={dateRange.end} onChange={(e) => setDateRange({ ...dateRange, end: e.target.value })} className="bg-drs-card rounded px-2 py-1 border border-drs-border text-drs-text w-28 sm:w-auto" />
            </div>
            <button onClick={fetch} className="text-xs px-2.5 py-1.5 rounded-lg bg-drs-accent text-white font-medium hover:bg-drs-accent-soft transition-colors">Apply</button>
            {stats && <button onClick={() => exportCSV(stats)} className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg border border-drs-border text-xs text-drs-text-secondary hover:bg-drs-card transition-colors"><Download className="w-3 h-3" /> CSV</button>}
          </div>
        </div>

        {loading ? (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            {[1,2,3,4].map((i) => <div key={i} className="bg-white rounded-xl border border-drs-border p-5 animate-pulse"><div className="h-8 bg-drs-card rounded w-1/2 mb-2" /><div className="h-3 bg-drs-card rounded w-3/4" /></div>)}
          </div>
        ) : !stats ? (
          <div className="text-center py-16"><BarChart3 className="w-8 h-8 text-drs-text-light mx-auto mb-2" /><p className="text-sm text-drs-text-secondary">No data yet. File some disputes to see analytics.</p></div>
        ) : (
          <>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <StatCard icon={Shield} label="Total Disputes" value={stats.total_disputes} color="bg-drs-accent" />
              <StatCard icon={TrendingUp} label="Resolution Rate" value={`${stats.resolution_rate}%`} color="bg-semantic-emerald" />
              <StatCard icon={Gavel} label="Avg Confidence" value={stats.avg_confidence} color="bg-drs-accent-soft" />
              <StatCard icon={BarChart3} label="Reason Codes" value={Object.keys(stats.by_reason_code || {}).length} sub="unique" />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white rounded-xl border border-drs-border p-4 sm:p-5">
                <h3 className="text-xs font-semibold text-drs-text-secondary uppercase tracking-wider mb-4">Disputes by Status</h3>
                <PieChart data={Object.entries(stats.by_status || {}).map(([k, v]) => ({ label: k, value: v }))} labelKey="label" valueKey="value" colors={Object.values(statusColors)} />
              </div>

              <div className="bg-white rounded-xl border border-drs-border p-4 sm:p-5">
                <h3 className="text-xs font-semibold text-drs-text-secondary uppercase tracking-wider mb-4">Disputes by Verdict</h3>
                <PieChart data={Object.entries(stats.by_verdict || {}).map(([k, v]) => ({ label: k, value: v }))} labelKey="label" valueKey="value" colors={verdictColors} />
              </div>

              <div className="bg-white rounded-xl border border-drs-border p-4 sm:p-5">
                <h3 className="text-xs font-semibold text-drs-text-secondary uppercase tracking-wider mb-4">Disputes by Reason Code</h3>
                <BarChart data={Object.entries(stats.by_reason_code || {}).map(([k, v]) => ({ label: k.replace(/_/g, " "), value: v }))} labelKey="label" valueKey="value" />
              </div>

              <div className="bg-white rounded-xl border border-drs-border p-4 sm:p-5">
                <h3 className="text-xs font-semibold text-drs-text-secondary uppercase tracking-wider mb-4">Disputes by Merchant</h3>
                <BarChart data={Object.entries(stats.by_merchant || {}).map(([k, v]) => ({ label: k, value: v }))} labelKey="label" valueKey="value" color="bg-semantic-emerald" />
              </div>
            </div>

            {stats.volume_over_time?.length > 0 && (
              <div className="bg-white rounded-xl border border-drs-border p-4 sm:p-5">
                <h3 className="text-xs font-semibold text-drs-text-secondary uppercase tracking-wider mb-4">Volume Over Time</h3>
                <div className="flex items-end gap-1 h-24 sm:h-32">
                  {stats.volume_over_time.map((d, i) => {
                    const maxVol = Math.max(...stats.volume_over_time.map((x) => x.count), 1);
                    const h = (d.count / maxVol) * 100;
                    return (
                      <div key={i} className="flex-1 flex flex-col items-center gap-1">
                        <div className="w-full bg-drs-accent-subtle rounded-t relative" style={{ height: `${h}%` }}>
                          <div className="absolute -top-4 left-1/2 -translate-x-1/2 text-[10px] text-drs-text-secondary">{d.count}</div>
                        </div>
                        <span className="text-[8px] text-drs-text-light truncate w-full text-center">{d.date?.slice(5, 10) || ""}</span>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </PortalLayout>
  );
}
