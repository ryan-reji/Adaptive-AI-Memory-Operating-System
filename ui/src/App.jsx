import { HashRouter, Routes, Route, useNavigate } from "react-router-dom";
import { useEffect } from "react";
import Sidebar from "./components/Sidebar";
import Dashboard from "./pages/Dashboard";
import SearchPage from "./pages/SearchPage";
import TimelinePage from "./pages/TimelinePage";
import SettingsPage from "./pages/SettingsPage";
import { ToastProvider } from "./components/Toast";
import ContourBackground from "./components/ContourBackground";

function GlobalShortcuts() {
  const navigate = useNavigate();
  useEffect(() => {
    function handleKeyDown(e) {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        navigate("/search");
      }
    }
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [navigate]);
  return null;
}

export default function App() {
  return (
    <ToastProvider>
      <HashRouter>
        <ContourBackground />
        <GlobalShortcuts />
        <div className="flex h-screen overflow-hidden">
          <Sidebar />
          <main className="flex-1 overflow-y-auto">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/search" element={<SearchPage />} />
              <Route path="/timeline" element={<TimelinePage />} />
              <Route path="/settings" element={<SettingsPage />} />
            </Routes>
          </main>
        </div>
      </HashRouter>
    </ToastProvider>
  );
}