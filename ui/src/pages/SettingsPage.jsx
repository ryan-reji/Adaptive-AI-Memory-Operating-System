import { useEffect, useState } from "react";
import { getSettings, updateSettings } from "../lib/api";
import { useToast } from "../components/Toast";

function Toggle({ checked, onChange }) {
  return (
    <button
      role="switch"
      aria-checked={checked}
      onClick={() => onChange(!checked)}
      className={`w-10 h-5.5 rounded-full relative transition-colors shrink-0 ${
        checked ? "bg-glow-500" : "bg-ink-700"
      }`}
    >
      <span
        className={`absolute top-0.5 left-0.5 w-4 h-4 rounded-full bg-ink-950 transition-transform ${
          checked ? "translate-x-4.5" : ""
        }`}
      />
    </button>
  );
}

const sourceLabels = {
  browser: "Browser history",
  files: "Files & documents",
  vscode: "VS Code / IDE activity",
  email: "Email",
};

const policyOptions = [
  { value: "aggressive", label: "Aggressive", desc: "Forget low-relevance memories quickly" },
  { value: "balanced", label: "Balanced", desc: "Keep important memories, summarize the rest" },
  { value: "retain-all", label: "Retain all", desc: "Never automatically forget anything" },
];

export default function SettingsPage() {
  const [settings, setSettings] = useState(null);
  const [saving, setSaving] = useState(false);
  const showToast = useToast();

  useEffect(() => {
    getSettings().then(setSettings);
  }, []);

  async function save(partial) {
    setSaving(true);
    const updated = await updateSettings({ ...settings, ...partial });
    setSettings(updated);
    setSaving(false);
    showToast("Settings saved");
  }

  if (!settings) {
    return <div className="p-8 text-sm text-mist-300">Loading settings…</div>;
  }

  return (
    <div className="p-8 max-w-2xl mx-auto space-y-8">
      <div>
        <h2 className="font-[family-name:var(--font-display)] text-2xl text-paper-100">
          Privacy & Settings
        </h2>
        <p className="text-sm text-mist-300 mt-1">
          Nothing here leaves your device. Turn any source off and it stops being captured
          immediately — past memories from it stay until you delete them.
        </p>
      </div>

      <section className="bg-ink-900 border border-ink-700 rounded-lg p-5 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <div className="text-sm text-paper-100">Capture activity</div>
            <div className="text-[11px] text-mist-300 mt-0.5">
              Master switch for all monitoring
            </div>
          </div>
          <Toggle
            checked={settings.captureEnabled}
            onChange={(v) => save({ captureEnabled: v })}
          />
        </div>
      </section>

      <section>
        <h3 className="text-sm font-medium text-mist-200 mb-3">Sources</h3>
        <div className="bg-ink-900 border border-ink-700 rounded-lg divide-y divide-ink-700">
          {Object.entries(settings.sources).map(([key, val]) => (
            <div key={key} className="flex items-center justify-between px-5 py-3.5">
              <span className="text-sm text-mist-200">{sourceLabels[key] || key}</span>
              <Toggle
                checked={val}
                onChange={(v) => save({ sources: { ...settings.sources, [key]: v } })}
              />
            </div>
          ))}
        </div>
      </section>

      <section>
        <h3 className="text-sm font-medium text-mist-200 mb-3">Forgetting policy</h3>
        <div className="grid grid-cols-3 gap-3">
          {policyOptions.map((opt) => (
            <button
              key={opt.value}
              onClick={() => save({ forgettingPolicy: opt.value })}
              className={`text-left p-3.5 rounded-lg border transition-colors ${
                settings.forgettingPolicy === opt.value
                  ? "border-glow-500 bg-ink-800"
                  : "border-ink-700 bg-ink-900 hover:border-ink-600"
              }`}
            >
              <div className="text-sm text-paper-100">{opt.label}</div>
              <div className="text-[11px] text-mist-300 mt-1">{opt.desc}</div>
            </button>
          ))}
        </div>
      </section>

      <section className="bg-ink-900 border border-ink-700 rounded-lg p-5">
        <div className="flex items-center justify-between">
          <div>
            <div className="text-sm text-paper-100">Filter sensitive data</div>
            <div className="text-[11px] text-mist-300 mt-0.5">
              Strip passwords, card numbers, and similar patterns before storage
            </div>
          </div>
          <Toggle
            checked={settings.sensitiveDataFilter}
            onChange={(v) => save({ sensitiveDataFilter: v })}
          />
        </div>
      </section>

      {saving && <div className="text-[11px] text-glow-400">Saving…</div>}
    </div>
  );
}