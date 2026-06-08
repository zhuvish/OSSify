"use client";

import { useEffect, useState } from "react";
import { useRouter, useParams } from "next/navigation";
import { getContributor } from "@/src/lib/contributors";
import DigitalTwinCard from "@/src/components/DigitalTwinCard";
import ContributorGraph from "@/src/components/ContributorGraph";
import {
  Link as LinkIcon,
  ExternalLink,
  Code2,
  FolderGit2,
  Tags,
  GitCommit,
  ChevronRight,
  MessageSquare,
  Activity,
  BookOpen,
  Bot,
  Sparkles,
  ArrowUpRight,
  Globe,
  Map,
  Users,
  Star,
  GitPullRequest,
} from "lucide-react";
import ReactMarkdown from "react-markdown";

type Tab = "overview" | "activity" | "repositories";

export default function ContributorProfile() {
  const params = useParams();
  const contributorId = Number(params?.id);

  const [profile, setProfile] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<Tab>("overview");
  const router = useRouter();

  useEffect(() => {
    let mounted = true;
    async function load() {
      if (!contributorId || isNaN(contributorId)) {
        setProfile(null);
        setLoading(false);
        return;
      }

      setLoading(true);
      try {
        const data = await getContributor(contributorId);
        if (!mounted) return;
        setProfile(data);
      } catch (e) {
        setProfile(null);
      } finally {
        if (mounted) setLoading(false);
      }
    }
    load();
    return () => { mounted = false; };
  }, [contributorId]);

  // Derive expertise domains with scores for progress bars
  const expertiseDomains = (profile?.expertise_areas || []).map((e: any) => ({
    domain: e.domain || e,
    score: typeof e.score === "number" ? e.score : (profile?.expertise_score || 0) * 100,
  }));

  // Normalize expertise score for display
  const displayExpertiseScore = profile?.expertise_score
    ? Math.min(Math.round(profile.expertise_score * 20), 100)
    : expertiseDomains.length > 0
      ? Math.min(Math.round(expertiseDomains[0].score), 100)
      : 0;

  function scrollToSection(id: string) {
    const el = document.getElementById(id);
    if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function handleTabClick(tab: Tab) {
    setActiveTab(tab);
    if (tab === "activity") scrollToSection("recent-activity");
    else if (tab === "repositories") scrollToSection("active-repos");
    else window.scrollTo({ top: 0, behavior: "smooth" });
  }

  if (loading) {
    return (
      <div className="px-6 py-6 max-w-7xl mx-auto space-y-6 animate-pulse">
        <div className="bg-white rounded-2xl border border-slate-200/80 p-6">
          <div className="flex items-center gap-5">
            <div className="h-20 w-20 rounded-full bg-slate-200" />
            <div className="flex-1 space-y-3">
              <div className="h-6 w-48 bg-slate-200 rounded" />
              <div className="h-4 w-64 bg-slate-200 rounded" />
              <div className="flex gap-3 mt-3">
                <div className="h-6 w-24 bg-slate-200 rounded-full" />
                <div className="h-6 w-24 bg-slate-200 rounded-full" />
                <div className="h-6 w-24 bg-slate-200 rounded-full" />
              </div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-2xl border border-slate-200/80 p-6">
          <div className="h-24 bg-slate-200 rounded" />
        </div>
        <div className="grid grid-cols-4 gap-6">
          <div className="col-span-3 bg-white rounded-2xl border border-slate-200/80 p-6 h-96">
            <div className="h-6 w-48 bg-slate-200 rounded mb-4" />
            <div className="h-full bg-slate-100 rounded" />
          </div>
          <div className="col-span-1 space-y-6">
            <div className="bg-white rounded-2xl border border-slate-200/80 p-5">
              <div className="h-5 w-32 bg-slate-200 rounded mb-4" />
              <div className="space-y-3">
                <div className="h-16 bg-slate-200 rounded-xl" />
                <div className="h-16 bg-slate-200 rounded-xl" />
              </div>
            </div>
            <div className="bg-white rounded-2xl border border-slate-200/80 p-5">
              <div className="h-5 w-32 bg-slate-200 rounded mb-4" />
              <div className="space-y-3">
                <div className="h-12 bg-slate-200 rounded" />
                <div className="h-12 bg-slate-200 rounded" />
                <div className="h-12 bg-slate-200 rounded" />
              </div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-2xl border border-slate-200/80 p-6">
          <div className="h-48 bg-slate-200 rounded" />
        </div>
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="px-6 py-6 max-w-7xl mx-auto">
        <div className="bg-white rounded-2xl border border-slate-200/80 p-12 text-center">
          <div className="w-16 h-16 rounded-2xl bg-slate-100 flex items-center justify-center mx-auto mb-4">
            <Users size={24} className="text-slate-400" />
          </div>
          <h3 className="text-lg font-semibold text-slate-900 mb-1">Contributor not found</h3>
          <p className="text-sm text-slate-500">The requested contributor could not be loaded.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="px-6 py-6 max-w-7xl mx-auto space-y-8">

      {/* ===== 1. HERO PROFILE CARD ===== */}
      <div className="bg-white rounded-2xl border border-slate-200/80 p-6 md:p-8 hover:shadow-lg transition-shadow duration-300">
        <div className="flex flex-col md:flex-row items-start gap-6">
          {/* Left: Avatar + Info */}
          <div className="flex items-start gap-5 flex-1">
            <div className="relative shrink-0">
              <img
                src={profile.avatar_url}
                className="w-20 h-20 md:w-24 md:h-24 rounded-2xl object-cover ring-4 ring-violet-100"
                alt={profile.username}
              />
              <div className="absolute -bottom-1 -right-1 w-6 h-6 bg-emerald-400 border-[3px] border-white rounded-full" />
            </div>

            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-3 flex-wrap">
                <h1 className="text-2xl md:text-3xl font-bold text-slate-900 tracking-tight">
                  {profile.username}
                </h1>

                <a
                  href={profile.profile_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-100 text-slate-600 hover:bg-violet-100 hover:text-violet-700 transition-all text-sm font-medium"
                >
                  <Globe size={14} />
                  <span>GitHub</span>
                  <ExternalLink size={12} />
                </a>
              </div>

              <p className="text-sm text-slate-400 mt-1 flex items-center gap-1">
                <Sparkles size={13} className="text-violet-500" />
                <span>Open Source Contributor</span>
              </p>

              <div className="flex flex-wrap gap-2 mt-4">
                <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-violet-50 text-violet-700 text-sm font-medium border border-violet-200/50">
                  <Code2 size={14} />
                  {profile.commit_count || 0} Commits
                </span>
                <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-blue-50 text-blue-700 text-sm font-medium border border-blue-200/50">
                  <FolderGit2 size={14} />
                  {profile.top_repositories?.length || 0} Repositories
                </span>
                <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-purple-50 text-purple-700 text-sm font-medium border border-purple-200/50">
                  <Tags size={14} />
                  {(profile.expertise_areas || []).length} Topics
                </span>
              </div>
            </div>
          </div>

          {/* Right: Expertise Score Card */}
          <div className="w-full md:w-56 shrink-0 bg-gradient-to-br from-violet-600 to-indigo-700 rounded-2xl p-5 text-white">
            <div className="flex items-center gap-2 mb-3">
              <Star size={16} className="text-yellow-300" fill="currentColor" />
              <span className="text-sm font-medium text-violet-200">Expertise Score</span>
            </div>
            <div className="text-4xl font-bold tracking-tight mb-1">
              {displayExpertiseScore}%
            </div>
            <div className="w-full h-1.5 bg-white/20 rounded-full overflow-hidden mt-2">
              <div
                className="h-full bg-white rounded-full transition-all duration-1000"
                style={{ width: `${displayExpertiseScore}%` }}
              />
            </div>
            <p className="text-xs text-violet-200 mt-2">
              Based on {profile.commit_count || 0} contributions
            </p>
          </div>
        </div>
      </div>

      {/* ===== 2. TOP EXPERTISE SECTION ===== */}
      {expertiseDomains.length > 0 && (
        <div className="bg-white rounded-2xl border border-slate-200/80 p-6 hover:shadow-lg transition-shadow duration-300">
          <div className="flex items-center gap-2 mb-6">
            <div className="w-8 h-8 rounded-lg bg-violet-100 flex items-center justify-center">
              <Star size={16} className="text-violet-600" />
            </div>
            <h2 className="text-xl font-bold text-slate-900">Top Expertise</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-x-12 gap-y-4">
            {expertiseDomains.slice(0, 8).map((e: any, idx: number) => {
              const score = Math.min(Math.round(e.score), 100);
              return (
                <div key={`${e.domain}-${idx}`}>
                  <div className="flex justify-between items-center mb-1.5">
                    <span className="text-sm font-medium text-slate-700">{e.domain}</span>
                    <span className="text-sm font-bold text-violet-700">{score}%</span>
                  </div>
                  <div className="w-full h-2.5 bg-slate-100 rounded-full overflow-hidden">
                    <div
                      className="h-full rounded-full bg-gradient-to-r from-violet-500 to-indigo-600 transition-all duration-1000"
                      style={{ width: `${score}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* ===== 3. CONTRIBUTOR SUMMARY (ABOUT) ===== */}
      <div className="bg-white rounded-2xl border border-slate-200/80 p-6 hover:shadow-lg transition-shadow duration-300" id="contributor-summary">
        <div className="flex items-start justify-between gap-4 mb-4">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-violet-100 flex items-center justify-center">
              <BookOpen size={16} className="text-violet-600" />
            </div>
            <h2 className="text-xl font-bold text-slate-900">About {profile.username}</h2>
          </div>

          {/* Expertise tags in header */}
          <div className="flex flex-wrap gap-2 justify-end max-w-[50%]">
            {(profile.expertise_areas || []).slice(0, 3).map((e: any, idx: number) => (
              <span
                key={`${e.domain || e}-${idx}`}
                className="px-3 py-1 rounded-full bg-violet-50 text-violet-700 text-xs font-medium border border-violet-200/50"
              >
                {e.domain || e}
              </span>
            ))}
            {(profile.expertise_areas || []).length > 3 && (
              <span className="px-3 py-1 rounded-full bg-slate-50 text-slate-500 text-xs font-medium border border-slate-200">
                +{profile.expertise_areas.length - 3}
              </span>
            )}
          </div>
        </div>

        <div className="border-t border-slate-100 pt-5">
          <div className="prose prose-slate max-w-none text-slate-600 leading-relaxed">
            <ReactMarkdown>
              {profile.semantic_expertise_summary || "No summary available."}
            </ReactMarkdown>
          </div>
        </div>
      </div>

      {/* ===== 4. NAVIGATION TABS ===== */}
      <div className="flex items-center gap-1 bg-slate-100/80 rounded-xl p-1 border border-slate-200/60 w-fit">
        {[
          { id: "overview" as Tab, label: "Overview", icon: Map },
          { id: "activity" as Tab, label: "Activity", icon: Activity },
          { id: "repositories" as Tab, label: "Repositories", icon: FolderGit2 },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => handleTabClick(tab.id)}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 ${
              activeTab === tab.id
                ? "bg-white text-violet-700 shadow-sm border border-slate-200"
                : "text-slate-500 hover:text-slate-700 hover:bg-white/50"
            }`}
          >
            <tab.icon size={15} />
            <span>{tab.label}</span>
          </button>
        ))}
      </div>

      {/* ===== 5. KNOWLEDGE GRAPH + SIDEBAR ===== */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Knowledge Graph */}
        <div className="lg:col-span-3" id="knowledge-graph">
          <div className="bg-white rounded-2xl border border-slate-200/80 p-6 hover:shadow-lg transition-shadow duration-300 h-full">
            <div className="flex items-center gap-2 mb-5">
              <div className="w-8 h-8 rounded-lg bg-violet-100 flex items-center justify-center">
                <Map size={16} className="text-violet-600" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-slate-900">Knowledge Graph</h2>
                <p className="text-xs text-slate-400">Visual exploration of contributor expertise</p>
              </div>
            </div>
            <div className="h-[500px] rounded-xl border border-slate-100 overflow-hidden bg-slate-50/50">
              {typeof window !== "undefined" &&
                localStorage.getItem("selected_repo_id") && (
                  <ContributorGraph contributorId={contributorId} />
                )}
            </div>
          </div>
        </div>

        {/* Right Sidebar */}
        <div className="lg:col-span-1 flex flex-col gap-6">
          {/* Active Repositories */}
          <div className="bg-white rounded-2xl border border-slate-200/80 p-5 hover:shadow-lg transition-shadow duration-300" id="active-repos">
            <div className="flex items-center gap-2 mb-4">
              <div className="w-7 h-7 rounded-lg bg-blue-100 flex items-center justify-center">
                <FolderGit2 size={14} className="text-blue-600" />
              </div>
              <h2 className="font-semibold text-slate-900">Active Repositories</h2>
            </div>
            <div className="space-y-3">
              {(profile.top_repositories || []).map((r: any, idx: number) => (
                <div
                  key={`${r.name}-${idx}`}
                  className="group rounded-xl border border-slate-100 bg-slate-50/50 p-3.5 hover:border-violet-200 hover:bg-violet-50/30 transition-all duration-200 cursor-pointer"
                >
                  <div className="font-medium text-sm text-slate-900 group-hover:text-violet-700 transition-colors truncate">
                    {r.name}
                  </div>
                  <div className="flex items-center gap-3 mt-2 text-xs text-slate-400">
                    <span className="flex items-center gap-1">
                      <GitCommit size={11} />
                      {r.commits || r.commit_count || 0}
                    </span>
                    <span className="flex items-center gap-1">
                      <Users size={11} />
                      {r.contributors || r.contributor_count || 0}
                    </span>
                    {r.issues !== undefined && (
                      <span className="flex items-center gap-1">
                        <GitPullRequest size={11} />
                        {r.issues || r.issue_count || 0}
                      </span>
                    )}
                  </div>
                  <div className="mt-2 flex justify-end">
                    <span className="inline-flex items-center gap-1 text-xs font-medium text-violet-600 opacity-0 group-hover:opacity-100 transition-opacity">
                      Open <ArrowUpRight size={11} />
                    </span>
                  </div>
                </div>
              ))}
              {(profile.top_repositories || []).length === 0 && (
                <p className="text-sm text-slate-400 text-center py-4">No active repositories</p>
              )}
            </div>
          </div>

          {/* Recent Activity */}
          <div className="bg-white rounded-2xl border border-slate-200/80 p-5 hover:shadow-lg transition-shadow duration-300" id="recent-activity">
            <div className="flex items-center gap-2 mb-4">
              <div className="w-7 h-7 rounded-lg bg-emerald-100 flex items-center justify-center">
                <Activity size={14} className="text-emerald-600" />
              </div>
              <h2 className="font-semibold text-slate-900">Recent Activity</h2>
            </div>
            <div className="space-y-0">
              {(profile.recent_activity || []).slice(0, 6).map((a: any, idx: number) => (
                <div key={idx} className="relative flex gap-3 pb-4 last:pb-0">
                  {/* Timeline line */}
                  {idx < Math.min((profile.recent_activity || []).length - 1, 5) && (
                    <div className="absolute left-[7px] top-5 bottom-0 w-px bg-slate-200" />
                  )}
                  {/* Timeline dot */}
                  <div className="relative shrink-0 mt-1">
                    <div className="w-[15px] h-[15px] rounded-full border-2 border-violet-300 bg-white" />
                  </div>
                  {/* Content */}
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-medium text-slate-800 leading-snug">
                      {a.description || a.sha || "Activity"}
                    </p>
                    <p className="text-xs text-slate-400 mt-0.5">
                      {a.date || "Recent"}
                    </p>
                  </div>
                </div>
              ))}
              {(profile.recent_activity || []).length === 0 && (
                <p className="text-sm text-slate-400 text-center py-4">No recent activity</p>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* ===== 6. DIGITAL TWIN SECTION ===== */}
      <div className="bg-white rounded-2xl border border-slate-200/80 overflow-hidden hover:shadow-lg transition-shadow duration-300">
        <div className="p-6">
          <div className="flex items-center gap-3 mb-5">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center shadow-md shadow-violet-200">
              <Bot size={20} className="text-white" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2">
                Talk to {profile.username}'s Digital Twin
                <span className="px-2 py-0.5 rounded-full bg-gradient-to-r from-violet-500 to-indigo-600 text-white text-[10px] font-bold tracking-wider uppercase">AI</span>
              </h2>
              <p className="text-xs text-slate-400">Ask questions about their expertise and contributions</p>
            </div>
          </div>

          {/* Suggested prompts */}
          <div className="flex flex-wrap gap-2 mb-5">
            {expertiseDomains.slice(0, 4).map((e: any, idx: number) => (
              <span
                key={`prompt-${e.domain}-${idx}`}
                className="px-3 py-1.5 rounded-lg bg-slate-100 text-slate-600 text-xs font-medium border border-slate-200 hover:border-violet-200 hover:bg-violet-50 hover:text-violet-700 transition-all cursor-pointer"
              >
                <MessageSquare size={11} className="inline mr-1" />
                Explain {e.domain} expertise
              </span>
            ))}
            <span className="px-3 py-1.5 rounded-lg bg-gradient-to-r from-violet-500 to-indigo-600 text-white text-xs font-medium shadow-sm hover:shadow-md transition-all cursor-pointer">
              <Sparkles size={11} className="inline mr-1" />
              Suggest improvements
            </span>
          </div>

          {/* Digital Twin Component */}
          <DigitalTwinCard contributorId={contributorId} />
        </div>
      </div>

    </div>
  );
}