"use client";

import { useEffect, useState } from "react";
import dynamic from 'next/dynamic';
import { getDashboardStats } from "@/src/lib/dashboard";

import {
  Users,
  FolderGit2,
  FileText,
  Tags,
  Calendar,
  Share2,
  Crown,
} from "lucide-react";

import StatCard from "@/src/components/StatCard";
import TopExperts from "@/src/components/TopExperts";
import AskAI from "@/src/components/AskAI";

const GraphView = dynamic(() => import('@/src/components/GraphView'), { ssr: false });

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
  const [repoId, setRepoId] = useState<number | null>(null);
  const [maxContributors, setMaxContributors] = useState(25);

  useEffect(() => {
    if (typeof window === 'undefined') return;

    const name = localStorage.getItem("selected_repo_name");
    if (name) setRepoName(name);

    const stored = localStorage.getItem('selected_repo_id');
    const id = stored ? Number(stored) : null;
    if (id && !isNaN(id)) setRepoId(id);
  }, []);

  useEffect(() => {
    if (!repoId) return;

    async function load() {
      const data = await getDashboardStats(Number(repoId));
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
  }, [repoId]);

  return (
    <div>

      <div className="bg-gradient-to-r from-blue-500 via-indigo-600 to-violet-600 px-6 py-8 rounded-2xl ml-6 mr-6 mb-8">

        <div className="flex justify-between items-start mb-8">

          <div>
            <h1 className="text-2xl font-bold text-white">
              OSSify 🚀
            </h1>

            <p className="text-white/80 mt-2">
              Here's everything about {repoName}
            </p>
          </div>

          <div className="flex gap-3">
            <div className="bg-black/30 text-white px-3 py-1 rounded-2xl shadow-sm flex items-center gap-2">
              <FileText size={18} />
              <span className="text-sm">{stats.repositories} Repository</span>
            </div>

            <div className="bg-black/30 text-white px-3 py-1 rounded-2xl shadow-sm flex items-center gap-2">
              <Users size={18} />
              <span className="text-sm">{stats.contributors} Contributors</span>
            </div>

            <div className="bg-black/30 text-white px-3 py-1 rounded-2xl shadow-sm flex items-center gap-2">
              <Calendar size={18} />
              <span className="text-sm">
                {stats.last_updated
                  ? new Date(stats.last_updated).toLocaleDateString()
                  : ""}
              </span>
            </div>
          </div>
        </div>


        <div className="grid grid-cols-4 gap-4">

          <StatCard
            icon={FolderGit2}
            value={stats.repositories}
            title="Repositories"
            iconBg="bg-violet-100"
            iconColor="text-violet-600"
          />

          <StatCard
            icon={Users}
            value={stats.contributors}
            title="Contributors"
            iconBg="bg-blue-100"
            iconColor="text-blue-600"
          />

          <StatCard
            icon={FileText}
            value={stats.files}
            title="Files"
            iconBg="bg-emerald-100"
            iconColor="text-emerald-600"
          />

          <StatCard
            icon={Tags}
            value={stats.topics}
            title="Topics"
            iconBg="bg-yellow-100"
            iconColor="text-yellow-600"
          />

        </div>
      </div>

      <div className="grid grid-cols-16 gap-4">

        <div className="col-span-5">
          <TopExperts experts={topExperts} />
          {/* <RepositorySummary /> */}
        </div>

        <div className="col-span-11 mr-5">
          <div className="bg-white rounded-3xl p-5 border border-slate-200">
            <div className="mb-6">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <div className="flex items-center gap-3">
                    <Share2
                      size={24}
                      strokeWidth={1.5}
                      className="text-violet-500"
                    />

                    <h2 className="text-lg font-bold">
                      Repository Knowledge Map
                    </h2>
                  </div>

                  <p className="text-sm ml-10 text-slate-500 mt-1">
                    Repository → Topics → Top Experts
                  </p>
                </div>
                <div className="flex gap-4 text-sm text-slate-600">

                  <div className="flex items-center gap-2">
                    <div className="h-3 w-3 rounded-full bg-slate-900" />
                    Repository
                  </div>

                  <div className="flex items-center gap-2">
                    <div className="h-3 w-3 rounded-full bg-blue-500" />
                    Topic
                  </div>

                  <div className="flex items-center gap-2">
                    <div className="h-3 w-3 rounded-full bg-emerald-500" />
                    Expert
                  </div>

                </div>

                {/* <select
                  value={maxContributors}
                  onChange={(e) =>
                    setMaxContributors(Number(e.target.value))
                  }
                  className="border border-slate-200 rounded-xl px-4 py-2 bg-white text-sm"
                >
                  <option value={25}>Top 25</option>
                  <option value={50}>Top 50</option>
                  <option value={999}>All</option>
                </select> */}
              </div>
            </div>

            <div className="mt-4">
              {repoId && (
                <GraphView
                  repoId={repoId}
                  maxContributors={maxContributors}
                />
              )}
            </div>
          </div>
          <div className="mt-6">
            <AskAI />
          </div>
        </div>
      </div>
    </div>
  );
}