"use client";

import { useEffect, useState } from "react";
import ReactFlow, {
    Background,
    Controls,
} from "reactflow";

import "reactflow/dist/style.css";

import RepositoryNode from "./graph/RepositoryNode";
import TopicNode from "./graph/TopicNode";
import ContributorNode from "./graph/ContributorNode";

import { layout } from "@/src/lib/graphLayout";
import { getContributorGraph } from "@/src/lib/contributors";

const nodeTypes = {
    repository: RepositoryNode,
    topic: TopicNode,
    contributor: ContributorNode,
};

export default function ContributorGraph({
    contributorId
}: {
    contributorId: number;
}) {

    const [data, setData] = useState<any>({
        nodes: [],
        links: [],
    });

    useEffect(() => {

        async function load() {

            const graph =
                await getContributorGraph(
                    contributorId
                );

            setData(graph);
        }

        load();

    }, [contributorId]);

    const nodes =
        data.nodes.map((node: any) => ({
            id: node.id,
            type: node.type,
            data: {
                label: node.label,
            },
            position: {
                x: 0,
                y: 0,
            },
        }));

    const edges =
        data.links.map(
            (
                link: any,
                index: number
            ) => ({
                id: `e-${index}`,
                source: link.source,
                target: link.target,
            })
        );

    const positionedNodes =
        layout(nodes, edges);

    return (
        <div className="h-full w-full">

            <ReactFlow
                nodes={positionedNodes}
                edges={edges}
                nodeTypes={nodeTypes}
            >
                <Background />
                <Controls />
            </ReactFlow>

        </div>
    );
}