import { NavLink } from "react-router-dom";
import { LayoutDashboard, Search, Clock3, Settings, Circle } from "lucide-react";
import { isMockMode } from "../lib/api";

const items = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard, end: true },
  { to: "/search", label: "Search", icon: Search },
  { to: "/timeline", label: "Timeline", icon: Clock3 },
  { to: "/settings", label: "Privacy & Settings", icon: Settings },
];

export default function Sidebar() {
  return (
    <aside className="w-56 shrink-0 h-full bg-ink-900 border-r border-ink-700 flex flex-col">
      <div className="px-5 pt-6 pb-5">
        <h1 className="font-[family-name:var(--font-display)] text-lg text-paper-100 tracking-wide">
          Recall
        </h1>
        <p className="text-[11px] text-mist-300 mt-0.5">your memory, kept local</p>
      </div>

      <nav className="flex-1 px-3 space-y-1">
        {items.map(({ to, label, icon: Icon, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) =>
              `flex items-center gap-2.5 px-3 py-2 rounded-md text-sm transition-colors ${
                isActive
                  ? "bg-ink-700 text-glow-300"
                  : "text-mist-300 hover:bg-ink-800 hover:text-mist-200"
              }`
            }
          >
            <Icon size={16} strokeWidth={1.75} />
            {label}
          </NavLink>
        ))}
      </nav>

      <div className="px-5 py-4 border-t border-ink-700 flex items-center gap-2 text-[11px] text-mist-300">
        <Circle
          size={7}
          className={isMockMode ? "fill-glow-500 text-glow-500" : "fill-kept-500 text-kept-500"}
        />
        {isMockMode ? "Demo mode — mock data" : "Connected to local engine"}
      </div>
    </aside>
  );
}
