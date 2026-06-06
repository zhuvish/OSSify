"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { analyzeRepo } from "@/src/lib/api";

export default function Home() {
  const [repoUrl, setRepoUrl] = useState("");
  const [loading, setLoading] = useState(false);

  const router = useRouter();

  async function handleAnalyze() {
    try {
      setLoading(true);

      const result = await analyzeRepo(repoUrl);
      localStorage.setItem(
        "selected_repo_id",
        result.repo_id
      );

      localStorage.setItem(
        "selected_repo_name",
        result.repo_name
      );

      if (result.cached) {
        router.push("/dashboard");
        return;
      }

      router.push("/loading");
    } catch (error) {
      if (error instanceof Error) {
        alert(error.message);
      } else {
        alert("Unexpected error occurred.");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen flex items-center justify-center">
      <div className="w-full max-w-xl text-center">
        <h1 className="text-5xl font-bold mb-4">
          OSSify 🚀
        </h1>

        <p className="text-gray-500 mb-8">
          Discover contributors, expertise and repository knowledge.
        </p>

        <input
          value={repoUrl}
          onChange={(e) => setRepoUrl(e.target.value)}
          placeholder="https://github.com/pallets/flask"
          className="w-full border rounded-xl p-4"
        />

        <button
          onClick={handleAnalyze}
          disabled={loading}
          className="mt-4 w-full bg-black text-white p-4 rounded-xl"
        >
          {loading ? "Analyzing..." : "Analyze Repository"}
        </button>
      </div>
    </main>
  );
}