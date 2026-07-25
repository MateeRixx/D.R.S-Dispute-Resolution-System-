import { useCallback, useState, useRef } from "react";
import { Upload, CheckCircle, Loader, X } from "lucide-react";

export default function UploadZone({ onUpload, disabled }) {
  const [drag, setDrag] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [done, setDone] = useState(false);
  const [file, setFile] = useState(null);
  const [error, setError] = useState(null);
  const ref = useRef(null);

  const handle = useCallback(async (f) => {
    if (!f) return;
    setFile(f);
    setError(null);
    setUploading(true);
    try {
      await onUpload(f);
      setDone(true);
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  }, [onUpload]);

  const drop = useCallback((e) => {
    e.preventDefault();
    setDrag(false);
    handle(e.dataTransfer.files[0]);
  }, [handle]);

  return (
    <div className="space-y-2">
      <div
        onDrop={drop}
        onDragOver={(e) => { e.preventDefault(); setDrag(true); }}
        onDragLeave={() => setDrag(false)}
        onClick={() => ref.current?.click()}
        className={`rounded-xl border-2 border-dashed p-6 text-center cursor-pointer transition-all ${
          drag ? "border-drs-accent-soft bg-drs-accent-subtle" :
          done ? "border-semantic-emerald/40 bg-semantic-emerald/5" :
          "border-drs-border hover:border-drs-accent-soft/40 hover:bg-drs-card"
        } ${disabled ? "opacity-50 cursor-not-allowed" : ""}`}
      >
        <input ref={ref} type="file" accept="image/*,application/pdf" className="hidden"
          onChange={(e) => handle(e.target.files[0])} disabled={disabled} />

        {uploading ? (
          <div className="flex flex-col items-center gap-1.5">
            <Loader className="w-5 h-5 text-drs-accent-soft animate-spin" />
            <p className="text-xs text-drs-text-secondary">Uploading...</p>
          </div>
        ) : done ? (
          <div className="flex flex-col items-center gap-1.5">
            <CheckCircle className="w-5 h-5 text-semantic-emerald" />
            <p className="text-xs text-semantic-emerald font-medium">Uploaded</p>
            <p className="text-[11px] text-drs-text-light">{file?.name}</p>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-1.5">
            <Upload className="w-5 h-5 text-drs-text-light" />
            <p className="text-xs text-drs-text-secondary font-medium">{drag ? "Drop file" : "Drag & drop or click to browse"}</p>
            <p className="text-[11px] text-drs-text-light">Images and PDFs</p>
          </div>
        )}
      </div>

      {error && (
        <div className="flex items-center gap-1.5 px-3 py-2 rounded-lg bg-semantic-red/5 border border-semantic-red/10 text-xs text-semantic-red">
          <X className="w-3.5 h-3.5 shrink-0" /> {error}
        </div>
      )}

      {done && <button onClick={() => { setDone(false); setFile(null); }} className="text-[11px] text-drs-text-light hover:text-drs-text-secondary transition-colors">Upload another</button>}
    </div>
  );
}
