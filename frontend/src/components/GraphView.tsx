"use client";

import dynamic from "next/dynamic";
import { useEffect, useRef, useState } from "react";
import { getRepoGraph } from "@/src/lib/api";

const ForceGraph2D = dynamic(
  () => import("react-force-graph-2d"),
  {
    ssr: false,
  }
);

export default function GraphView({ repoId }: { repoId: number }) {
  const [data, setData] = useState<any>({ nodes: [], links: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const fgRef = useRef<any>(null);
  const [mounted, setMounted] = useState(false);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [width, setWidth] = useState<number>(800);
  const height = 650;

  useEffect(() => {
    setMounted(true);
    return () => setMounted(false);
  }, []);

  useEffect(() => {
    function updateWidth() {
      if (containerRef.current) setWidth(containerRef.current.clientWidth);
    }
    updateWidth();
    window.addEventListener('resize', updateWidth);
    return () => window.removeEventListener('resize', updateWidth);
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

  useEffect(() => {
    if (!fgRef.current || !data?.nodes?.length) return;

    const charge = fgRef.current.d3Force("charge");

    if (charge) {
      charge.strength(-500);
    }

    const link = fgRef.current.d3Force("link");

    if (link) {
      link.distance(140);
    }
  }, [data]);

  if (!mounted) {
    return <div className="h-[700px] rounded-2xl border border-slate-200 flex items-center justify-center">Loading graph…</div>;
  }

  if (loading) {
    return <div className="h-[700px] rounded-2xl border border-dashed border-slate-200 flex items-center justify-center">Loading graph…</div>;
  }

  if (error) {
    return <div className="h-[700px] rounded-2xl border border-dashed border-slate-200 flex items-center justify-center text-red-600">{error}</div>;
  }

  return (
    <div ref={containerRef} className="
      h-[700px]
      w-full
      rounded-2xl
      border
      border-slate-200
      overflow-hidden
      bg-white
    ">
      <ForceGraph2D
        ref={fgRef}
        width={width}
        height={height}
        graphData={data}
        nodeLabel={(n: any) => n.label}
        nodeAutoColorBy={(n: any) => n.type}
        linkDirectionalArrowLength={0}
        linkColor={() => "#CBD5E1"}
        linkWidth={1}
        nodeRelSize={12}
        cooldownTicks={500}
        d3VelocityDecay={0.15}
        onEngineStop={() => fgRef.current?.zoomToFit(800, 50)}
        onNodeHover={(node: any) => {
          // optional: could show tooltip via state
        }}
        // nodeCanvasObject={(node: any, ctx: CanvasRenderingContext2D, globalScale: number) => {
        //   const label = node.label;
        //   const fontSize = 12 / (globalScale || 1);
        //   ctx.fillStyle = node.type === "repository" ? "#111827" : node.type === "contributor" ? "#0ea5a4" : "#3b82f6";
        //   ctx.beginPath();
        //   ctx.arc(node.x, node.y, 6, 0, 2 * Math.PI, false);
        //   ctx.fill();

        //   ctx.font = `${fontSize}px Sans-Serif`;
        //   ctx.fillStyle = "#111827";
        //   ctx.textAlign = "left";
        //   ctx.textBaseline = "middle";
        //   ctx.fillText(label, node.x + 8, node.y);
        // }}
        nodeCanvasObject={(node: any, ctx, globalScale) => {
          const label = node.label;

          const fontSize = Math.max(10 / globalScale, 2);

          const color =
            node.type === "repository"
              ? "#111827"
              : node.type === "topic"
              ? "#2563eb"
              : node.type === "file"
              ? "#8b5cf6"
              : "#14b8a6";

          const radius =
            node.type === "repository"
              ? 18
              : node.type === "topic"
              ? 10
              : node.type === "file"
              ? 8
              : 6;

          ctx.beginPath();
          ctx.arc(node.x, node.y, radius, 0, 2 * Math.PI);
          ctx.fillStyle = color;
          ctx.fill();

          ctx.font = `${fontSize}px Sans-Serif`;
          ctx.fillStyle = "#111827";

          if (globalScale > 1.5) {
            ctx.fillText(
              label,
              node.x + radius + 4,
              node.y
            );
          }
        }}
        enableNodeDrag={true}
      />
    </div>
  );
}
