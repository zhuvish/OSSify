import { Crown } from "lucide-react";

interface Props {
  experts: any[];
}

export default function TopExperts({
  experts,
}: Props) {
  return (
    <div className="bg-white rounded-3xl p-6 border border-slate-200">

      {/* <h2 className="text-3xl font-bold mb-2">
        Top Experts
      </h2> */}

      <div className="flex items-center gap-3 mb-2">
        <Crown className="text-violet-500" />
        <h2 className="text-3xl font-bold">
            Top Experts
        </h2>
      </div>

      <p className="text-slate-500 mb-6">
        Top contributors by expertise
      </p>

      <div className="space-y-5">

        {experts.map((expert, index) => (
          <div
            key={expert.id}
            className="border rounded-2xl p-5 shadow-sm hover:shadow-md transition"
          >
            <div className="flex justify-between">

              <div className="flex gap-4">

                <div className="h-12 w-12 rounded-full bg-violet-100 text-violet-700 flex items-center justify-center font-bold">
                  {expert.username[0]?.toUpperCase()}
                </div>

                <div>
                  <div className="flex items-center gap-2">
                    <p className="font-semibold">
                      {expert.username}
                    </p>
                    <span className="text-xs text-slate-500">#{index + 1}</span>
                  </div>

                  <div className="flex flex-wrap gap-2 mt-2">
                    {(expert.topics || [])
                      .slice(0, 2)
                      .map((topic: string) => (
                        <span
                          key={topic}
                          className="px-2 py-1 rounded-full bg-blue-100 text-blue-700 text-xs"
                        >
                          {topic}
                        </span>
                      ))}
                  </div>
                </div>

              </div>

              <div className="text-right">
                <div className="text-2xl font-bold">
                  {Math.round(expert.score)}
                </div>

                <div className="text-xs text-slate-500">
                  Expertise Score
                </div>
              </div>

            </div>

            <div className="mt-4 h-2 rounded-full bg-slate-100">
              <div
                className="h-2 rounded-full bg-violet-500"
                style={{
                  width: `${Math.min(expert.score, 100)}%`,
                }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}