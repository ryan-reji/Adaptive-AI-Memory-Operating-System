import { useEffect, useRef, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { searchMemories, forgetMemory, getProjects } from "../lib/api";
import SearchBar from "../components/SearchBar";
import MemoryCard from "../components/MemoryCard";
import { useToast } from "../components/Toast";

export default function SearchPage() {
  const [params, setParams] = useSearchParams();
  const initialQuery = params.get("q") || "";
  const [query, setQuery] = useState(initialQuery);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [projects, setProjects] = useState([]);
  const [projectFilter, setProjectFilter] = useState("all");
  const searchInputRef = useRef(null);
  const showToast = useToast();

  async function runSearch(q) {
    if (!q.trim()) return;
    setLoading(true);
    const res = await searchMemories(q);
    setResults(res);
    setLoading(false);
  }

  useEffect(() => {
    if (initialQuery) runSearch(initialQuery);
    getProjects().then(setProjects);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
  searchInputRef.current?.focus();
}, []);

  function handleSubmit() {
    setParams({ q: query });
    runSearch(query);
  }

  async function handleForget(id) {
    await forgetMemory(id);
    setResults((prev) => prev.filter((m) => m.id !== id));
    showToast("Memory forgotten");
  }

  const filteredResults =
    projectFilter === "all"
      ? results
      : results?.filter((m) => m.project === projectFilter);

  return (
    <div className="p-8 max-w-4xl mx-auto space-y-6">
      <div>
        <h2 className="font-[family-name:var(--font-display)] text-2xl text-paper-100">
          Search your memory
        </h2>
        <p className="text-sm text-mist-300 mt-1">
          Results are ranked by relevance, not just recency — and show exactly where each memory came from.
        </p>
      </div>

      <div className="flex items-center gap-3">
        <div className="flex-1">
          <SearchBar
            ref={searchInputRef}
            value={query}
            onChange={setQuery}
            onSubmit={handleSubmit}
            loading={loading}
          />
        </div>
        <select
          value={projectFilter}
          onChange={(e) => setProjectFilter(e.target.value)}
          className="bg-ink-900 border border-ink-700 rounded-lg px-3 py-3 text-sm text-mist-200 outline-none focus:border-glow-500"
        >
          <option value="all">All projects</option>
          {projects.map((p) => (
            <option key={p.id} value={p.name}>
              {p.name}
            </option>
          ))}
        </select>
      </div>
      <div className="text-[11px] text-mist-300 -mt-4">
        Tip: press <kbd className="px-1 py-0.5 bg-ink-800 rounded border border-ink-600">Ctrl/Cmd + K</kbd> to jump here from anywhere.
      </div>

      <div className="space-y-2.5">
        {loading && <div className="text-sm text-mist-300 py-6 text-center">Searching…</div>}
        {!loading && filteredResults !== null && filteredResults.length === 0 && (
          <div className="text-sm text-mist-300 py-10 text-center border border-dashed border-ink-700 rounded-lg">
            No memories matched "{initialQuery}". Try a different phrase or check Settings to
            confirm capture is on for the source you're expecting.
          </div>
        )}
        {!loading &&
          filteredResults !== null &&
          filteredResults.map((m) => (
            <MemoryCard key={m.id} memory={m} onForget={handleForget} />
          ))}
        {!loading && results === null && (
          <div className="text-sm text-mist-300 py-10 text-center">
            Type a question above to search across everything you've captured.
          </div>
        )}
      </div>
    </div>
  );
}