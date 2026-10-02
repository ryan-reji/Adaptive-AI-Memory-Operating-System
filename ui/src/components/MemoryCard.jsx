import { Globe, Code2, FolderOpen, CheckCircle2, Clock } from "lucide-react";

const sourceIcons = {
  browser: Globe,
  vscode: Code2,
  file: FolderOpen,
};

function formatDate(iso) {
  const d = new Date(iso);
  return d.toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" });
}

export default function MemoryCard({ memory }) {
  const Icon = sourceIcons[memory.source] || FolderOpen;

  return (
    <div className="bg-ink-900 border border-ink-700 rounded-lg p-4 hover:border-ink-600 transition-colors">
      <div className="flex items-start justify-between gap-4">
        <p className="text-sm text-mist-200 leading-relaxed">{memory.text}</p>
        <div className="shrink-0" title={memory.processed ? "Processed by AI engine" : "Not yet AI-processed"}>
          {memory.processed ? (
            <CheckCircle2 size={14} className="text-kept-500" />
          ) : (
            <Clock size={14} className="text-mist-300" />
          )}
        </div>
      </div>

      <div className="mt-3 flex items-center justify-between text-[11px] text-mist-300">
        <div className="flex items-center gap-3">
          <span className="flex items-center gap-1.5">
            <Icon size={13} strokeWidth={1.75} />
            {memory.sourceLabel}
          </span>
          <span className="text-ink-600">•</span>
          <span>{memory.project}</span>
        </div>
        <span className="font-[family-name:var(--font-mono)]">{formatDate(memory.timestamp)}</span>
      </div>
    </div>
  );
}