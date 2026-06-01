import Link from "next/link";

export default function ContributorsPage() {
  const contributors = [
    {
      id: 1,
      name: "davidism",
      expertise: ["Authentication", "Sessions"],
      commits: 42,
      repos: 3,
    },
    {
      id: 2,
      name: "pgjones",
      expertise: ["Routing", "Flask Core"],
      commits: 38,
      repos: 2,
    },
    {
      id: 3,
      name: "justquick",
      expertise: ["Security", "Sessions"],
      commits: 29,
      repos: 1,
    },
    {
      id: 4,
      name: "mitsuhiko",
      expertise: ["Jinja", "Werkzeug"],
      commits: 51,
      repos: 4,
    },
  ];

  return (
    <div>
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-4xl font-bold text-slate-900">
          Contributors
        </h1>

        <input
          placeholder="Search contributors..."
          className="w-80 rounded-xl border border-slate-300 bg-white px-4 py-3 outline-none"
        />
      </div>

      {/* Contributors List */}
      <div className="space-y-4">
        {contributors.map((c) => (
          <Link
            key={c.id}
            href={`/contributors/${c.id}`}
            className="block"
          >
            <div className="bg-white border border-slate-200 rounded-2xl p-6 hover:shadow-md transition">
              <div className="flex justify-between items-center">

                <div className="flex items-center gap-4">

                  <div className="h-14 w-14 rounded-full bg-indigo-100 text-indigo-700 flex items-center justify-center font-bold text-lg">
                    {c.name[0].toUpperCase()}
                  </div>

                  <div>
                    <h2 className="text-lg font-semibold text-slate-900">
                      {c.name}
                    </h2>

                    <div className="flex gap-2 mt-2">
                      {c.expertise.map((skill) => (
                        <span
                          key={skill}
                          className="px-3 py-1 rounded-full bg-indigo-100 text-indigo-700 text-xs"
                        >
                          {skill}
                        </span>
                      ))}
                    </div>

                    <p className="mt-3 text-sm text-slate-500">
                      {c.commits} commits • {c.repos} repositories
                    </p>
                  </div>

                </div>

                <div className="text-2xl text-slate-400">
                  →
                </div>

              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}