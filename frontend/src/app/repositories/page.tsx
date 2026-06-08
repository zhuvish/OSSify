"use client";

import { useEffect, useMemo, useState } from "react";
import RepositoryCard from "@/src/components/RepositoryCard";
import Sidebar from "@/src/components/Sidebar";
import { getRepositories } from "@/src/lib/api";
import { useRouter } from "next/navigation";
import { Search, Grid3X3, List } from "lucide-react";

export default function RepositoriesPage() {
  const [repos, setRepos] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [query, setQuery] = useState("");
  const router = useRouter();

  useEffect(() => {
    let mounted = true;
    setLoading(true);
    getRepositories()
      .then((data) => {
        if (!mounted) return;
        setRepos(data || []);
      })
      .catch(() => {
        setRepos([]);
      })
      .finally(() => {
        if (mounted) setLoading(false);
      });

    return () => {
      mounted = false;
    };
  }, []);

  const filtered = useMemo(() => {
    if (!query) return repos;
    const q = query.toLowerCase();
    return repos.filter((r) => (r.name || r.full_name || "").toLowerCase().includes(q));
  }, [repos, query]);

  function openRepo(repo: any) {
    localStorage.setItem("selected_repo_id", String(repo.id));
    localStorage.setItem("selected_repo_name", repo.name || repo.full_name || "");
    router.push("/dashboard");
  }

  return (
    <div className="px-6 py-6 max-w-7xl mx-auto space-y-8">

      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 tracking-tight">
            Repositories
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Browse and manage your analyzed repositories
          </p>
        </div>

        <div className="relative w-full sm:w-80">
          <Search size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search repositories..."
            className="
              w-full
              bg-white
              border
              border-slate-200
              rounded-xl
              pl-10
              pr-4
              py-2.5
              text-sm
              placeholder:text-slate-400
              focus:outline-none
              focus:ring-2
              focus:ring-violet-500/20
              focus:border-violet-400
              transition-all
              shadow-sm
            "
          />
        </div>
      </div>

      {/* Loading */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="bg-white rounded-2xl border border-slate-200/80 p-6 animate-pulse">
              <div className="flex items-start gap-4 mb-5">
                <div className="w-14 h-14 rounded-xl bg-slate-200" />
                <div className="flex-1 space-y-2">
                  <div className="h-5 w-3/4 bg-slate-200 rounded" />
                  <div className="h-4 w-1/2 bg-slate-200 rounded" />
                </div>
              </div>
              <div className="flex gap-3 mb-5">
                <div className="h-4 w-20 bg-slate-200 rounded" />
                <div className="h-4 w-24 bg-slate-200 rounded" />
                <div className="h-4 w-20 bg-slate-200 rounded" />
              </div>
              <div className="h-5 w-32 bg-slate-200 rounded ml-auto" />
            </div>
          ))}
        </div>
      ) : filtered.length === 0 ? (
        <div className="bg-white rounded-2xl border border-slate-200/80 p-12 text-center">
          <div className="w-16 h-16 rounded-2xl bg-slate-100 flex items-center justify-center mx-auto mb-4">
            <Search size={24} className="text-slate-400" />
          </div>
          <h3 className="text-lg font-semibold text-slate-900 mb-1">No repositories found</h3>
          <p className="text-sm text-slate-500">Try adjusting your search query</p>
        </div>
      ) : (
        <>
          {/* Results count */}
          <div className="flex items-center justify-between">
            <p className="text-sm text-slate-500">
              Showing <span className="font-medium text-slate-700">{filtered.length}</span> {filtered.length === 1 ? "repository" : "repositories"}
            </p>
          </div>

          {/* Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {filtered.map((r) => (
              <div key={r.id} onClick={() => openRepo(r)} className="cursor-pointer">
                <RepositoryCard
                  name={r.full_name || r.name}
                  url={r.url || ''}
                  contributors={r.contributors || 0}
                  commits={r.commits || 0}
                  issues={r.issues || 0}
                  topics={r.topics || r.topic || []}
                />
              </div>
            ))}
          </div>
        </>
      )}

    </div>
  );
}