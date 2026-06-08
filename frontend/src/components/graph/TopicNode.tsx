import { Handle, Position } from "reactflow";

export default function TopicNode({ data }: any) {
    return (
        <>
            <Handle type="target" position={Position.Top} />
            <div className="
      px-5
      py-3
      bg-blue-400
      border
      border-blue-700
      rounded-xl
      shadow-sm
      font-semibold
      min-w-[180px]
      text-center
      text-lg
    ">
            📃 {data.label}
            </div>
            <Handle type="source" position={Position.Bottom} />
        </>
    );
}