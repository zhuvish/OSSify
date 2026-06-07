import { Handle, Position } from "reactflow";

export default function TopicNode({ data }: any) {
    return (
        <>
            <Handle type="target" position={Position.Top} />
            <div className="
      px-5
      py-3
      bg-blue-50
      border
      border-blue-200
      rounded-xl
      shadow-sm
      text-blue-700
      font-semibold
      min-w-[180px]
      text-center
      text-lg
    ">
                {data.label}
            </div>
            <Handle type="source" position={Position.Bottom} />
        </>
    );
}