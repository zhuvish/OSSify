"use client";

import dynamic from "next/dynamic";
import { useEffect, useRef, useState } from "react";
import { getRepoGraph } from "@/src/lib/api";

const ForceGraph2D = dynamic(() => import("react-force-graph").then((m) => m.ForceGraph2D), {
  ssr: false,
});

export default function GraphView({ repoId }: { repoId: number }) {
  const [data, setData] = useState<any>({ nodes: [], links: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const fgRef = useRef<any>(null);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    return () => setMounted(false);
  }, []);

  useEffect(() => {
    let active = true;
    setLoading(true);

    getRepoGraph(repoId)
      .then((d) => {
        if (!active || !mounted) return;
        setData(d);
      })
      .catch((e) => {
        if (!active || !mounted) return;
        setError(e instanceof Error ? e.message : String(e));
      })
      .finally(() => {
        if (!active || !mounted) return;
        setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [repoId, mounted]);

  if (!mounted) {
    return <div className="h-[600px] rounded-xl border-2 border-slate-200 flex items-center justify-center">Loading graph…</div>;
  }

  if (loading) {
    return <div className="h-[600px] rounded-xl border-2 border-dashed border-slate-200 flex items-center justify-center">Loading graph…</div>;
  }

  if (error) {
    return <div className="h-[600px] rounded-xl border-2 border-dashed border-slate-200 flex items-center justify-center text-red-600">{error}</div>;
  }

  return (
    <div className="h-[600px] rounded-xl border-2 border-slate-200">
      <ForceGraph2D
        ref={fgRef}
        graphData={data}
        nodeLabel={(n: any) => n.label}
        nodeAutoColorBy={(n: any) => n.type}
        linkDirectionalArrowLength={3}
        linkDirectionalArrowRelPos={0.9}
        onNodeHover={(node: any) => {
          // optional: could show tooltip via state
        }}
        nodeCanvasObject={(node: any, ctx: CanvasRenderingContext2D, globalScale: number) => {
          const label = node.label;
          const fontSize = 12 / (globalScale || 1);
          ctx.fillStyle = node.type === "repository" ? "#111827" : node.type === "contributor" ? "#0ea5a4" : "#3b82f6";
          ctx.beginPath();
          ctx.arc(node.x, node.y, 6, 0, 2 * Math.PI, false);
          ctx.fill();

          ctx.font = `${fontSize}px Sans-Serif`;
          ctx.fillStyle = "#111827";
          ctx.textAlign = "left";
          ctx.textBaseline = "middle";
          ctx.fillText(label, node.x + 8, node.y);
        }}
        enableNodeDrag={true}
        zoom={1}
      />
    </div>
  );
}
