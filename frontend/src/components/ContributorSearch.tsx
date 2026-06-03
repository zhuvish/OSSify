"use client";

import { useEffect, useState, useRef } from "react";
import { searchContributors } from "@/src/lib/contributors";

type Contributor = {
  id: number;
  username: string;
  display_name?: string;
  avatar_url?: string;
  expertise_score?: number;
};

export default function ContributorSearch({
  value,
  onChange,
  onSelect,
}: {
  value: string;
  onChange: (v: string) => void;
  onSelect: (c: Contributor) => void;
}) {
  const [suggestions, setSuggestions] = useState<Contributor[]>([]);
  const [loading, setLoading] = useState(false);
  const containerRef = useRef<HTMLDivElement | null>(null);

  const [activeIndex, setActiveIndex] = useState<number>(-1);

  useEffect(() => {
    let mounted = true;
    if (!value || value.length < 2) {
      setSuggestions([]);
      setActiveIndex(-1);
      return;
    }

    setLoading(true);
    const t = setTimeout(async () => {
      try {
        const res = await searchContributors(value);
        if (!mounted) return;
        setSuggestions(res || []);
        setActiveIndex(res && res.length ? 0 : -1);
      } catch (e) {
        setSuggestions([]);
        setActiveIndex(-1);
      } finally {
        if (mounted) setLoading(false);
      }
    }, 250);

    return () => {
      mounted = false;
      clearTimeout(t);
    };
  }, [value]);

  const onKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (!suggestions || suggestions.length === 0) return;

    if (e.key === "ArrowDown") {
      e.preventDefault();
      setActiveIndex((prev) => {
        const next = prev + 1;
        return next >= suggestions.length ? 0 : next;
      });
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setActiveIndex((prev) => {
        const next = prev - 1;
        return next < 0 ? suggestions.length - 1 : next;
      });
    } else if (e.key === "Enter") {
      e.preventDefault();
      if (activeIndex >= 0 && activeIndex < suggestions.length) {
        const sel = suggestions[activeIndex];
        onSelect(sel);
        setSuggestions([]);
        setActiveIndex(-1);
      }
    } else if (e.key === "Escape") {
      setSuggestions([]);
      setActiveIndex(-1);
    }
  };

  return (
    <div className="relative" ref={containerRef}>
      <input
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={onKeyDown}
        placeholder="Search contributors..."
        aria-autocomplete="list"
        aria-expanded={suggestions.length > 0}
        className="w-80 rounded-xl border border-slate-300 bg-white px-4 py-3 outline-none"
      />

      {suggestions.length > 0 && (
        <div role="listbox" className="absolute left-0 mt-2 w-80 bg-white border border-slate-200 rounded-xl shadow-lg z-40">
          {suggestions.map((s, idx) => (
            <button
              key={s.id}
              onMouseEnter={() => setActiveIndex(idx)}
              onMouseLeave={() => setActiveIndex(-1)}
              onClick={() => {
                onSelect(s);
                setSuggestions([]);
                setActiveIndex(-1);
              }}
              aria-selected={activeIndex === idx}
              role="option"
              className={`w-full text-left px-4 py-3 flex items-center gap-3 ${activeIndex === idx ? 'bg-slate-100' : 'hover:bg-slate-50'}`}
            >
              <div className="h-8 w-8 rounded-full bg-indigo-100 text-indigo-700 flex items-center justify-center font-semibold">
                {s.username ? s.username[0].toUpperCase() : "U"}
              </div>
              <div className="flex-1">
                <div className="text-sm font-medium text-slate-900">{s.username}</div>
                <div className="text-xs text-slate-500">{s.display_name || ''}</div>
              </div>
              <div className="text-xs text-slate-400">{Math.round((s.expertise_score||0)*10)/10}</div>
            </button>
          ))}
        </div>
      )}

      {loading && (
        <div className="absolute right-3 top-3 text-xs text-slate-400">Searching...</div>
      )}
    </div>
  );
}
