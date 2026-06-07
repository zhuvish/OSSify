"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { MessageCircle, X, Search, Sparkles, Loader2, AlertCircle, User } from "lucide-react";
import { searchExperts } from "@/src/lib/api";

const SUGGESTED_QUERIES = [
  "frontend",
  "backend",
  "database",
  "testing",
  "documentation",
  "devops",
];

type Expert = {
  contributor_id: number;
  username: string;
  score: number;
  expertise: string;
  confidence: number;
  matched_documents: number;
  expertise_areas: { domain: string; score: number }[];
};

type SearchResult = {
  query: string;
  experts: Expert[];
  count: number;
};

export default function AskAI() {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [result, setResult] = useState<SearchResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const panelRef = useRef<HTMLDivElement>(null);
  const router = useRouter();

  const doSearch = useCallback(async (q: string) => {
    if (!q.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await searchExperts(q.trim());
      setResult(data);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Something went wrong. Please try again."
      );
    } finally {
      setLoading(false);
    }
  }, []);

  const handleSuggestion = (suggestion: string) => {
    setQuery(suggestion);
    doSearch(suggestion);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) doSearch(query);
  };

  // Focus input when panel opens
  useEffect(() => {
    if (open) {
      setTimeout(() => inputRef.current?.focus(), 100);
    } else {
      // Reset state when closing
      setQuery("");
      setResult(null);
      setError(null);
    }
  }, [open]);

  // Close on Escape
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape" && open) {
        setOpen(false);
      }
    };
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [open]);

  // Close on click outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (
        open &&
        panelRef.current &&
        !panelRef.current.contains(e.target as Node) &&
        !(e.target as Element)?.closest('[data-ask-ai-toggle]')
      ) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [open]);

  return (
    <>
      {/* Floating button */}
      <div className="fixed bottom-6 right-6 z-50">
        <button
          type="button"
          data-ask-ai-toggle
          onClick={() => setOpen(!open)}
          className="inline-flex items-center gap-2 rounded-full bg-violet-600 px-5 py-3 text-white shadow-2xl shadow-violet-500/25 transition hover:bg-violet-700 active:scale-95"
        >
          {open ? <X size={18} /> : <MessageCircle size={18} />}
          {open ? "Close" : "Ask AI"}
        </button>
      </div>

      {/* Popup panel */}
      {open && (
        <div className="fixed bottom-24 right-6 z-50 w-[420px] max-h-[600px] bg-white rounded-2xl border border-slate-200 shadow-2xl shadow-slate-900/10 flex flex-col overflow-hidden animate-in fade-in slide-in-from-bottom-4 duration-200">
          {/* Header */}
          <div className="flex items-center gap-3 px-5 py-4 border-b border-slate-100 bg-gradient-to-r from-violet-50 to-indigo-50">
            <div className="h-9 w-9 rounded-full bg-violet-600 flex items-center justify-center">
              <Sparkles size={16} className="text-white" />
            </div>
            <div>
              <h3 className="font-semibold text-slate-900 text-sm">Expert Discovery</h3>
              <p className="text-xs text-slate-500">Search for experts by topic</p>
            </div>
          </div>

          {/* Search form */}
          <div className="px-5 pt-4 pb-2">
            <form onSubmit={handleSubmit} className="relative">
              <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                ref={inputRef}
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search experts..."
                className="w-full rounded-xl border border-slate-200 bg-slate-50 py-2.5 pl-10 pr-10 text-sm outline-none focus:border-violet-400 focus:bg-white focus:ring-2 focus:ring-violet-100 transition"
              />
              {query && (
                <button
                  type="button"
                  onClick={() => {
                    setQuery("");
                    setResult(null);
                    setError(null);
                  }}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                >
                  <X size={14} />
                </button>
              )}
            </form>
          </div>

          {/* Suggested queries */}
          {!result && !loading && !error && (
            <div className="px-5 py-2">
              <p className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-2">Suggestions</p>
              <div className="flex flex-wrap gap-2">
                {SUGGESTED_QUERIES.map((s) => (
                  <button
                    key={s}
                    onClick={() => handleSuggestion(s)}
                    className="px-3 py-1.5 rounded-lg bg-slate-100 text-slate-600 text-xs font-medium hover:bg-violet-100 hover:text-violet-700 hover:border-violet-200 border border-slate-200 transition"
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Content area */}
          <div className="flex-1 overflow-y-auto px-5 pb-4 pt-2">
            {/* Loading state */}
            {loading && (
              <div className="flex flex-col items-center justify-center py-10 gap-3">
                <Loader2 size={28} className="text-violet-500 animate-spin" />
                <p className="text-sm text-slate-500">Searching experts...</p>
              </div>
            )}

            {/* Error state */}
            {error && !loading && (
              <div className="flex flex-col items-center justify-center py-10 gap-3">
                <div className="h-12 w-12 rounded-full bg-red-50 flex items-center justify-center">
                  <AlertCircle size={24} className="text-red-500" />
                </div>
                <p className="text-sm text-red-600 text-center">{error}</p>
                <button
                  onClick={() => query && doSearch(query)}
                  className="text-xs text-violet-600 hover:text-violet-700 underline"
                >
                  Try again
                </button>
              </div>
            )}

            {/* Empty state */}
            {result && result.experts.length === 0 && !loading && (
              <div className="flex flex-col items-center justify-center py-10 gap-3">
                <div className="h-12 w-12 rounded-full bg-slate-100 flex items-center justify-center">
                  <Search size={24} className="text-slate-400" />
                </div>
                <p className="text-sm font-medium text-slate-700">No experts found</p>
                <p className="text-xs text-slate-500 text-center">
                  No experts matching "{result.query}" were found. Try a different search term.
                </p>
              </div>
            )}

            {/* Results */}
            {result && result.experts.length > 0 && !loading && (
              <div className="space-y-3">
                <p className="text-xs text-slate-400">
                  Found {result.count} expert{result.count !== 1 ? "s" : ""} for "{result.query}"
                </p>
                {result.experts.map((expert, idx) => (
                  <button
                    key={expert.contributor_id}
                    onClick={() => {
                      router.push(`/contributors/${expert.contributor_id}`);
                      setOpen(false);
                    }}
                    className="w-full text-left bg-white rounded-xl border border-slate-200 p-4 hover:border-violet-300 hover:shadow-md hover:shadow-violet-100/50 transition-all group"
                  >
                    {/* Top expert badge */}
                    {idx === 0 && (
                      <div className="flex items-center gap-1.5 mb-2">
                        <Sparkles size={12} className="text-amber-500" />
                        <span className="text-[11px] font-semibold text-amber-600 uppercase tracking-wider">Top Expert</span>
                      </div>
                    )}

                    {/* Username and primary expertise */}
                    <div className="flex items-center gap-3">
                      <div className="h-10 w-10 rounded-full bg-indigo-100 text-indigo-700 flex items-center justify-center font-bold text-sm shrink-0">
                        {expert.username ? expert.username[0].toUpperCase() : <User size={16} />}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-semibold text-slate-900 text-sm group-hover:text-violet-700 transition-colors">
                          {expert.username}
                        </p>
                        <p className="text-xs text-slate-500 capitalize">
                          {expert.expertise} Expert
                        </p>
                      </div>
                      <div className="text-right shrink-0">
                        <p className="text-xs font-medium text-slate-900">
                          {Math.round(expert.confidence * 100)}%
                        </p>
                        <p className="text-[10px] text-slate-400">Confidence</p>
                      </div>
                    </div>

                    {/* Matched documents */}
                    <div className="mt-2 flex items-center gap-1.5">
                      <div className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
                      <span className="text-[11px] text-slate-500">
                        {expert.matched_documents} document{expert.matched_documents !== 1 ? "s" : ""} matched
                      </span>
                    </div>

                    {/* Expertise domains */}
                    {expert.expertise_areas && expert.expertise_areas.length > 0 && (
                      <div className="mt-2.5 pt-2.5 border-t border-slate-100">
                        <div className="flex flex-wrap gap-x-3 gap-y-1">
                          {expert.expertise_areas.slice(0, 3).map((area) => (
                            <div key={area.domain} className="flex items-center gap-1.5">
                              <span className="text-xs text-slate-600 capitalize">{area.domain}</span>
                              <span className="text-[10px] font-medium text-violet-600">
                                {area.score.toFixed(1)}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </button>
                ))}
              </div>
            )}

            {/* Initial state - no search yet */}
            {!result && !loading && !error && (
              <div className="flex flex-col items-center justify-center py-8 gap-2">
                <div className="h-10 w-10 rounded-full bg-violet-50 flex items-center justify-center">
                  <Sparkles size={20} className="text-violet-500" />
                </div>
                <p className="text-sm text-slate-500 text-center">
                  Search for experts by topic or choose a suggestion above.
                </p>
              </div>
            )}
          </div>
        </div>
      )}
    </>
  );
}