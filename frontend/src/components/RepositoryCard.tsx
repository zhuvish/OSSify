import {
  FolderGit2,
  Users,
  GitCommit,
  CircleDot,
} from "lucide-react";

type Props = {
  name: string;
  url: string;
  contributors: number;
  commits: number;
  issues: number;
};

export default function RepositoryCard({
  name,
  url,
  contributors,
  commits,
  issues,
}: Props) {
  return (
    <div className="bg-white rounded-xl border border-slate-200 p-5 hover:shadow-lg hover:-translate-y-1 transition-all duration-200">

      <div className="flex items-center gap-2 mb-3">
        <FolderGit2
          size={18}
          className="text-indigo-500"
        />

        <h2 className="font-semibold text-lg">
          {name}
        </h2>
      </div>

      <p className="text-slate-500 text-sm mb-5">
        {url}
      </p>

      <div className="flex gap-3 flex-wrap">

        <span className="bg-indigo-50 text-indigo-700 px-3 py-1 rounded-full text-sm flex items-center gap-1">
          <Users size={14} />
          {contributors} Contributors
        </span>

        <span className="bg-green-50 text-green-700 px-3 py-1 rounded-full text-sm flex items-center gap-1">
          <CircleDot size={14} />
          {issues} Issues
        </span>

        <span className="bg-blue-50 text-blue-700 px-3 py-1 rounded-full text-sm flex items-center gap-1">
          <GitCommit size={14} />
          {commits} Commits
        </span>

      </div>

      <div className="mt-6 flex justify-between text-sm text-slate-500">
        <span>Created May 4, 2025</span>
        <span>Updated May 4, 2025</span>
      </div>

    </div>
  );
}