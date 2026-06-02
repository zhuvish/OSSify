"use client";

import { useEffect, useState } from "react";
import { getDashboardStats } from "@/src/lib/dashboard";

export default function DashboardPage() {
  const [stats, setStats] = useState({
    repositories: 0,
    contributors: 0,
    files: 0,
    topics: 0,
    last_updated: null,
  });
  const [repoName, setRepoName] = useState("");
  const [topExperts, setTopExperts] = useState<any[]>([]);
  const [topics, setTopics] = useState<any[]>([]);

  useEffect(() => {
    const name = localStorage.getItem(
      "selected_repo_name"
    );

    if (name) {
      setRepoName(name);
    }
  }, []);

  useEffect(() => {

    async function load() {

      const repoId = localStorage.getItem("selected_repo_id");

      if (!repoId) return;

      const data = await getDashboardStats(
        Number(repoId)
      );

      setStats(data);

      try {
        const experts = await (await fetch(`http://127.0.0.1:8000/repositories/${repoId}/top-experts`)).json();
        setTopExperts(experts || []);
      } catch (e) {
        setTopExperts([]);
      }

      try {
        const t = await (await fetch(`http://127.0.0.1:8000/repositories/${repoId}/topics`)).json();
        setTopics(t || []);
        setStats((s) => ({ ...s, topics: Array.isArray(t) ? t.length : s.topics }));
      } catch (e) {
        setTopics([]);
      }
    }

    load();

  }, []);

  return (
    <div className="bg-slate-100">

      <div className="ml-5 mr-5 rounded-xl bg-gradient-to-r from-indigo-700 to-blue-500 px-8 py-6">
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-2xl font-bold text-white">
              OSSify 🚀: {repoName}
            </h1>

            <p className="mt-2 text-blue-100 mb-8">
              Discover expertise, contributor networks and repository knowledge.
            </p>
          </div>
          <div className="mt-3 flex gap-3">
            <span className="bg-black/40 text-white px-4 py-1 rounded-2xl text-sm">
              {stats.repositories} Repo
            </span>

            <span className="bg-black/40 text-white px-4 py-1 rounded-2xl text-sm">
              {stats.contributors} Contributors
            </span>

            <span className="bg-black/40 text-white px-4 py-1 rounded-2xl text-sm">
              {stats.last_updated ? new Date(stats.last_updated).toLocaleDateString() : new Date().toLocaleDateString()}
            </span>
          </div>
        </div>
        <div className="grid grid-cols-4 gap-4">
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 py-3 px-4 h-20">
            <h3 className="text-2xl font-bold text-slate-900">{stats.repositories}</h3>
            <p className="text-slate-500">Repositories</p>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-slate-200 py-3 px-4 h-20">
            <h3 className="text-2xl font-bold text-slate-900">{stats.contributors}</h3>
            <p className="text-slate-500">Contributors</p>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-slate-200 py-3 px-4 h-20">
            <h3 className="text-2xl font-bold text-slate-900">{stats.files}</h3>
            <p className="text-slate-500">Files</p>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-slate-200 py-3 px-4 h-20">
            <h3 className="text-2xl font-bold text-slate-900">{stats.topics}</h3>
            <p className="text-slate-500">Topics</p>
          </div>
        </div>
      </div>

      <div className="ml-5 mr-5 grid grid-cols-12 gap-6 mt-6">

        <div className="col-span-3 space-y-6">
          <div className="bg-white rounded-2xl border border-slate-200 p-6">
            <h2 className="text-2xl font-semibold text-slate-900 mb-6">
              Top Experts
            </h2>

            <div className="space-y-5">
              {topExperts.length === 0 ? (
                <div className="text-sm text-slate-500">No experts yet.</div>
              ) : (
                topExperts.map((e) => (
                  <div key={e.id} className="flex items-center gap-3">
                    <div className="h-12 w-12 rounded-full bg-indigo-100 flex items-center justify-center font-bold text-indigo-700">
                      {e.username ? e.username.charAt(0).toUpperCase() : 'U'}
                    </div>

                    <div>
                      <p className="font-medium text-slate-900">{e.username}</p>

                      <div className="flex gap-2 mt-1">
                        {(e.topics || []).slice(0, 4).map((t: string) => (
                          <span key={t} className="px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-700">{t}</span>
                        ))}
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          <div className="bg-white rounded-2xl border border-slate-200 p-6 mt-6">
            <h2 className="text-xl font-semibold mb-5">
              Repository Activity
            </h2>

            <div className="space-y-5">

              <div>
                <p className="font-medium text-slate-900">
                  Fixed authentication bug
                </p>

                <p className="text-sm text-slate-500">
                  davidism • 2 hours ago
                </p>
              </div>

              <div>
                <p className="font-medium text-slate-900">
                  Added session middleware
                </p>

                <p className="text-sm text-slate-500">
                  pgjones • 5 hours ago
                </p>
              </div>

              <div>
                <p className="font-medium text-slate-900">
                  Refactored routing logic
                </p>

                <p className="text-sm text-slate-500">
                  justquick • yesterday
                </p>
              </div>

            </div>
          </div>
        </div>



        <div className="col-span-9">
          <div className="bg-white rounded-2xl border border-slate-200 p-6 h-[700px]">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-semibold">
                Knowledge Graph
              </h2>

              <button className="text-sm text-slate-500">
                Expand
              </button>
            </div>

            <div>
              {/* Graph visualization */}
              {typeof window !== 'undefined' && (
                (() => {
                  const repoId = Number(localStorage.getItem('selected_repo_id')) || null;
                  if (!repoId) {
                    return (
                      <div className="h-[600px] rounded-xl border-2 border-dashed border-slate-200 flex items-center justify-center">
                        <p className="text-slate-400">No repository selected</p>
                      </div>
                    );
                  }

                  // Lazy load GraphView
                  const GraphView = require('@/src/components/GraphView').default;
                  return <GraphView repoId={repoId} />;
                })()
              )}
            </div>
          </div>
        </div>

      </div>

    </div>
  );
}