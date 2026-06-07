"use client";

import { useEffect, useState } from "react";
import { getRepoGraph } from "@/src/lib/api";
import RepositoryNode from "./graph/RepositoryNode";
import TopicNode from "./graph/TopicNode";
import ContributorNode from "./graph/ContributorNode";
import ReactFlow, {
  useReactFlow,
  Controls,
  Background,
  useNodesInitialized,
} from "reactflow";
import "reactflow/dist/style.css";
import { layout } from "@/src/lib/graphLayout";

const nodeTypes = {
  repository: RepositoryNode,
  topic: TopicNode,
  contributor: ContributorNode,
};

export default function GraphView({ repoId, maxContributors = 25 }: { repoId: number; maxContributors?: number }) {
  const [fullData, setFullData] = useState<any>({ nodes: [], links: [] });
  const [data, setData] = useState<any>({ nodes: [], links: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
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
        setFullData(d);
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
    if (!fullData?.nodes?.length) return;
    setData(fullData);
  }, [fullData, maxContributors]);

  if (!mounted) {
    return <div className="h-[700px] rounded-2xl border border-slate-200 flex items-center justify-center">Loading graph…</div>;
  }

  if (loading) {
    return <div className="h-[700px] rounded-2xl border border-dashed border-slate-200 flex items-center justify-center">Loading graph…</div>;
  }

  if (error) {
    return <div className="h-[700px] rounded-2xl border border-dashed border-slate-200 flex items-center justify-center text-red-600">{error}</div>;
  }

  const reactFlowNodes =
    data.nodes?.map((node: any) => ({
      id: node.id,

      type: node.type,

      data: {
        label: node.label,
      },

      position: {
        x: 0,
        y: 0,
      },
    })) || [];

  const reactFlowEdges =
    data.links?.map((link: any, index: number) => ({

      id: `e-${index}`,

      source:
        typeof link.source === "object"
          ? link.source.id
          : link.source,

      target:
        typeof link.target === "object"
          ? link.target.id
          : link.target,

      type: "smoothstep",

      style: {
        stroke: "#CBD5E1",
        strokeWidth: 2,
      },

      animated: false,
    })) || [];

  const positionedNodes = layout(
    reactFlowNodes,
    reactFlowEdges
  );

  const handleInit = (instance: any) => {
    const repoNode = positionedNodes.find(
      (n) => n.type === "repository"
    );

    if (!repoNode) return;

    instance.setCenter(
      repoNode.position.x + 400,
      repoNode.position.y + 50,
      {
        zoom: 0.65,
        duration: 0,
      }
    );
  };

  return (
    <div className="h-[500px] w-full rounded-2xl bg-slate-50 border border-slate-100">
      <ReactFlow
        nodes={positionedNodes}
        edges={reactFlowEdges}
        nodeTypes={nodeTypes}
        onInit={handleInit}

        nodesDraggable={true}
        nodesConnectable={false}
        elementsSelectable={true}
        zoomOnScroll={true}
        zoomOnPinch={true}
        panOnDrag={true}
      >
        <Background />
        <Controls />
      </ReactFlow>
    </div>
  );
}
