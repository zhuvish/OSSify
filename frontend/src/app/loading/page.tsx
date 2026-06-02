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

  useEffect(() => {
    if (!repoId) return;

    let mounted = true;

    async function check() {
      try {
        const res = await getRepoStatus(repoId);
        if (!mounted) return;

        setStatus(res.status);

        if (res.status === "ready") {
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

  function stepIcon() {
    if (status === "ready") return "✓";
    if (status === "failed") return "✕";
    return "...";
  }

  return (
    <main className="min-h-screen flex items-center justify-center bg-slate-100">
      <div className="w-full max-w-2xl bg-white rounded-xl p-8 shadow">
        <h2 className="text-xl font-semibold mb-4">Analyzing Repository</h2>

        <p className="text-sm text-slate-500 mb-6">
          Processing repository — this can take a few minutes. This page will update automatically.
        </p>

        <div className="space-y-3">
          {["Fetching Repository Data","Loading PostgreSQL","Building Knowledge Graph","Generating Embeddings","Building Contributor Profiles"].map((title, i) => (
            <div key={i} className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className="w-8 h-8 flex items-center justify-center rounded-full bg-slate-100">{stepIcon()}</span>
                <div>
                  <div className="font-medium">{title}</div>
                </div>
              </div>
              <div className="text-sm text-slate-400">{status === "ready" ? "Done" : status === "failed" ? "Failed" : i === 0 ? "Starting" : "Pending"}</div>
            </div>
          ))}
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