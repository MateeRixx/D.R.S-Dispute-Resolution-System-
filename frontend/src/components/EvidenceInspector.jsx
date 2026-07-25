import { Camera, FileText, Receipt } from "lucide-react";

function Card({ ev }) {
  const isImage = ev.file_type?.startsWith("image/");
  const ocr = ev.ocr_extracted_json;
  const vision = ev.ai_vision_analysis;

  return (
    <div className="bg-white rounded-xl border border-drs-border overflow-hidden">
      <div className="px-4 py-2.5 border-b border-drs-border flex items-center gap-2">
        {isImage ? <Camera className="w-3.5 h-3.5 text-drs-accent-soft" /> : <FileText className="w-3.5 h-3.5 text-drs-text-light" />}
        <span className="text-xs font-medium text-drs-text flex-1">{ev.uploaded_by} evidence</span>
        <span className="text-[11px] text-drs-text-light">{ev.file_type}</span>
      </div>

      {isImage && ev.storage_url && (
        <div className="relative bg-drs-bg">
          <img src={ev.storage_url} alt="" className="w-full h-40 object-contain" loading="lazy" />
          {vision?.defect_regions?.map((r, i) => (
            <div key={i} className="absolute border-2 border-semantic-red/50 rounded pointer-events-none"
              style={{ left: `${r.bbox?.[0] ?? 0}%`, top: `${r.bbox?.[1] ?? 0}%`, width: `${r.bbox?.[2] ?? 10}%`, height: `${r.bbox?.[3] ?? 10}%` }}
            />
          ))}
        </div>
      )}

      {ocr?.invoice_number && (
        <div className="px-4 py-3 space-y-1 text-xs">
          <div className="flex justify-between"><span className="text-drs-text-light">Invoice</span><span className="text-drs-text">{ocr.invoice_number}</span></div>
          {ocr.vendor_name && <div className="flex justify-between"><span className="text-drs-text-light">Vendor</span><span className="text-drs-text">{ocr.vendor_name}</span></div>}
          {ocr.total_amount && <div className="flex justify-between"><span className="text-drs-text-light">Amount</span><span className="text-drs-text font-medium">{ocr.currency || ""} {ocr.total_amount}</span></div>}
        </div>
      )}

      {vision?.defects_detected && (
        <div className="px-4 pb-3 flex flex-wrap gap-1.5">
          {vision.defect_regions.map((r, i) => (
            <span key={i} className="text-[11px] px-1.5 py-0.5 rounded bg-semantic-red/5 text-semantic-red border border-semantic-red/10">{r.label}</span>
          ))}
        </div>
      )}
    </div>
  );
}

export default function EvidenceInspector({ evidence = [] }) {
  if (!evidence.length) {
    return (
      <div className="bg-white rounded-xl border border-drs-border p-8 text-center">
        <Receipt className="w-6 h-6 text-drs-text-light mx-auto mb-2" />
        <p className="text-xs text-drs-text-light">No evidence uploaded yet</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <h3 className="text-xs font-semibold text-drs-text-secondary uppercase tracking-wider">Evidence ({evidence.length})</h3>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {evidence.map((ev) => <Card key={ev.id} ev={ev} />)}
      </div>
    </div>
  );
}
