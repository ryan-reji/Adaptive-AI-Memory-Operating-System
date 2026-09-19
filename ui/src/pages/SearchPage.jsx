import { useEffect, useRef, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { askQuery, getMemories } from "../lib/api";
import { toDisplayMemory } from "../lib/memoryAdapter";
import SearchBar from "../components/SearchBar";
import MemoryCard from "../components/MemoryCard";
import ErrorState from "../components/ErrorState";

export default function SearchPage() {
  const [params, setParams] = useSearchParams();
  const initialQuery = params.get("q") || "";
  const [query, setQuery] = useState(initialQuery);
  const [answer, setAnswer] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [allMemories, setAllMemories] = useState([]);
  const searchInputRef = useRef(null);

  useEffect(() => {
    getMemories(200, 0)
      .then((data) => setAllMemories(data.map(toDisplayMemory)))
      .catch(() => {});
    searchInputRef.current?.focus();
  }, []);

  async function runQuery(q) {
    if (!q.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const res = await askQuery(q);
      setAnswer(res);
    } catch {
      setError("Couldn't reach the AI engine. Make sure the backend and Ollama are running.");
    }
    setLoading(false);
  }

  useEffect(() => {
    if (initialQuery) runQuery(initialQuery);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function handleSubmit() {
    setParams({ q: query });
    runQuery(query);
  }

  const relatedMemories = query.trim()
    ? allMemories.filter((m) => m.text.toLowerCase().includes(query.toLowerCase())).slice(0, 5)
    : [];

  return (
    <div className="p-8 max-w-4xl mx-auto space-y-6">
      <div>
        <h2 className="font-[family-name:var(--font-display)] text-2xl text-paper-100">Ask your memory</h2>
        <p className="text-sm text-mist-300 mt-1">
          Answers are generated from what's actually been captured — nothing here leaves your device.
        </p>
      </div>

      <SearchBar ref={searchInputRef} value={query} onChange={setQuery} onSubmit={handleSubmit} loading={loading} placeholder="Ask a question…" />

      {loading && <div className="text-sm text-mist-300 py-6 text-center">Thinking…</div>}

      {!loading && error && <ErrorState message={error} onRetry={() => runQuery(query)} />}

      {!loading && !error && answer && (
        <div className="bg-ink-900 border border-ink-700 rounded-lg p-5">
          <div className="text-[11px] text-glow-400 mb-2 font-[family-name:var(--font-mono)]">
            {answer.retrieval_time_ms?.toFixed(1)}ms
          </div>
          <p className="text-sm text-mist-200 leading-relaxed">{answer.answer}</p>
        </div>
      )}

      {relatedMemories.length > 0 && (
        <div>
          <h3 className="text-sm font-medium text-mist-200 mb-3">Related activity</h3>
          <div className="space-y-2.5">
            {relatedMemories.map((m) => <MemoryCard key={m.id} memory={m} />)}
          </div>
        </div>
      )}

      {!loading && !error && !answer && (
        <div className="text-sm text-mist-300 py-10 text-center">Ask a question to search what's been captured.</div>
      )}
    </div>
  );
}