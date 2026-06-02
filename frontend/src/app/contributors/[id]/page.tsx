"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getContributor } from "@/src/lib/contributors";
import GraphView from "@/src/components/GraphView";

export default function ContributorProfile({ params }: { params: { id: string } }) {
  const [profile, setProfile] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    let mounted = true;
    async function load() {
      setLoading(true);
      try {
        const data = await getContributor(Number(params.id));
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
  }, [params.id]);

  if (loading) {
    return <div className="p-8">Loading contributor...</div>;
  }

  if (!profile) {
    return <div className="p-8">Contributor not found.</div>;
  }

  return (
    <div className="space-y-6">

      {/* Header */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6">

        <div className="flex items-center gap-5">

          <div className="h-20 w-20 rounded-full bg-indigo-100 flex items-center justify-center text-3xl font-bold text-indigo-700">
            {profile.username ? profile.username.charAt(0).toUpperCase() : 'U'}
          </div>

          <div>
            <h1 className="text-3xl font-bold text-slate-900">{profile.username}</h1>

            <p className="text-slate-500">
              {profile.profile_url}
            </p>

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
      <div className="bg-white rounded-2xl border border-slate-200 p-6">

        <h2 className="text-xl font-semibold mb-4">Contributor Summary</h2>

        <p className="text-slate-600 leading-7">
          {profile.semantic_expertise_summary && profile.semantic_expertise_summary.length ? (
            profile.semantic_expertise_summary.map((s:any) => s.term).join(', ')
          ) : (profile.bio || 'No summary available.')}
        </p>

      </div>

      {/* Two-column section */}
      <div className="grid grid-cols-3 gap-6">

        {/* Repository Contributions */}
        <div className="col-span-2 bg-white rounded-2xl border border-slate-200 p-6">

          <h2 className="text-xl font-semibold mb-4">Repository Contributions</h2>

          <ul className="space-y-4">
            {(profile.top_repositories || []).map((r:any) => (
              <li key={r.name}>
                <p className="font-medium">{r.name}</p>
                <p className="text-slate-500 text-sm">Top repository</p>
              </li>
            ))}
          </ul>

        </div>

        {/* Recent Activity */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6">

          <h2 className="text-xl font-semibold mb-4">Recent Activity</h2>

          <div className="space-y-4">
            {(profile.recent_activity || []).map((a:any, idx:number) => (
              <div key={idx}>
                <p className="font-medium">{a.type === 'commit' ? (a.description || a.sha) : (a.description || '')}</p>
                <p className="text-sm text-slate-500">{a.date}</p>
              </div>
            ))}

            {(!profile.recent_activity || profile.recent_activity.length === 0) && (
              <div className="text-sm text-slate-500">No recent activity available.</div>
            )}

          </div>

        </div>

      </div>

      {/* Expertise */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6">

        <h2 className="text-xl font-semibold mb-4">Expertise</h2>

        <div className="flex flex-wrap gap-3">

          {(profile.expertise_areas || []).map((e:any) => (
            <span key={e.domain} className="px-4 py-2 rounded-full bg-indigo-100 text-indigo-700">{e.domain}</span>
          ))}

        </div>

      </div>

      {/* Digital Twin Card */}
      <div className="mt-6">
        <DigitalTwinCard contributorId={Number(params.id)} />
      </div>

      {/* Graph */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 mt-6">

        <h2 className="text-xl font-semibold mb-4">Repository Connections</h2>

        {/* show graph for the first repo the contributor contributed to if available */}
        {profile.top_repositories && profile.top_repositories.length > 0 ? (
          <div className="h-[350px] rounded-xl border-2 border-dashed border-slate-200">
            {/* GraphView expects repo id; attempt to read from localStorage selected_repo_id */}
            {typeof window !== 'undefined' && localStorage.getItem('selected_repo_id') && (
              <GraphView repoId={Number(localStorage.getItem('selected_repo_id'))} />
            )}
          </div>
        ) : (
          <div className="h-[350px] rounded-xl border-2 border-dashed border-slate-200 flex items-center justify-center text-slate-400">No repository connections</div>
        )}

      </div>

    </div>
  );
}