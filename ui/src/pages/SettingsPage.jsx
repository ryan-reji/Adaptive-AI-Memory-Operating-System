import { useEffect, useState } from "react";
import {
  getPermissionMode, setPermissionMode,
  getAllowedFolders, addAllowedFolder, removeAllowedFolder,
  getExclusions, addExclusion, removeExclusion,
} from "../lib/api";
import { useToast } from "../components/Toast";
import ErrorState from "../components/ErrorState";
import { X, Plus } from "lucide-react";

const MODE_OPTIONS = [
  { value: "allow_all", label: "Allow all", desc: "Capture everything except explicit exclusions" },
  { value: "allow_only", label: "Allow only", desc: "Only capture from folders you explicitly allow" },
];

export default function SettingsPage() {
  const [mode, setMode] = useState(null);
  const [allowedFolders, setAllowedFolders] = useState([]);
  const [exclusions, setExclusions] = useState([]);
  const [newFolder, setNewFolder] = useState("");
  const [newExclusion, setNewExclusion] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const showToast = useToast();

  function load() {
    setLoading(true);
    setError(null);
    Promise.all([getPermissionMode(), getAllowedFolders(), getExclusions()])
      .then(([modeRes, folders, excl]) => {
        setMode(modeRes.mode);
        setAllowedFolders(folders);
        setExclusions(excl);
        setLoading(false);
      })
      .catch(() => {
        setError("Can't reach the backend right now.");
        setLoading(false);
      });
  }

  useEffect(load, []);

  async function handleModeChange(newMode) {
    try {
      await setPermissionMode(newMode);
      setMode(newMode);
      showToast("Permission mode updated");
    } catch {
      showToast("Couldn't update — backend unreachable");
    }
  }

  async function handleAddFolder() {
    if (!newFolder.trim()) return;
    try {
      await addAllowedFolder(newFolder.trim());
      setNewFolder("");
      const updated = await getAllowedFolders();
      setAllowedFolders(updated);
      showToast("Folder added");
    } catch {
      showToast("Couldn't add folder — backend unreachable");
    }
  }

  async function handleRemoveFolder(path) {
    try {
      await removeAllowedFolder(path);
      const updated = await getAllowedFolders();
      setAllowedFolders(updated);
      showToast("Folder removed");
    } catch {
      showToast("Couldn't remove folder — backend unreachable");
    }
  }

  async function handleAddExclusion() {
    if (!newExclusion.trim()) return;
    try {
      await addExclusion(newExclusion.trim());
      setNewExclusion("");
      const updated = await getExclusions();
      setExclusions(updated);
      showToast("Exclusion added");
    } catch {
      showToast("Couldn't add exclusion — backend unreachable");
    }
  }

  async function handleRemoveExclusion(path) {
    try {
      await removeExclusion(path);
      const updated = await getExclusions();
      setExclusions(updated);
      showToast("Exclusion removed");
    } catch {
      showToast("Couldn't remove exclusion — backend unreachable");
    }
  }

  if (loading) return <div className="p-8 text-sm text-mist-300">Loading settings…</div>;
  if (error) {
    return (
      <div className="p-8 max-w-2xl mx-auto">
        <ErrorState message={error} onRetry={load} />
      </div>
    );
  }

  return (
    <div className="p-8 max-w-2xl mx-auto space-y-8">
      <div>
        <h2 className="font-[family-name:var(--font-display)] text-2xl text-paper-100">Privacy & Settings</h2>
        <p className="text-sm text-mist-300 mt-1">Nothing here leaves your device.</p>
      </div>

      <section>
        <h3 className="text-sm font-medium text-mist-200 mb-3">Capture mode</h3>
        <div className="grid grid-cols-2 gap-3">
          {MODE_OPTIONS.map((opt) => (
            <button
              key={opt.value}
              onClick={() => handleModeChange(opt.value)}
              className={`text-left p-3.5 rounded-lg border transition-colors ${
                mode === opt.value ? "border-glow-500 bg-ink-800" : "border-ink-700 bg-ink-900 hover:border-ink-600"
              }`}
            >
              <div className="text-sm text-paper-100">{opt.label}</div>
              <div className="text-[11px] text-mist-300 mt-1">{opt.desc}</div>
            </button>
          ))}
        </div>
      </section>

      <section>
        <h3 className="text-sm font-medium text-mist-200 mb-3">
          Allowed folders {mode === "allow_all" && <span className="text-mist-300 font-normal">(used in Allow-only mode)</span>}
        </h3>
        <div className="bg-ink-900 border border-ink-700 rounded-lg divide-y divide-ink-700">
          {allowedFolders.length === 0 ? (
            <div className="px-5 py-4 text-sm text-mist-300">No folders added yet.</div>
          ) : (
            allowedFolders.map((f) => (
              <div key={f.path} className="flex items-center justify-between px-5 py-3">
                <span className="text-sm text-mist-200 font-[family-name:var(--font-mono)]">{f.path}</span>
                <button onClick={() => handleRemoveFolder(f.path)} className="text-mist-300 hover:text-fade-500">
                  <X size={14} />
                </button>
              </div>
            ))
          )}
        </div>
        <div className="flex gap-2 mt-3">
          <input
            value={newFolder}
            onChange={(e) => setNewFolder(e.target.value)}
            placeholder="C:\Users\you\Documents\project"
            className="flex-1 bg-ink-900 border border-ink-700 focus:border-glow-500 rounded-lg px-3 py-2 text-sm text-mist-200 outline-none"
          />
          <button onClick={handleAddFolder} className="px-3 py-2 bg-ink-800 border border-ink-700 rounded-lg text-mist-200 hover:border-glow-500">
            <Plus size={14} />
          </button>
        </div>
      </section>

      <section>
        <h3 className="text-sm font-medium text-mist-200 mb-3">Exclusions</h3>
        <div className="bg-ink-900 border border-ink-700 rounded-lg divide-y divide-ink-700">
          {exclusions.length === 0 ? (
            <div className="px-5 py-4 text-sm text-mist-300">No exclusions set.</div>
          ) : (
            exclusions.map((f) => (
              <div key={f.path} className="flex items-center justify-between px-5 py-3">
                <span className="text-sm text-mist-200 font-[family-name:var(--font-mono)]">{f.path}</span>
                <button onClick={() => handleRemoveExclusion(f.path)} className="text-mist-300 hover:text-fade-500">
                  <X size={14} />
                </button>
              </div>
            ))
          )}
        </div>
        <div className="flex gap-2 mt-3">
          <input
            value={newExclusion}
            onChange={(e) => setNewExclusion(e.target.value)}
            placeholder="C:\Users\you\Downloads"
            className="flex-1 bg-ink-900 border border-ink-700 focus:border-glow-500 rounded-lg px-3 py-2 text-sm text-mist-200 outline-none"
          />
          <button onClick={handleAddExclusion} className="px-3 py-2 bg-ink-800 border border-ink-700 rounded-lg text-mist-200 hover:border-glow-500">
            <Plus size={14} />
          </button>
        </div>
      </section>
    </div>
  );
}