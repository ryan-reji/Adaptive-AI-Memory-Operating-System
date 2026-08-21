import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getRecentMemories, getProjects, forgetMemory } from "../lib/api";
import SearchBar from "../components/SearchBar";
import MemoryCard from "../components/MemoryCard";
import { useToast } from "../components/Toast";

function StatCard({ label, value, sub }) {
  return (
    <div className="bg-ink-900 border border-ink-700 rounded-lg p-4 flex-1">
      <div className="text-2xl font-[family-name:var(--font-display)] text-paper-100">
        {value}
      </div>
      <div className="text-xs text-mist-300 mt-1">{label}</div>
      {sub && <div className="text-[11px] text-glow-400 mt-2">{sub}</div>}
    </div>
  );
}

export default function Dashboard() {
  const [memories, setMemories] = useState([]);
  const [projects, setProjects] = useState([]);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const showToast = useToast();

  useEffect(() => {
    Promise.all([getRecentMemories(), getProjects()]).then(([m, p]) => {
      setMemories(m);
      setProjects(p);
      setLoading(false);
    });
  }, []);

  const totalMemories = projects.reduce((sum, p) => sum + p.memoryCount, 0);

  function handleSubmit() {
    if (query.trim()) {
      navigate(`/search?q=${encodeURIComponent(query)}`);
    }
  }

  async function handleForget(id) {
    await forgetMemory(id);
    setMemories((prev) => prev.filter((m) => m.id !== id));
    showToast("Memory forgotten");
  }

  return (
    <div className="p-8 max-w-4xl mx-auto space-y-8">
      <div>
        <h2 className="font-[family-name:var(--font-display)] text-2xl text-paper-100">
          Good to see you.
        </h2>
        <p className="text-sm text-mist-300 mt-1">
          Everything below stays on this device.
        </p>
      </div>

      <SearchBar
        value={query}
        onChange={setQuery}
        onSubmit={handleSubmit}
        placeholder="Ask about anything you've worked on…"
      />

      <div className="flex gap-4">
        <StatCard label="Memories stored" value={loading ? "—" : totalMemories} />
        <StatCard label="Active projects" value={loading ? "—" : projects.length} />
        <StatCard
          label="Forgetting policy"
          value="Balanced"
          sub="Adjust in Settings"
        />
      </div>

      <div>
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-medium text-mist-200">Recent activity</h3>
          <button
            onClick={() => navigate("/timeline")}
            className="text-[11px] text-glow-400 hover:text-glow-300"
          >
            View timeline →
          </button>
        </div>
        <div className="space-y-2.5">
          {loading ? (
            <div className="text-sm text-mist-300 py-6 text-center">Loading memories…</div>
          ) : memories.length === 0 ? (
            <div className="text-sm text-mist-300 py-6 text-center border border-dashed border-ink-700 rounded-lg">
              Nothing captured yet. Turn on capture in Settings to get started.
            </div>
          ) : (
            memories.slice(0, 4).map((m) => <MemoryCard key={m.id} memory={m} onForget={handleForget} />)
          )}
        </div>
      </div>
    </div>
  );
}

