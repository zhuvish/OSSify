export default function ContributorProfile() {
  return (
    <div className="space-y-6">

      {/* Header */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6">

        <div className="flex items-center gap-5">

          <div className="h-20 w-20 rounded-full bg-indigo-100 flex items-center justify-center text-3xl font-bold text-indigo-700">
            D
          </div>

          <div>
            <h1 className="text-3xl font-bold text-slate-900">
              davidism
            </h1>

            <p className="text-slate-500">
              github.com/davidism
            </p>

            <div className="flex gap-3 mt-3">

              <span className="px-3 py-1 rounded-full bg-indigo-100 text-indigo-700 text-sm">
                42 Commits
              </span>

              <span className="px-3 py-1 rounded-full bg-green-100 text-green-700 text-sm">
                3 Repositories
              </span>

              <span className="px-3 py-1 rounded-full bg-purple-100 text-purple-700 text-sm">
                5 Expertise Areas
              </span>

            </div>
          </div>

        </div>
      </div>

      {/* Summary */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6">

        <h2 className="text-xl font-semibold mb-4">
          Contributor Summary
        </h2>

        <p className="text-slate-600 leading-7">
          David demonstrates strong expertise in Flask's
          authentication system, session handling and
          security-related modules. Their contributions
          focus heavily on backend infrastructure and
          framework internals, making them a key
          contributor for authentication workflows.
        </p>

      </div>

      {/* Two-column section */}
      <div className="grid grid-cols-3 gap-6">

        {/* Repository Contributions */}
        <div className="col-span-2 bg-white rounded-2xl border border-slate-200 p-6">

          <h2 className="text-xl font-semibold mb-4">
            Repository Contributions
          </h2>

          <ul className="space-y-4">

            <li>
              <p className="font-medium">Flask</p>
              <p className="text-slate-500 text-sm">
                Authentication and session management
              </p>
            </li>

            <li>
              <p className="font-medium">Werkzeug</p>
              <p className="text-slate-500 text-sm">
                Routing and request lifecycle
              </p>
            </li>

            <li>
              <p className="font-medium">Jinja</p>
              <p className="text-slate-500 text-sm">
                Template rendering improvements
              </p>
            </li>

          </ul>

        </div>

        {/* Recent Activity */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6">

          <h2 className="text-xl font-semibold mb-4">
            Recent Activity
          </h2>

          <div className="space-y-4">

            <div>
              <p className="font-medium">
                Fixed auth bug
              </p>
              <p className="text-sm text-slate-500">
                2 hours ago
              </p>
            </div>

            <div>
              <p className="font-medium">
                Added middleware
              </p>
              <p className="text-sm text-slate-500">
                Yesterday
              </p>
            </div>

            <div>
              <p className="font-medium">
                Refactored routing
              </p>
              <p className="text-sm text-slate-500">
                3 days ago
              </p>
            </div>

          </div>

        </div>

      </div>

      {/* Expertise */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6">

        <h2 className="text-xl font-semibold mb-4">
          Expertise
        </h2>

        <div className="flex flex-wrap gap-3">

          <span className="px-4 py-2 rounded-full bg-indigo-100 text-indigo-700">
            Authentication
          </span>

          <span className="px-4 py-2 rounded-full bg-purple-100 text-purple-700">
            Sessions
          </span>

          <span className="px-4 py-2 rounded-full bg-red-100 text-red-700">
            Security
          </span>

          <span className="px-4 py-2 rounded-full bg-green-100 text-green-700">
            Flask Core
          </span>

        </div>

      </div>

      {/* Graph */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6">

        <h2 className="text-xl font-semibold mb-4">
          Repository Connections
        </h2>

        <div className="h-[350px] rounded-xl border-2 border-dashed border-slate-200 flex items-center justify-center">
          Graph Visualization Here
        </div>

      </div>

    </div>
  );
}