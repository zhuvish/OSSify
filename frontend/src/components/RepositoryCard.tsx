import {
  FolderGit2,
  ExternalLink,
} from "lucide-react";

type Props = {
  name: string;
  url: string;
  contributors: number;
  commits: number;
  issues: number;
  topics?: string[];
};

function getInitial(name: string): string {
  return (name?.[0] || "R").toUpperCase();
}

function getColorFromName(name: string): string {
  const colors = [
    "from-violet-500 to-indigo-600",
    "from-blue-500 to-cyan-600",
    "from-emerald-500 to-teal-600",
    "from-rose-500 to-pink-600",
    "from-amber-500 to-orange-600",
    "from-purple-500 to-fuchsia-600",
  ];
  let hash = 0;
  for (let i = 0; i < (name || "").length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash);
  }
  return colors[Math.abs(hash) % colors.length];
}

function getTopicColor(topic: string): string {
  const colors = [
    "bg-violet-50 text-violet-700 border-violet-200",
    "bg-blue-50 text-blue-700 border-blue-200",
    "bg-emerald-50 text-emerald-700 border-emerald-200",
    "bg-amber-50 text-amber-700 border-amber-200",
    "bg-rose-50 text-rose-700 border-rose-200",
    "bg-cyan-50 text-cyan-700 border-cyan-200",
    "bg-purple-50 text-purple-700 border-purple-200",
    "bg-pink-50 text-pink-700 border-pink-200",
  ];
  let hash = 0;
  for (let i = 0; i < topic.length; i++) {
    hash = topic.charCodeAt(i) + ((hash << 5) - hash);
  }
  return colors[Math.abs(hash) % colors.length];
}

export default function RepositoryCard({
  name,
  url,
  contributors,
  commits,
  issues,
  topics,
}: Props) {
  const initial = getInitial(name);
  const gradient = getColorFromName(name);

  return (
    <div className="group bg-white rounded-2xl border border-slate-200/80 p-6 hover:shadow-xl hover:-translate-y-1 transition-all duration-300 ease-out cursor-pointer flex flex-col h-full">

      {/* Avatar + Name + URL */}
      <div className="flex items-start gap-4 mb-5">
        <div className={`w-14 h-14 rounded-xl bg-gradient-to-br ${gradient} flex items-center justify-center text-white font-bold text-xl shadow-sm shrink-0`}>
          {initial}
        </div>
        <div className="min-w-0 flex-1">
          <h2 className="font-semibold text-lg text-slate-900 truncate group-hover:text-violet-700 transition-colors">
            {name}
          </h2>
          <a
            href={url}
            target="_blank"
            rel="noopener noreferrer"
            onClick={(e) => e.stopPropagation()}
            className="text-sm text-slate-400 hover:text-violet-600 truncate block mt-0.5 transition-colors"
          >
            <span className="flex items-center gap-1">
              <FolderGit2 size={13} />
              <span className="truncate">{url || "No URL"}</span>
              <ExternalLink size={11} className="shrink-0 opacity-0 group-hover:opacity-100 transition-opacity" />
            </span>
          </a>
        </div>
      </div>

      {/* Stats row */}
      <div className="flex items-center gap-4 mb-5 text-sm">
        <span className="flex items-center gap-1.5 text-slate-500">
          <span className="w-2 h-2 rounded-full bg-emerald-400" />
          {commits} commits
        </span>
        <span className="text-slate-300">·</span>
        <span className="flex items-center gap-1.5 text-slate-500">
          <span className="w-2 h-2 rounded-full bg-blue-400" />
          {contributors} contributors
        </span>
        <span className="text-slate-300">·</span>
        <span className="flex items-center gap-1.5 text-slate-500">
          <span className="w-2 h-2 rounded-full bg-amber-400" />
          {issues} issues
        </span>
      </div>

      {/* Topic Pills */}
      {topics && topics.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-5 flex-1">
          {topics.slice(0, 6).map((topic) => (
            <span
              key={topic}
              className={`px-3 py-1 rounded-full text-xs font-medium border ${getTopicColor(topic)}`}
            >
              {topic}
            </span>
          ))}
          {topics.length > 6 && (
            <span className="px-3 py-1 rounded-full text-xs font-medium bg-slate-100 text-slate-500 border border-slate-200">
              +{topics.length - 6} more
            </span>
          )}
        </div>
      )}

      {(!topics || topics.length === 0) && <div className="flex-1" />}

      {/* Divider */}
      <div className="border-t border-slate-100 -mx-6 mb-5" />

      {/* CTA Button */}
      <div className="flex justify-end">
        <span className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 text-white text-sm font-medium shadow-md shadow-violet-200 hover:shadow-lg hover:shadow-violet-300 hover:from-violet-500 hover:to-indigo-500 transition-all duration-200 group/btn">
          <span>Open Dashboard</span>
          <span className="text-lg group-hover/btn:translate-x-0.5 transition-transform">→</span>
        </span>
      </div>
    </div>
  );
}