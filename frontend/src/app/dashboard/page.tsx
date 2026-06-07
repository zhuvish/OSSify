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

        <div className="col-span-11 h-[650px]">

          <div className="bg-white rounded-3xl p-6 border border-slate-200">

            <div className="flex justify-between mb-6 items-start">

              <div>
                <div className="flex items-center gap-3">
                  <Share2
                    size={28}
                    className="text-violet-500"
                  />

                  <h2 className="text-3xl font-bold">
                    Knowledge Graph
                  </h2>
                </div>

                <p className="text-slate-500">
                  Visualizing contributors,
                  files and topics
                </p>
              </div>

              <div className="flex items-center gap-6 text-sm">

                <div className="flex items-center gap-2">
                  <div className="h-3 w-3 rounded-full bg-black" />
                  Repository
                </div>

                <div className="flex items-center gap-2">
                  <div className="h-3 w-3 rounded-full bg-violet-500" />
                  File
                </div>

                <div className="flex items-center gap-2">
                  <div className="h-3 w-3 rounded-full bg-teal-500" />
                  Contributor
                </div>

                <div className="flex items-center gap-2">
                  <div className="h-3 w-3 rounded-full bg-blue-500" />
                  Topic
                </div>

              </div>

              {/* <select
                className="
                border
                rounded-xl
                px-4
                py-2
                text-sm
                bg-white
                "
              >
                <option>
                  Top 25 Contributors
                </option>
              </select> */}

              <select
                value={maxContributors}
                onChange={(e) =>
                  setMaxContributors(Number(e.target.value))
                }
              >
                <option value={25}>Top 25</option>
                <option value={50}>Top 50</option>
                <option value={999}>All</option>
              </select>

            </div>

            {repoId && (
              <GraphView repoId={repoId} maxContributors={maxContributors} />
            )}

            <AskAI />

          </div>

        </div>

      </div>

    </div>
  );
}