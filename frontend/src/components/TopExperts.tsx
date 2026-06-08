"use client";

import { useRouter } from "next/navigation";
import { Crown, ArrowRight, Users } from "lucide-react";

interface Props {
  experts: any[];
}

export default function TopExperts({
  experts,
}: Props) {
  const router = useRouter();

  return (
    <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm ml-6 h-full flex flex-col">

      <div className="flex items-center gap-2 mb-4">
        <Crown
          size={24}
          strokeWidth={1.5}
          className="text-violet-500"
        />
        <h2 className="text-lg font-semibold">
          Top Contributors
        </h2>
      </div>

      <div className="space-y-3 flex-1">
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

      {/* Spacer pushes button to bottom */}
      <div className="mt-auto pt-4">
        <button
          onClick={() => router.push("/contributors")}
          className="w-full flex items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm font-medium text-slate-700 hover:bg-slate-50 hover:border-violet-300 hover:text-violet-700 transition"
        >
          <Users size={16} />
          View all contributors
          <ArrowRight size={16} />
        </button>
      </div>
    </div>
  );
}
