// src/components/ErrorState.jsx
import { AlertCircle, RotateCw } from "lucide-react";

export default function ErrorState({ message, onRetry }) {
  return (
    <div className="border border-dashed border-ink-700 rounded-lg py-10 px-6 text-center space-y-3">
      <AlertCircle size={20} className="mx-auto text-fade-500" />
      <p className="text-sm text-mist-300">{message || "Can't reach the backend right now."}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="inline-flex items-center gap-1.5 text-[11px] text-glow-400 hover:text-glow-300"
        >
          <RotateCw size={12} /> Try again
        </button>
      )}
    </div>
  );
}