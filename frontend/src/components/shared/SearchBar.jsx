import { Search } from "lucide-react";
import { cn } from "../../utils/cn";

function SearchBar({ value, onChange, placeholder = "Search...", className = "" }) {
  return (
    <label className={cn("relative block w-full", className)}>
      <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-text-faint" />
      <input
        type="search"
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        className="input-base pl-10"
      />
    </label>
  );
}

export default SearchBar;
