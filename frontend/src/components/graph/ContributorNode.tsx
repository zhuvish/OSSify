import { Handle, Position } from "reactflow";

export default function ContributorNode({ data }: any) {
    return (
        <>
            <Handle type="target" position={Position.Top} />
            <div className="
      px-4
      py-3
      bg-emerald-400
      border
      border-emerald-200
      rounded-xl
      shadow-sm
      min-w-[140px]
      text-center
      font-medium
    ">
                👤 {data.label}
            </div>
            <Handle type="source" position={Position.Bottom} />
        </>
    );
}