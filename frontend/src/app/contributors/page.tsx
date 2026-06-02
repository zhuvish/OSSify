"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { getContributors, searchContributors } from "@/src/lib/contributors";

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

  return (
    <div>
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-4xl font-bold text-slate-900">Contributors</h1>
          <p className="text-sm text-slate-500">Search, sort and filter contributors for the selected repository.</p>
        </div>

        <div className="flex items-center gap-3">
          <ContributorSearch
            value={query}
            onChange={(v) => setQuery(v)}
            onSelect={(item) => router.push(`/contributors/${item.id}`)}
          />

          <select value={sortBy} onChange={(e) => setSortBy(e.target.value as SortBy)} className="rounded-xl border px-3 py-2 bg-white">
            <option value="contributions">Sort: Contributions</option>
            <option value="expertise">Sort: Expertise Score</option>
            <option value="name">Sort: Name</option>
          </select>

          <select value={topicFilter || ""} onChange={(e) => setTopicFilter(e.target.value || null)} className="rounded-xl border px-3 py-2 bg-white">
            <option value="">Filter: All topics</option>
            {topics.map((t) => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Contributors List */}
      {loading ? (
        <div className="space-y-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="bg-white border border-slate-200 rounded-2xl p-6 animate-pulse h-24" />
          ))}
        </div>
      ) : filtered.length === 0 ? (
        <div className="bg-white border border-slate-200 rounded-2xl p-8 text-center">
          No contributors found.
        </div>
      ) : (
        <div className="space-y-4">
          {filtered.map((c) => (
            <Link key={c.id} href={`/contributors/${c.id}`} className="block">
              <div className="bg-white border border-slate-200 rounded-2xl p-6 hover:shadow-md transition">
                <div className="flex justify-between items-center">

                  <div className="flex items-center gap-4">

                    <div className="h-14 w-14 rounded-full bg-indigo-100 text-indigo-700 flex items-center justify-center font-bold text-lg">
                      {c.username ? c.username[0].toUpperCase() : "U"}
                    </div>

                    <div>
                      <h2 className="text-lg font-semibold text-slate-900">{c.username}</h2>

                      <div className="flex gap-2 mt-2">
                        {(c.top_expertise || []).slice(0, 4).map((skill: string) => (
                          <span key={skill} className="px-3 py-1 rounded-full bg-indigo-100 text-indigo-700 text-xs">{skill}</span>
                        ))}
                      </div>

                      <p className="mt-3 text-sm text-slate-500">{c.commit_count} commits • Expertise {Math.round((c.expertise_score || 0) * 10)/10}</p>
                    </div>

                  </div>

                  <div className="text-2xl text-slate-400">→</div>

                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}