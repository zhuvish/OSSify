import dagre from "dagre";
import { Position } from "reactflow";

const dagreGraph = new dagre.graphlib.Graph();

dagreGraph.setDefaultEdgeLabel(() => ({}));

export function layout(nodes: any[], edges: any[]) {

    dagreGraph.setGraph({
        rankdir: "LR",
        ranksep: 140,
        nodesep: 100,
    });

    nodes.forEach((node) => {

    let width = 150;
    let height = 50;

    if (node.type === "repository") {
      width = 280;
      height = 80;
    }

    if (node.type === "topic") {
      width = 180;
      height = 60;
    }

    if (node.type === "contributor") {
      width = 160;
      height = 60;
    }

    dagreGraph.setNode(node.id, {
      width,
      height,
    });
  });

    edges.forEach((edge) => {
        dagreGraph.setEdge(
            edge.source,
            edge.target
        );
    });

    dagre.layout(dagreGraph);

    return nodes.map((node) => {

    const pos = dagreGraph.node(node.id);

    let width = 150;
    let height = 50;

    if (node.type === "repository") {
      width = 280;
      height = 80;
    }

    if (node.type === "topic") {
      width = 180;
      height = 60;
    }

    if (node.type === "contributor") {
      width = 160;
      height = 60;
    }

    return {
      ...node,

      position: {
        x: pos.x - width / 2,
        y: pos.y - height / 2,
      },

      sourcePosition: Position.Bottom,
      targetPosition: Position.Top,
    };
  });
}