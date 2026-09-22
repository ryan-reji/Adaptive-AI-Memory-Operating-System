import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getMemories } from "../lib/api";
import { toDisplayMemory, groupByProject } from "../lib/memoryAdapter";
import SearchBar from "../components/SearchBar";
import MemoryCard from "../components/MemoryCard";
import ErrorState from "../components/ErrorState";
import { RotateCw } from "lucide-react";

function StatCard({ label, value, sub }) {
  return (
    <div className="bg-ink-900 border border-ink-700 rounded-lg p-4 flex-1">
      <div className="text-2xl font-[family-name:var(--font-display)] text-paper-100">{value}</div>
      <div className="text-xs text-mist-300 mt-1">{label}</div>
      {sub && <div className="text-[11px] text-glow-400 mt-2">{sub}</div>}
    </div>
  );
}

export default function Dashboard() {
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [query, setQuery] = useState("");
  const navigate = useNavigate();

  function load(silent = false) {
    if (!silent) setLoading(true);
    setError(null);
    getMemories(50, 0)
      .then((data) => {
        setRecords(data);
        setLoading(false);
      })
      .catch(() => {
        setError("Can't reach the backend. Make sure it's running on port 8000.");
        setLoading(false);
      });
  }

  useEffect(() => {
    load();
    // Poll every 15s so newly created memories show up without a manual reload —
    // "silent" so it doesn't flash the loading state on every refresh.
    const interval = setInterval(() => load(true), 15000);
    return () => clearInterval(interval);
  }, []);

  const memories = records.map(toDisplayMemory);
  const projects = groupByProject(records);
  const processedCount = records.filter((r) => r.ai_processed).length;

  function handleSubmit() {
    if (query.trim()) navigate(`/search?q=${encodeURIComponent(query)}`);
  }

  return (
    <div className="p-8 max-w-4xl mx-auto space-y-8">
      <div className="flex items-start justify-between">
        <div>
          <h2 className="font-[family-name:var(--font-display)] text-2xl text-paper-100">Good to see you.</h2>
          <p className="text-sm text-mist-300 mt-1">Everything below stays on this device.</p>
        </div>
        <button
          onClick={() => load()}
          className="text-mist-300 hover:text-glow-400 transition-colors p-1"
          title="Refresh now"
        >
          <RotateCw size={14} />
        </button>
      </div>

      <SearchBar value={query} onChange={setQuery} onSubmit={handleSubmit} placeholder="Ask about anything you've worked on…" />

      {error ? (
        <ErrorState message={error} onRetry={() => load()} />
      ) : (
        <>
          <div className="flex gap-4">
            <StatCard label="Memories captured" value={loading ? "—" : records.length} />
            <StatCard label="AI-processed" value={loading ? "—" : processedCount} />
            <StatCard label="Active projects" value={loading ? "—" : projects.length} />
          </div>

          <div>
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-medium text-mist-200">Recent activity</h3>
              <button onClick={() => navigate("/timeline")} className="text-[11px] text-glow-400 hover:text-glow-300">
                View timeline →
              </button>
            </div>
            <div className="space-y-2.5">
              {loading ? (
                <div className="text-sm text-mist-300 py-6 text-center">Loading memories…</div>
              ) : memories.length === 0 ? (
                <div className="text-sm text-mist-300 py-6 text-center border border-dashed border-ink-700 rounded-lg">
                  Nothing captured yet. Run the orchestrator to start capturing activity.
                </div>
              ) : (
                memories.slice(0, 4).map((m) => <MemoryCard key={m.id} memory={m} />)
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}