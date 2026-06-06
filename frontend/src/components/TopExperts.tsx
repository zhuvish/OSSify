import { Crown } from "lucide-react";

interface Props {
  experts: any[];
}

export default function TopExperts({
  experts,
}: Props) {
  return (
    <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm ml-6">

      <div className="flex justify-between items-center mb-4">

        <div className="flex items-center gap-2">
          <Crown
            size={24}
            strokeWidth={1.5}
            className="text-violet-500"
          />

          <h2 className="text-lg font-semibold">
            Top Contributors
          </h2>
        </div>

        <button
          className="
      text-xs
      text-violet-600
      hover:text-violet-700
    "
        >
          View all →
        </button>

      </div>

      <div className="space-y-3">

        {experts.map((expert, index) => (
          <div
            key={expert.id}
            className="
      flex items-center justify-between
      py-3
      border-b border-slate-100
      last:border-b-0
    "
          >
            <div className="flex items-center gap-3">

              {expert.avatar_url ? (
                <img
                  src={expert.avatar_url}
                  alt={expert.username}
                  className="w-12 h-12 rounded-full object-cover"
                />
              ) : (
                <div className="w-12 h-12 rounded-full bg-indigo-100 text-indigo-700 flex items-center justify-center font-bold">
                  {expert.username[0]?.toUpperCase()}
                </div>
              )}

              <div>
                <p className="font-medium text-sm">
                  {expert.username.toLowerCase()}
                </p>

                <div className="flex gap-2 mt-1">
                  {(expert.topics || [])
                    .slice(0, 2)
                    .map((topic: string) => (
                      <span
                        key={topic}
                        className="
                        px-2 py-0.5
                        text-[10px]
                        rounded-full
                        bg-violet-50
                        text-violet-700
                        border border-violet-100
                      "
                      >
                        {topic}
                      </span>
                    ))}
                </div>
              </div>

            </div>

            <div className="text-right">
              <p className="font-semibold">
                {Math.round(expert.score)}
              </p>

              <p className="text-xs text-slate-400">
                #{index + 1}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}