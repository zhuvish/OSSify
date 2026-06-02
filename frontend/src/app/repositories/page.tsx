import { useEffect, useMemo, useState } from "react";
import RepositoryCard from "@/src/components/RepositoryCard";
import Sidebar from "@/src/components/Sidebar";
import { getRepositories } from "@/src/lib/api";
import { useRouter } from "next/navigation";

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
    <div className="ml-5 mr-5  space-y-8">

      <div className="flex justify-between items-center">

        <div>
          <h1 className="text-2xl font-bold">
            Repositories
          </h1>
        </div>

        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search repositories..."
          className="
            bg-white
            border
            border-slate-300
            rounded-xl
            px-4
            py-2
            w-72
          "
        />
      </div>

      {loading ? (
        <div className="grid grid-cols-2 gap-6">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="bg-white rounded-xl border border-slate-200 p-5 animate-pulse h-40" />
          ))}
        </div>
      ) : filtered.length === 0 ? (
        <div className="bg-white rounded-xl border border-slate-200 p-8 text-center">
          No repositories found.
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-6">
          {filtered.map((r) => (
            <div key={r.id} onClick={() => openRepo(r)} className="cursor-pointer">
              <RepositoryCard
                name={r.full_name || r.name}
                url={r.url || ''}
                contributors={r.contributors || 0}
                commits={r.commits || 0}
                issues={r.issues || 0}
              />
            </div>
          ))}
        </div>
      )}

    </div>
  );
}