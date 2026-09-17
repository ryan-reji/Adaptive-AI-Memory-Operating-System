import { useState } from "react";
import { FileText, Globe, Code2, FolderOpen, Mail, X } from "lucide-react";

const sourceIcons = {
  browser: Globe,
  pdf: FileText,
  vscode: Code2,
  files: FolderOpen,
  email: Mail,
};

const statusLabel = {
  kept: { text: "Kept", color: "text-kept-500" },
  summarized: { text: "Summarized", color: "text-glow-400" },
  archived: { text: "Archived", color: "text-mist-300" },
};

function formatDate(iso) {
  const d = new Date(iso);
  return d.toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" });
}

export default function MemoryCard({ memory, onForget }) {
  const Icon = sourceIcons[memory.source] || FileText;
  const status = statusLabel[memory.status] || statusLabel.kept;
  const importancePct = Math.round(memory.importance * 100);
  const [confirming, setConfirming] = useState(false);

  function handleForgetClick() {
    if (!confirming) {
      setConfirming(true);
      return;
    }
    onForget?.(memory.id);
  }

  return (
    <div className="bg-ink-900 border border-ink-700 rounded-lg p-4 hover:border-ink-600 transition-colors group">
      <div className="flex items-start justify-between gap-4">
        <p className="text-sm text-mist-200 leading-relaxed">{memory.text}</p>
        <div className="shrink-0 flex items-start gap-3">
          <div className="text-right">
            <div className="text-[11px] font-[family-name:var(--font-mono)] text-glow-400">
              {importancePct}%
            </div>
            <div className="text-[10px] text-mist-300 mt-0.5">relevance</div>
          </div>
          {onForget && (
            <button
              onClick={handleForgetClick}
              onBlur={() => setConfirming(false)}
              title={confirming ? "Click again to confirm" : "Forget this memory"}
              className={`opacity-0 group-hover:opacity-100 focus:opacity-100 transition-opacity p-1 rounded ${
                confirming
                  ? "opacity-100 bg-fade-500/20 text-fade-500"
                  : "text-mist-300 hover:text-fade-500"
              }`}
            >
              <X size={14} strokeWidth={2} />
            </button>
          )}
        </div>
      </div>
      {confirming && (
        <div className="text-[11px] text-fade-500 mt-1">Click the X again to forget this permanently.</div>
      )}

      <div className="mt-3 flex items-center justify-between text-[11px] text-mist-300">
        <div className="flex items-center gap-3">
          <span className="flex items-center gap-1.5">
            <Icon size={13} strokeWidth={1.75} />
            {memory.sourceLabel}
          </span>
          <span className="text-ink-600">•</span>
          <span>{memory.project}</span>
        </div>
        <div className="flex items-center gap-2 font-[family-name:var(--font-mono)]">
          <span className={status.color}>{status.text}</span>
          <span className="text-ink-600">·</span>
          <span>{formatDate(memory.timestamp)}</span>
        </div>
      </div>
    </div>
  );
}