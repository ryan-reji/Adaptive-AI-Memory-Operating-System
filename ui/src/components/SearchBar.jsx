import { forwardRef } from "react";
import { Search, Loader2 } from "lucide-react";

const SearchBar = forwardRef(function SearchBar(
  { value, onChange, onSubmit, loading, placeholder },
  ref
) {
  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        onSubmit();
      }}
      className="relative"
    >
      <Search
        size={16}
        strokeWidth={1.75}
        className="absolute left-3.5 top-1/2 -translate-y-1/2 text-mist-300"
      />
      <input
        ref={ref}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder || "Ask about anything you've worked on…"}
        className="w-full bg-ink-900 border border-ink-700 focus:border-glow-500 rounded-lg pl-10 pr-10 py-3 text-sm text-mist-200 placeholder:text-mist-300/70 outline-none transition-colors"
      />
      {loading && (
        <Loader2
          size={16}
          className="absolute right-3.5 top-1/2 -translate-y-1/2 text-glow-400 animate-spin"
        />
      )}
    </form>
  );
});

export default SearchBar;