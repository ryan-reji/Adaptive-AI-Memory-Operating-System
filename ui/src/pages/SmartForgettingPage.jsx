import { useEffect, useState } from "react";
import {
  getForgettingCandidates,
  getForgettingStats,
  dismissCandidate,
  keepFile,
  dismissAllCandidates,
  runForgettingAnalysis,
} from "../lib/api";
import ErrorState from "../components/ErrorState";
import { useToast } from "../components/Toast";
import {
  FileQuestion,
  ShieldCheck,
  RefreshCw,
  AlertTriangle,
  CheckCircle2,
  Cpu,
  Brain,
} from "lucide-react";

function formatSize(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function formatDate(iso) {
  const d = new Date(iso);
  return d.toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" });
}

function ConfidenceBar({ confidence }) {
  const pct = Math.round((confidence ?? 0) * 100);
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-1 bg-ink-700 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full ${pct >= 70 ? "bg-glow-500" : "bg-fade-500"}`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="text-[10px] text-mist-300 tabular-nums w-8 text-right">{pct}%</span>
    </div>
  );
}

function SourceBadge({ source }) {
  if (source === "random_forest") {
    return (
      <span className="flex items-center gap-1 text-[10px] text-mist-300">
        <Cpu size={10} /> RF model
      </span>
    );
  }
  if (source === "ollama") {
    return (
      <span className="flex items-center gap-1 text-[10px] text-mist-300">
        <Brain size={10} /> LLM fallback
      </span>
    );
  }
  return (
    <span className="flex items-center gap-1 text-[10px] text-mist-300">
      <AlertTriangle size={10} /> {source || "unknown"}
    </span>
  );
}

function CandidateCard({ rec, onKeep, onDismiss, busy }) {
  return (
    <div className="bg-ink-900 border border-ink-700 rounded-lg p-4 space-y-3 hover:border-ink-600 transition-colors">
      {/* File name + actions */}
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-start gap-2.5 flex-1 min-w-0">
          <FileQuestion size={16} className="text-glow-400 mt-0.5 shrink-0" />
          <div className="min-w-0">
            <p className="text-sm text-paper-100 font-medium truncate">{rec.file_name}</p>
            <p className="text-[11px] text-mist-300 font-[family-name:var(--font-mono)] truncate mt-0.5">
              {rec.file_path}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-1.5 shrink-0">
          <button
            onClick={() => onKeep(rec.id)}
            disabled={busy}
            title="Keep this file — don't show again"
            className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-md text-[11px] bg-ink-800 border border-ink-700 text-mist-200 hover:border-kept-500 hover:text-kept-400 transition-colors disabled:opacity-40"
          >
            <ShieldCheck size={12} />
            Keep
          </button>
          <button
            onClick={() => onDismiss(rec.id)}
            disabled={busy}
            title="Dismiss this recommendation"
            className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-md text-[11px] bg-ink-800 border border-ink-700 text-mist-200 hover:border-glow-500 hover:text-glow-400 transition-colors disabled:opacity-40"
          >
            <CheckCircle2 size={12} />
            Dismiss
          </button>
        </div>
      </div>

      {/* Reason */}
      <div className="flex items-start gap-2">
        <AlertTriangle size={11} className="text-glow-500 mt-0.5 shrink-0" />
        <p className="text-[11px] text-mist-300 leading-relaxed">{rec.reason}</p>
      </div>

      {/* Confidence + source */}
      <div className="space-y-1.5">
        <div className="flex justify-between">
          <span className="text-[10px] text-mist-300">Confidence</span>
          <SourceBadge source={rec.prediction_source} />
        </div>
        <ConfidenceBar confidence={rec.confidence} />
      </div>

      {/* Footer meta */}
      <div className="flex items-center justify-between text-[11px] text-mist-300 pt-1 border-t border-ink-700">
        <span>{formatSize(rec.file_size_bytes)}</span>
        <span className="font-[family-name:var(--font-mono)]">Scanned {formatDate(rec.last_scanned_at)}</span>
      </div>
    </div>
  );
}

function StatCard({ label, value, sub }) {
  return (
    <div className="bg-ink-900 border border-ink-700 rounded-lg p-4 flex-1">
      <div className="text-2xl font-[family-name:var(--font-display)] text-paper-100">{value}</div>
      <div className="text-xs text-mist-300 mt-1">{label}</div>
      {sub && <div className="text-[11px] text-glow-400 mt-2">{sub}</div>}
    </div>
  );
}

export default function SmartForgettingPage() {
  const [candidates, setCandidates] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const showToast = useToast();

  function load(silent = false) {
    if (!silent) setLoading(true);
    setError(null);
    Promise.all([getForgettingCandidates(), getForgettingStats()])
      .then(([cands, s]) => {
        setCandidates(cands);
        setStats(s);
        setLoading(false);
      })
      .catch(() => {
        setError("Can't reach the backend. Make sure it's running on port 8000.");
        setLoading(false);
      });
  }

  useEffect(() => { load(); }, []);

  async function handleKeep(id) {
    setBusy(true);
    try {
      await keepFile(id);
      setCandidates((prev) => prev.filter((c) => c.id !== id));
      showToast("Marked as keep");
    } catch {
      showToast("Couldn't update — backend unreachable");
    } finally {
      setBusy(false);
    }
  }

  async function handleDismiss(id) {
    setBusy(true);
    try {
      await dismissCandidate(id);
      setCandidates((prev) => prev.filter((c) => c.id !== id));
      showToast("Recommendation dismissed");
    } catch {
      showToast("Couldn't update — backend unreachable");
    } finally {
      setBusy(false);
    }
  }

  async function handleDismissAll() {
    if (candidates.length === 0) return;
    setBusy(true);
    try {
      await dismissAllCandidates();
      setCandidates([]);
      showToast(`Dismissed ${candidates.length} recommendations`);
    } catch {
      showToast("Couldn't dismiss — backend unreachable");
    } finally {
      setBusy(false);
    }
  }

  async function handleRunAnalysis() {
    setAnalyzing(true);
    try {
      await runForgettingAnalysis();
      showToast("Scan complete — refreshing…");
      load(true);
    } catch {
      showToast("Couldn't run scan — backend unreachable");
    } finally {
      setAnalyzing(false);
    }
  }

  return (
    <div className="p-8 max-w-3xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h2 className="font-[family-name:var(--font-display)] text-2xl text-paper-100">
            Smart Forgetting
          </h2>
          <p className="text-sm text-mist-300 mt-1">
            Files the system thinks are worth reviewing. Nothing is ever auto-deleted.
          </p>
        </div>
        <button
          onClick={handleRunAnalysis}
          disabled={analyzing || loading}
          className="flex items-center gap-2 px-3 py-2 bg-ink-900 border border-ink-700 rounded-lg text-sm text-mist-200 hover:border-glow-500 transition-colors disabled:opacity-40"
        >
          <RefreshCw size={13} className={analyzing ? "animate-spin" : ""} />
          {analyzing ? "Scanning…" : "Run scan"}
        </button>
      </div>

      {error ? (
        <ErrorState message={error} onRetry={() => load()} />
      ) : (
        <>
          {/* Stats row */}
          <div className="flex gap-4">
            <StatCard
              label="Files scanned"
              value={loading ? "—" : (stats?.total_files_scanned ?? "—")}
            />
            <StatCard
              label="Review candidates"
              value={loading ? "—" : candidates.length}
              sub={candidates.length > 0 ? "Review below" : undefined}
            />
            <StatCard
              label="Kept"
              value={loading ? "—" : (stats?.kept ?? "—")}
            />
          </div>

          {/* Last scan timestamp */}
          {stats?.last_scan && (
            <p className="text-[11px] text-mist-300 -mt-4">
              Last scan: {formatDate(stats.last_scan)} at{" "}
              {new Date(stats.last_scan).toLocaleTimeString(undefined, { hour: "2-digit", minute: "2-digit" })}
            </p>
          )}

          {/* Candidates list */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-medium text-mist-200">
                Review candidates
                {candidates.length > 0 && (
                  <span className="ml-2 text-[11px] text-mist-300 font-normal">
                    ({candidates.length} flagged)
                  </span>
                )}
              </h3>
              {candidates.length > 1 && (
                <button
                  onClick={handleDismissAll}
                  disabled={busy}
                  className="flex items-center gap-1.5 text-[11px] text-mist-300 hover:text-glow-400 transition-colors disabled:opacity-40"
                >
                  <CheckCircle2 size={11} />
                  Dismiss all
                </button>
              )}
            </div>

            {loading ? (
              <div className="text-sm text-mist-300 py-8 text-center">
                Loading recommendations…
              </div>
            ) : candidates.length === 0 ? (
              <div className="text-sm text-mist-300 py-8 text-center border border-dashed border-ink-700 rounded-lg">
                No files flagged for review. The runner scans every 12 hours, or run a scan manually above.
              </div>
            ) : (
              <div className="space-y-3">
                {candidates.map((rec) => (
                  <CandidateCard
                    key={rec.id}
                    rec={rec}
                    onKeep={handleKeep}
                    onDismiss={handleDismiss}
                    busy={busy}
                  />
                ))}
              </div>
            )}
          </div>

          {/* Info note */}
          <p className="text-[11px] text-mist-300 border-t border-ink-700 pt-4">
            Smart Forgetting runs as a separate background process
            (<code className="text-glow-400">python -m memory.smart_forgetting.runner</code>),
            not through the orchestrator. It uses a Random Forest model with Ollama LLM fallback
            for low-confidence predictions. "Review" is a suggestion to inspect — the system never
            deletes files automatically.
          </p>
        </>
      )}
    </div>
  );
}
