"use client";

import { useEffect, useState } from "react";
import { useRouter, useParams } from "next/navigation";
import { getContributor } from "@/src/lib/contributors";
import GraphView from "@/src/components/GraphView";
import DigitalTwinCard from "@/src/components/DigitalTwinCard";

export default function ContributorProfile() {
  const params = useParams();
  const contributorId = Number(params?.id);

  const [profile, setProfile] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);
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

  if (loading) {
    return (
      <div className="p-8 space-y-6 animate-pulse">
        <div className="bg-white rounded-2xl border border-slate-200 p-6">
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

        <div className="bg-white rounded-2xl border border-slate-200 p-6">
          <div className="h-24 bg-slate-200 rounded" />
        </div>

        <div className="bg-white rounded-2xl border border-slate-200 p-6">
          <div className="flex gap-3">
            <div className="h-8 w-24 bg-slate-200 rounded" />
            <div className="h-8 w-24 bg-slate-200 rounded" />
            <div className="h-8 w-24 bg-slate-200 rounded" />
          </div>
        </div>

        <div className="bg-white rounded-2xl border border-slate-200 p-6">
          <div className="h-40 bg-slate-200 rounded" />
        </div>
      </div>
    );
  }

  if (!profile) {
    return <div className="p-8">Contributor not found.</div>;
  }

  return (
    <div className="space-y-6">

      {/* Header */}
      <div className="px-6">

        <div className="flex items-center gap-5">

          <img
            src={profile.avatar_url}
            className="w-24 h-24 rounded-full"
          />

          <div className="flex-1">

            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-bold">
                {profile.username}
              </h1>

              <a
                href={profile.profile_url}
                target="_blank"
                className="text-sm text-slate-500"
              >
                GitHub
              </a>
            </div>

            <div className="flex gap-3 mt-3">

              <span className="px-3 py-1 rounded-full bg-indigo-100 text-indigo-700 text-sm">
                {profile.commit_count} Commits
              </span>

              <span className="px-3 py-1 rounded-full bg-green-100 text-green-700 text-sm">
                {profile.top_repositories ? profile.top_repositories.length : 0} Repositories
              </span>

              <span className="px-3 py-1 rounded-full bg-purple-100 text-purple-700 text-sm">
                {(profile.expertise_areas || []).length} Expertise Areas
              </span>

            </div>
          </div>

        </div>
      </div>

      {/* Summary */}
      <div className="bg-white rounded-xl border border-slate-200 p-6">

        <div className="flex justify-between items-start mb-2">
          <h2 className="text-xl font-semibold">
            Contributor Summary
          </h2>

          <div className="flex flex-wrap gap-2 max-w-[50%] justify-end mr-10">

            {(profile.expertise_areas || []).map((e: any) => (
              <span key={e.domain} className="px-3 py-1 rounded-full bg-violet-100 text-indigo-700 text-sm">{e.domain}</span>
            ))}

          </div>
        </div>
        <div className="mt-4 border-t border-slate-100 pt-4"></div>
        <p className="text-slate-600 leading-7">
          {profile.semantic_expertise_summary && profile.semantic_expertise_summary.length ? (
            profile.semantic_expertise_summary.map((s: any) => s.term).join(', ')
          ) : (profile.bio || 'No summary available.')}
        </p>
      </div>

      <div className="grid grid-cols-4 gap-6">
        {/*Knowledge Graph*/}
        <div className="col-span-3">
          <div className="bg-white rounded-2xl border border-slate-200 p-6 h-full">
            <h2 className="text-xl font-semibold mb-4">
              Knowledge Graph
            </h2>
            <div className="h-[500px] rounded-xl border border-slate-100 overflow-hidden">
              {typeof window !== "undefined" &&
                localStorage.getItem("selected_repo_id") && (
                  <GraphView
                    repoId={Number(
                      localStorage.getItem("selected_repo_id")
                    )}
                  />
                )}
            </div>
          </div>
        </div>

        <div className="col-span-1 flex flex-col gap-6">
          {/* Active Repositories*/}
          <div className="bg-white rounded-2xl border border-slate-200 p-5">
            <h2 className="font-semibold mb-4">
              Active Repositories
            </h2>
            <div className="space-y-3">
              {(profile.top_repositories || []).map((r: any) => (
                <div
                  key={r.name}
                  className="
                  rounded-xl
                  border
                  border-slate-100
                  p-3
                  "
                >
                  <div className="font-medium">
                    {r.name}
                  </div>
                </div>
              ))}
            </div>
          </div>
          <div className="bg-white rounded-2xl border border-slate-200 p-5">
            <h2 className="font-semibold mb-4">
              Recent Activity
            </h2>
            <div className="space-y-4">
              {(profile.recent_activity || [])
                .slice(0, 6)
                .map((a: any, idx: number) => (
                  <div
                    key={idx}
                    className="border-l-2 border-violet-200 pl-3">
                    <div className="text-sm font-medium">
                      {a.description || a.sha}
                    </div>
                    <div className="text-xs text-slate-500 mt-1">
                      {a.date}
                    </div>
                  </div>
                ))}
            </div>
          </div>
        </div>
      </div>

      {/* Digital Twin Card */}
      <div className="mt-6">
        <DigitalTwinCard contributorId={contributorId} />
      </div>
    </div>
  );
}