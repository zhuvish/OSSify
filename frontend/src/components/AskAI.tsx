"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import {
  MessageCircle, X, Search, Sparkles, Loader2, AlertCircle, User,
  MessageSquareText, Send, Lightbulb, Info, CheckCircle2, HelpCircle,
} from "lucide-react";
import { searchExperts, askExperts } from "@/src/lib/api";

const SUGGESTED_QUERIES = [
  "frontend",
  "backend",
  "database",
  "testing",
  "documentation",
  "devops",
];

const SUGGESTED_QUESTIONS = [
  "Who is the expert in frontend?",
  "Who should review backend APIs?",
  "Who owns the database layer?",
  "Who works most on documentation?",
  "Who should review testing changes?",
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

type AskResult = {
  summary: string;
  relevant_information: string[];
  answer: string;
};

type Tab = "discovery" | "ask";

export default function AskAI() {
  const [open, setOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<Tab>("discovery");
  const [query, setQuery] = useState("");
  const [result, setResult] = useState<SearchResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const panelRef = useRef<HTMLDivElement>(null);
  const router = useRouter();

  // Ask Question state
  const [question, setQuestion] = useState("");
  const [askResult, setAskResult] = useState<AskResult | null>(null);
  const [askLoading, setAskLoading] = useState(false);
  const [askError, setAskError] = useState<string | null>(null);

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

  const handleAskSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;
    setAskLoading(true);
    setAskError(null);
    setAskResult(null);
    try {
      const data = await askExperts(question.trim());
      setAskResult(data);
    } catch (err) {
      setAskError(
        err instanceof Error ? err.message : "Something went wrong. Please try again."
      );
    } finally {
      setAskLoading(false);
    }
  };

  const handleAskSuggestion = (suggestion: string) => {
    setQuestion(suggestion);
    // Auto-submit after short delay to allow state to update
    setTimeout(() => {
      setAskLoading(true);
      setAskError(null);
      setAskResult(null);
      askExperts(suggestion).then((data) => {
        setAskResult(data);
      }).catch((err) => {
        setAskError(err instanceof Error ? err.message : "Something went wrong.");
      }).finally(() => {
        setAskLoading(false);
      });
    }, 50);
  };

  // Focus input when panel opens
  const prevOpen = useRef(open);
  useEffect(() => {
    if (open && !prevOpen.current) {
      setTimeout(() => {
        if (activeTab === "discovery") inputRef.current?.focus();
        else textareaRef.current?.focus();
      }, 100);
    } else if (!open && prevOpen.current) {
      // Reset all state when closing
      setQuery("");
      setResult(null);
      setError(null);
      setQuestion("");
      setAskResult(null);
      setAskError(null);
      setActiveTab("discovery");
    }
    prevOpen.current = open;
  }, [open, activeTab]);

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
          className="h-14 w-14 rounded-full bg-violet-600 text-white shadow-2xl shadow-violet-500/30 flex items-center justify-center transition hover:bg-violet-700 hover:shadow-violet-500/40 hover:scale-105 active:scale-95"
        >
          {open ? <X size={22} /> : (
            <div className="relative">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="22"
                height="22"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
              </svg>
              <Sparkles
                size={10}
                className="absolute -top-0.5 -right-0.5 text-amber-300"
                strokeWidth={2.5}
              />
            </div>
          )}
        </button>
      </div>

      {/* Popup panel */}
      {open && (
        <div
          ref={panelRef}
          className="fixed bottom-24 right-6 z-50 w-[460px] max-h-[640px] bg-white rounded-2xl border border-slate-200 shadow-2xl shadow-slate-900/10 flex flex-col overflow-hidden animate-in fade-in slide-in-from-bottom-4 duration-200"
        >
          {/* Tab bar */}
          <div className="flex border-b border-slate-100 bg-slate-50/50">
            <button
              onClick={() => { setActiveTab("discovery"); setAskResult(null); setAskError(null); }}
              className={`flex-1 flex items-center justify-center gap-2 py-3 text-sm font-medium transition ${
                activeTab === "discovery"
                  ? "text-violet-700 bg-white border-b-2 border-violet-600"
                  : "text-slate-500 hover:text-slate-700"
              }`}
            >
              <Search size={15} />
              Expert Discovery
            </button>
            <button
              onClick={() => { setActiveTab("ask"); setResult(null); setError(null); }}
              className={`flex-1 flex items-center justify-center gap-2 py-3 text-sm font-medium transition ${
                activeTab === "ask"
                  ? "text-violet-700 bg-white border-b-2 border-violet-600"
                  : "text-slate-500 hover:text-slate-700"
              }`}
            >
              <MessageSquareText size={15} />
              Ask Question
            </button>
          </div>

          {/* ─── TAB 1: Expert Discovery ─── */}
          {activeTab === "discovery" && (
            <>
              {/* Header */}
              <div className="flex items-center gap-3 px-5 py-3 border-b border-slate-100 bg-gradient-to-r from-violet-50 to-indigo-50">
                <div className="h-8 w-8 rounded-full bg-violet-600 flex items-center justify-center">
                  <Sparkles size={14} className="text-white" />
                </div>
                <div>
                  <h3 className="font-semibold text-slate-900 text-sm">Expert Discovery</h3>
                  <p className="text-xs text-slate-500">Search for experts by topic</p>
                </div>
              </div>

              {/* Search form */}
              <div className="px-5 pt-3 pb-1">
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
                      onClick={() => { setQuery(""); setResult(null); setError(null); }}
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
                    <button onClick={() => query && doSearch(query)} className="text-xs text-violet-600 hover:text-violet-700 underline">
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
                        onClick={() => { router.push(`/contributors/${expert.contributor_id}`); setOpen(false); }}
                        className="w-full text-left bg-white rounded-xl border border-slate-200 p-4 hover:border-violet-300 hover:shadow-md hover:shadow-violet-100/50 transition-all group"
                      >
                        {idx === 0 && (
                          <div className="flex items-center gap-1.5 mb-2">
                            <Sparkles size={12} className="text-amber-500" />
                            <span className="text-[11px] font-semibold text-amber-600 uppercase tracking-wider">Top Expert</span>
                          </div>
                        )}
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
                        <div className="mt-2 flex items-center gap-1.5">
                          <div className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
                          <span className="text-[11px] text-slate-500">
                            {expert.matched_documents} document{expert.matched_documents !== 1 ? "s" : ""} matched
                          </span>
                        </div>
                        {expert.expertise_areas && expert.expertise_areas.length > 0 && (
                          <div className="mt-2.5 pt-2.5 border-t border-slate-100">
                            <div className="flex flex-wrap gap-x-3 gap-y-1">
                              {expert.expertise_areas.slice(0, 3).map((area) => (
                                <div key={area.domain} className="flex items-center gap-1.5">
                                  <span className="text-xs text-slate-600 capitalize">{area.domain}</span>
                                  <span className="text-[10px] font-medium text-violet-600">{area.score.toFixed(1)}</span>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </button>
                    ))}
                  </div>
                )}

                {/* Initial state */}
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
            </>
          )}

          {/* ─── TAB 2: Ask Question ─── */}
          {activeTab === "ask" && (
            <>
              {/* Header */}
              <div className="flex items-center gap-3 px-5 py-3 border-b border-slate-100 bg-gradient-to-r from-violet-50 to-indigo-50">
                <div className="h-8 w-8 rounded-full bg-indigo-600 flex items-center justify-center">
                  <HelpCircle size={14} className="text-white" />
                </div>
                <div>
                  <h3 className="font-semibold text-slate-900 text-sm">Ask a Question</h3>
                  <p className="text-xs text-slate-500">Natural language questions about contributors</p>
                </div>
              </div>

              {/* Question form */}
              <div className="px-5 pt-3 pb-1">
                <form onSubmit={handleAskSubmit} className="space-y-2">
                  <textarea
                    ref={textareaRef}
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    placeholder="e.g. Who is the expert in backend APIs?"
                    rows={2}
                    className="w-full rounded-xl border border-slate-200 bg-slate-50 p-3 text-sm outline-none resize-none focus:border-violet-400 focus:bg-white focus:ring-2 focus:ring-violet-100 transition"
                  />
                  <div className="flex justify-end">
                    <button
                      type="submit"
                      disabled={!question.trim() || askLoading}
                      className="inline-flex items-center gap-2 rounded-lg bg-violet-600 px-4 py-2 text-sm font-medium text-white hover:bg-violet-700 disabled:opacity-50 disabled:cursor-not-allowed transition active:scale-95"
                    >
                      {askLoading ? (
                        <Loader2 size={14} className="animate-spin" />
                      ) : (
                        <Send size={14} />
                      )}
                      Ask
                    </button>
                  </div>
                </form>
              </div>

              {/* Suggested questions */}
              {!askResult && !askLoading && !askError && (
                <div className="px-5 py-2">
                  <p className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-2">Suggested Questions</p>
                  <div className="flex flex-wrap gap-2">
                    {SUGGESTED_QUESTIONS.map((sq) => (
                      <button
                        key={sq}
                        onClick={() => handleAskSuggestion(sq)}
                        className="px-3 py-1.5 rounded-lg bg-slate-100 text-slate-600 text-xs font-medium hover:bg-indigo-100 hover:text-indigo-700 hover:border-indigo-200 border border-slate-200 transition text-left"
                      >
                        {sq}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Content area */}
              <div className="flex-1 overflow-y-auto px-5 pb-4 pt-2">
                {/* Loading */}
                {askLoading && (
                  <div className="flex flex-col items-center justify-center py-10 gap-3">
                    <Loader2 size={28} className="text-indigo-500 animate-spin" />
                    <p className="text-sm text-slate-500">Analyzing experts...</p>
                  </div>
                )}

                {/* Error */}
                {askError && !askLoading && (
                  <div className="flex flex-col items-center justify-center py-10 gap-3">
                    <div className="h-12 w-12 rounded-full bg-red-50 flex items-center justify-center">
                      <AlertCircle size={24} className="text-red-500" />
                    </div>
                    <p className="text-sm text-red-600 text-center">{askError}</p>
                    <button onClick={() => question && handleAskSubmit} className="text-xs text-violet-600 hover:text-violet-700 underline">
                      Try again
                    </button>
                  </div>
                )}

                {/* Results */}
                {askResult && !askLoading && (
                  <div className="space-y-4">
                    {/* Summary */}
                    <div className="bg-gradient-to-br from-violet-50 to-indigo-50 rounded-xl border border-violet-100 p-4">
                      <div className="flex items-center gap-2 mb-2">
                        <Lightbulb size={16} className="text-amber-500" />
                        <span className="text-xs font-semibold text-slate-700 uppercase tracking-wider">Summary</span>
                      </div>
                      <p className="text-sm text-slate-800 leading-relaxed">{askResult.summary}</p>
                    </div>

                    {/* Relevant Information */}
                    {askResult.relevant_information.length > 0 && (
                      <div className="bg-white rounded-xl border border-slate-200 p-4">
                        <div className="flex items-center gap-2 mb-2">
                          <Info size={16} className="text-blue-500" />
                          <span className="text-xs font-semibold text-slate-700 uppercase tracking-wider">Relevant Information</span>
                        </div>
                        <ul className="space-y-2">
                          {askResult.relevant_information.map((info, i) => (
                            <li key={i} className="flex items-start gap-2 text-sm text-slate-700">
                              <div className="h-5 w-5 rounded-full bg-blue-50 flex items-center justify-center shrink-0 mt-0.5">
                                <div className="h-1.5 w-1.5 rounded-full bg-blue-500" />
                              </div>
                              <span>{info}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Answer */}
                    <div className="bg-gradient-to-br from-emerald-50 to-green-50 rounded-xl border border-emerald-100 p-4">
                      <div className="flex items-center gap-2 mb-2">
                        <CheckCircle2 size={16} className="text-emerald-600" />
                        <span className="text-xs font-semibold text-slate-700 uppercase tracking-wider">Answer</span>
                      </div>
                      <p className="text-sm text-slate-800 leading-relaxed">{askResult.answer}</p>
                    </div>
                  </div>
                )}

                {/* Initial state */}
                {!askResult && !askLoading && !askError && (
                  <div className="flex flex-col items-center justify-center py-8 gap-2">
                    <div className="h-10 w-10 rounded-full bg-indigo-50 flex items-center justify-center">
                      <MessageSquareText size={20} className="text-indigo-500" />
                    </div>
                    <p className="text-sm text-slate-500 text-center">
                      Ask a natural language question about contributors or pick a suggestion above.
                    </p>
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      )}
    </>
  );
}