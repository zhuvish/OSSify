"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { getContributors, searchContributors } from "@/src/lib/contributors";
import ContributorSearch from "@/src/components/ContributorSearch";
import { Search, Code2, GitCommit, Award, ArrowUpRight } from "lucide-react";

type SortBy = "expertise" | "contributions" | "name";

export default function ContributorsPage() {
  const [contributors, setContributors] = useState<any[]>([]);
  const [initialContributors, setInitialContributors] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState("");
  const [sortBy, setSortBy] = useState<SortBy>("contributions");
  const [topicFilter, setTopicFilter] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    let mounted = true;
    async function load() {
      setLoading(true);
      const repoId = localStorage.getItem("selected_repo_id");
      if (!repoId) {
        setContributors([]);
        setLoading(false);
        return;
      }

      try {
        const data = await getContributors(Number(repoId));
        if (!mounted) return;
        setContributors(data || []);
        setInitialContributors(data || []);
      } catch (e) {
        setContributors([]);
      } finally {
        if (mounted) setLoading(false);
      }
    }

    load();
    return () => { mounted = false; };
  }, []);

  useEffect(() => {
    // Debounced server-side search when query length >= 2
    if (query.length >= 2) {
      const t = setTimeout(async () => {
        setLoading(true);
        try {
          const results = await searchContributors(query);
          setContributors(results || []);
        } catch (e) {
          setContributors([]);
        } finally {
          setLoading(false);
        }
      }, 350);

      return () => clearTimeout(t);
    } else {
      // restore initial list when query cleared
      setContributors(initialContributors);
    }
  }, [query]);

  const topics = useMemo(() => {
    const set = new Set<string>();
    contributors.forEach((c) => (c.top_expertise || []).forEach((t: string) => set.add(t)));
    return Array.from(set).sort();
  }, [contributors]);

  const filtered = useMemo(() => {
    let list = contributors.slice();

    if (query) {
      const q = query.toLowerCase();
      list = list.filter((c) => (c.username || "").toLowerCase().includes(q));
    }

    if (topicFilter) {
      list = list.filter((c) => (c.top_expertise || []).includes(topicFilter));
    }

    if (sortBy === "expertise") {
      list.sort((a, b) => (b.expertise_score || 0) - (a.expertise_score || 0));
    } else if (sortBy === "contributions") {
      list.sort((a, b) => (b.commit_count || 0) - (a.commit_count || 0));
    } else if (sortBy === "name") {
      list.sort((a, b) => (a.username || "").localeCompare(b.username || ""));
    }

    return list;
  }, [contributors, query, sortBy, topicFilter]);

  function getExpertiseStrength(score: number): number {
    // Normalize expertise score to 0-100 for progress bar
    return Math.min(Math.round((score || 0) * 20), 100);
  }

  function getProgressColor(score: number): string {
    if (score >= 80) return "bg-gradient-to-r from-violet-500 to-indigo-600";
    if (score >= 50) return "bg-gradient-to-r from-violet-400 to-indigo-500";
    if (score >= 30) return "bg-gradient-to-r from-violet-300 to-indigo-400";
    return "bg-gradient-to-r from-slate-300 to-slate-400";
  }

  function getInitial(name: string): string {
    return (name?.[0] || "U").toUpperCase();
  }

  return (
    <div className="px-6 py-6 max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 tracking-tight">
            Contributors
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Search, sort and filter contributors for the selected repository
          </p>
        </div>

        <div className="flex items-center gap-3 flex-wrap">
          <ContributorSearch
            value={query}
            onChange={(v) => setQuery(v)}
            onSelect={(item) => router.push(`/contributors/${item.id}`)}
          />

          <select value={sortBy} onChange={(e) => setSortBy(e.target.value as SortBy)} className="rounded-xl border border-slate-200 px-3.5 py-2.5 bg-white text-sm text-slate-600 focus:outline-none focus:ring-2 focus:ring-violet-500/20 focus:border-violet-400 shadow-sm">
            <option value="contributions">Sort: Contributions</option>
            <option value="expertise">Sort: Expertise Score</option>
            <option value="name">Sort: Name</option>
          </select>

          <select value={topicFilter || ""} onChange={(e) => setTopicFilter(e.target.value || null)} className="rounded-xl border border-slate-200 px-3.5 py-2.5 bg-white text-sm text-slate-600 focus:outline-none focus:ring-2 focus:ring-violet-500/20 focus:border-violet-400 shadow-sm">
            <option value="">Filter: All topics</option>
            {topics.map((t) => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Contributors Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="bg-white rounded-2xl border border-slate-200/80 p-6 animate-pulse">
              <div className="flex items-center gap-4 mb-5">
                <div className="w-14 h-14 rounded-full bg-slate-200" />
                <div className="flex-1 space-y-2">
                  <div className="h-5 w-28 bg-slate-200 rounded" />
                  <div className="h-4 w-20 bg-slate-200 rounded" />
                </div>
              </div>
              <div className="flex gap-2 mb-5">
                <div className="h-6 w-16 bg-slate-200 rounded-full" />
                <div className="h-6 w-20 bg-slate-200 rounded-full" />
                <div className="h-6 w-14 bg-slate-200 rounded-full" />
              </div>
              <div className="h-3 bg-slate-200 rounded-full mb-5" />
              <div className="h-10 w-full bg-slate-200 rounded-xl" />
            </div>
          ))}
        </div>
      ) : filtered.length === 0 ? (
        <div className="bg-white rounded-2xl border border-slate-200/80 p-12 text-center">
          <div className="w-16 h-16 rounded-2xl bg-slate-100 flex items-center justify-center mx-auto mb-4">
            <Search size={24} className="text-slate-400" />
          </div>
          <h3 className="text-lg font-semibold text-slate-900 mb-1">No contributors found</h3>
          <p className="text-sm text-slate-500">Try adjusting your search or filter criteria</p>
        </div>
      ) : (
        <>
          {/* Results count */}
          <div>
            <p className="text-sm text-slate-500">
              Showing <span className="font-medium text-slate-700">{filtered.length}</span> {filtered.length === 1 ? "contributor" : "contributors"}
            </p>
          </div>

          {/* Card Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filtered.map((c) => {
              const expertiseStrength = getExpertiseStrength(c.expertise_score);
              const progressColor = getProgressColor(expertiseStrength);

              return (
                <div
                  key={c.id}
                  className="group bg-white rounded-2xl border border-slate-200/80 p-6 hover:shadow-xl hover:-translate-y-1 transition-all duration-300 ease-out flex flex-col"
                >
                  {/* Avatar + Username */}
                  <div className="flex items-center gap-4 mb-5">
                    <div className="relative shrink-0">
                      <img
                        src={c.avatar_url}
                        className="w-14 h-14 rounded-full object-cover ring-2 ring-slate-100 group-hover:ring-violet-200 transition-all"
                        alt={c.username}
                      />
                      <div className="absolute -bottom-0.5 -right-0.5 w-5 h-5 bg-emerald-400 border-2 border-white rounded-full" />
                    </div>
                    <div className="min-w-0 flex-1">
                      <h2 className="font-semibold text-base text-slate-900 truncate group-hover:text-violet-700 transition-colors">
                        {c.username}
                      </h2>
                      <div className="flex items-center gap-1.5 text-xs text-slate-400 mt-0.5">
                        <Award size={12} />
                        <span>Contributor</span>
                      </div>
                    </div>
                  </div>

                  {/* Expertise Tags */}
                  <div className="flex flex-wrap gap-1.5 mb-5 min-h-[28px]">
                    {(c.top_expertise || []).slice(0, 4).map((skill: string, idx: number) => (
                      <span
                        key={`${skill}-${idx}`}
                        className="px-2.5 py-1 rounded-full bg-violet-50 text-violet-700 text-xs font-medium border border-violet-200/50"
                      >
                        {skill}
                      </span>
                    ))}
                    {(c.top_expertise || []).length > 4 && (
                      <span className="px-2.5 py-1 rounded-full bg-slate-50 text-slate-500 text-xs font-medium border border-slate-200">
                        +{c.top_expertise.length - 4}
                      </span>
                    )}
                  </div>

                  {/* Commit Count + Expertise Score */}
                  <div className="grid grid-cols-2 gap-3 mb-5">
                    <div className="bg-slate-50 rounded-xl p-3 border border-slate-100">
                      <div className="flex items-center gap-1.5 text-xs text-slate-400 mb-1">
                        <GitCommit size={12} />
                        <span>Commits</span>
                      </div>
                      <p className="text-lg font-bold text-slate-900">
                        {c.commit_count || 0}
                      </p>
                    </div>
                    <div className="bg-violet-50 rounded-xl p-3 border border-violet-100">
                      <div className="flex items-center gap-1.5 text-xs text-slate-400 mb-1">
                        <Code2 size={12} />
                        <span>Expertise</span>
                      </div>
                      <p className="text-lg font-bold text-violet-700">
                        {Math.round((c.expertise_score || 0) * 10) / 10}
                      </p>
                    </div>
                  </div>

                  {/* Expertise Strength Progress Bar */}
                  <div className="mb-5">
                    <div className="flex justify-between items-center mb-1.5">
                      <span className="text-xs font-medium text-slate-500">Expertise Strength</span>
                      <span className="text-xs font-semibold text-slate-700">{expertiseStrength}%</span>
                    </div>
                    <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all duration-500 ${progressColor}`}
                        style={{ width: `${expertiseStrength}%` }}
                      />
                    </div>
                  </div>

                  {/* Spacer */}
                  <div className="flex-1" />

                  {/* Divider */}
                  <div className="border-t border-slate-100 mb-4" />

                  {/* View Profile Button */}
                  <Link
                    href={`/contributors/${c.id}`}
                    className="w-full inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 text-white text-sm font-medium shadow-md shadow-violet-200 hover:shadow-lg hover:shadow-violet-300 hover:from-violet-500 hover:to-indigo-500 transition-all duration-200 group/btn"
                  >
                    <span>View Profile</span>
                    <ArrowUpRight size={15} className="group-hover/btn:translate-x-0.5 group-hover/btn:-translate-y-0.5 transition-transform" />
                  </Link>
                </div>
              );
            })}
          </div>
        </>
      )}
    </div>
  );
}