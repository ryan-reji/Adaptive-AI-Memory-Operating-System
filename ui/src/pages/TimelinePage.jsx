import { useEffect, useState } from "react";
import { getTimeline, getProjects } from "../lib/api";

function formatDate(iso) {
  const d = new Date(iso);
  return d.toLocaleDateString(undefined, { weekday: "short", month: "short", day: "numeric" });
}

export default function TimelinePage() {
  const [timeline, setTimeline] = useState([]);
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([getTimeline(), getProjects()]).then(([t, p]) => {
      setTimeline(t);
      setProjects(p);
      setLoading(false);
    });
  }, []);

  return (
    <div className="p-8 max-w-4xl mx-auto space-y-8">
      <div>
        <h2 className="font-[family-name:var(--font-display)] text-2xl text-paper-100">
          Timeline
        </h2>
        <p className="text-sm text-mist-300 mt-1">
          A thread through your work, day by day. Brighter days had more captured activity.
        </p>
      </div>

      <div>
        <h3 className="text-sm font-medium text-mist-200 mb-4">By day</h3>
        {loading ? (
          <div className="text-sm text-mist-300 py-6 text-center">Loading timeline…</div>
        ) : (
          <div className="memory-thread pl-8 space-y-5">
            {timeline.map((entry, i) => (
              <div key={i} className="relative">
                <div
                  className="absolute -left-8 top-1.5 w-[9px] h-[9px] rounded-full bg-glow-500"
                  style={{ opacity: 0.4 + Math.min(entry.count / 10, 0.6) }}
                />
                <div className="flex items-baseline gap-3">
                  <span className="text-sm text-paper-100 font-medium">
                    {formatDate(entry.date)}
                  </span>
                  <span className="text-[11px] font-[family-name:var(--font-mono)] text-glow-400">
                    {entry.count} memories
                  </span>
                </div>
                <div className="text-xs text-mist-300 mt-0.5">
                  {entry.projects.join(", ")}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div>
        <h3 className="text-sm font-medium text-mist-200 mb-4">By project</h3>
        <div className="grid grid-cols-2 gap-3">
          {projects.map((p) => (
            <div
              key={p.id}
              className="bg-ink-900 border border-ink-700 rounded-lg p-4 flex items-center justify-between"
            >
              <div>
                <div className="text-sm text-paper-100">{p.name}</div>
                <div className="text-[11px] text-mist-300 mt-0.5">
                  last active {formatDate(p.lastActive)}
                </div>
              </div>
              <div className="text-sm font-[family-name:var(--font-mono)] text-glow-400">
                {p.memoryCount}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
