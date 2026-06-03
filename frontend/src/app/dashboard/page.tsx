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
    // Read selected repo info from localStorage after hydration
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

      <div className="flex justify-end gap-4 mb-4">

              <div className="bg-white px-5 py-3 rounded-2xl shadow-sm flex items-center gap-2">
        <FileText size={18} />
        <span>{stats.repositories} Repository</span>
      </div>

      <div className="bg-white px-5 py-3 rounded-2xl shadow-sm flex items-center gap-2">
        <Users size={18} />
        <span>{stats.contributors} Contributors</span>
      </div>

      <div className="bg-white px-5 py-3 rounded-2xl shadow-sm flex items-center gap-2">
        <Calendar size={18} />
        <span>
          {stats.last_updated
            ? new Date(stats.last_updated).toLocaleDateString()
            : ""}
        </span>
      </div>

      </div>

      <div className="bg-gradient-to-r from-blue-600 via-indigo-600 to-violet-600 rounded-[32px] px-10 py-12 mb-8">

        <h1 className="text-6xl font-bold text-white">
          OSSify 🚀 {repoName}
        </h1>

        {/* <p className="text-white/80 mt-2 mb-8 text-lg"> */}
        <p className="text-white/90 mt-3 mb-10 text-xl">
          Discover expertise, contributor
          networks and repository knowledge.
        </p>

        <div className="grid grid-cols-4 gap-6">

          <StatCard
            icon={FolderGit2}
            value={stats.repositories}
            title="Repositories"
            subtitle="Tracked Repository"
          />

          <StatCard
            icon={Users}
            value={stats.contributors}
            title="Contributors"
            subtitle="Active Contributors"
          />

          <StatCard
            icon={FileText}
            value={stats.files}
            title="Files"
            subtitle="In Repository"
          />

          <StatCard
            icon={Tags}
            value={stats.topics}
            title="Topics"
            subtitle="Detected Topics"
          />

        </div>
      </div>

      <div className="grid grid-cols-12 gap-6">

        <div className="col-span-4">
          <TopExperts experts={topExperts} />
        </div>

        <div className="col-span-8">

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