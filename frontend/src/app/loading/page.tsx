"use client";

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { getRepoStatus } from "@/src/lib/api";

export default function LoadingPage() {
  const router = useRouter();
  const search = useSearchParams();

  const [repoId, setRepoId] = useState<number | null>(null);
  const [status, setStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [stage, setStage] = useState<string | null>(null);

  useEffect(() => {
    const q = search?.get("repo_id");
    if (q) {
      setRepoId(Number(q));
      return;
    }

    const stored = typeof window !== 'undefined' ? localStorage.getItem("selected_repo_id") : null;
    if (stored) {
      setRepoId(Number(stored));
    }
  }, [search]);

  const stages = [
    "fetching_metadata",
    "fetching_contributors",
    "fetching_prs",
    "fetching_issues",
    "computing_expertise",
    "building_graph",
    "building_embeddings",
  ];

  useEffect(() => {
    let mounted = true;

    async function check() {
      try {
        if (!repoId) return;
        const res = await getRepoStatus(repoId);
        if (!mounted) return;

        setStatus(res.status);
        setStage(res.stage);

        if (
          res.status === "ready" ||
          res.status === "success" ||
          res.status === "completed"
        ) {
          router.push("/dashboard");
        }

        if (res.status === "failed") {
          setError("Repository processing failed. Check server logs.");
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unknown error");
      }
    }

    check();

    const iv = setInterval(check, 5000);

    return () => {
      mounted = false;
      clearInterval(iv);
    };
  }, [repoId, router]);

  function getStepStatus(step: string) {
    if (status === "failed") return "failed";
    if (status === "ready") return "done";

    const current = stages.indexOf(stage || "");
    const target = stages.indexOf(step);

    if (target < current) return "done";
    if (target === current) return "active";

    return "pending";
  }

  const steps = [
    {
      title: "Fetching Repository Metadata",
      stage: "fetching_metadata",
    },
    {
      title: "Fetching Contributors",
      stage: "fetching_contributors",
    },
    {
      title: "Fetching PRs",
      stage: "fetching_prs",
    },
    {
      title: "Fetching Issues",
      stage: "fetching_issues",
    },
    {
      title: "Computing Expertise",
      stage: "computing_expertise",
    },
    {
      title: "Building Knowledge Graph",
      stage: "building_graph",
    },
    {
      title: "Generating Embeddings",
      stage: "building_embeddings",
    },
  ];

  return (
    <main className="min-h-screen flex items-center justify-center bg-slate-100">
      <div className="w-full max-w-2xl bg-white rounded-xl p-8 shadow">
        <h2 className="text-xl font-semibold mb-4">Analyzing Repository</h2>

        <p className="text-sm text-slate-500 mb-6">
          Processing repository — this can take a few minutes. This page will update automatically.
        </p>

        <div className="space-y-3">
          {steps.map((step) => {
            const state = getStepStatus(step.stage);

            return (
              <div
                key={step.stage}
                className="flex items-center justify-between"
              >
                <div className="flex items-center gap-3">

                  <span className="w-8 h-8 flex items-center justify-center rounded-full bg-slate-100">

                    {state === "done" && "✓"}

                    {state === "active" && "⏳"}

                    {state === "pending" && "..."}

                    {state === "failed" && "✕"}

                  </span>

                  <div>
                    <div className="font-medium">
                      {step.title}
                    </div>
                  </div>
                </div>

                <div className="text-sm text-slate-400">
                  {state === "done" && "Done"}

                  {state === "active" && "In Progress"}

                  {state === "pending" && "Pending"}

                  {state === "failed" && "Failed"}
                </div>
              </div>
            );
          })}
        </div>

        {error && (
          <div className="mt-6 text-sm text-red-600">{error}</div>
        )}

        <div className="mt-6 flex justify-end">
          <button
            onClick={() => router.push("/")}
            className="px-4 py-2 rounded bg-slate-100 text-slate-700"
          >
            Back
          </button>
        </div>
      </div>
    </main>
  );
}