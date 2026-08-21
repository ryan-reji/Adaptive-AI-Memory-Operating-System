import { createContext, useCallback, useContext, useState } from "react";
import { Check } from "lucide-react";

const ToastContext = createContext(null);

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);

  const showToast = useCallback((message) => {
    const id = Date.now();
    setToasts((prev) => [...prev, { id, message }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 2200);
  }, []);

  return (
    <ToastContext.Provider value={showToast}>
      {children}
      <div className="fixed bottom-5 right-5 space-y-2 z-50">
        {toasts.map((t) => (
          <div
            key={t.id}
            className="flex items-center gap-2 bg-ink-800 border border-ink-600 text-mist-200 text-sm px-4 py-2.5 rounded-lg shadow-lg"
          >
            <Check size={14} className="text-kept-500" />
            {t.message}
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error("useToast must be used within ToastProvider");
  return ctx;
}