import { Handle, Position } from "reactflow";

export default function RepositoryNode({ data }: any) {
    return (
        <>
            <Handle type="target" position={Position.Top} />
            <div className="
        min-w-[260px]
        px-8
        py-5
        bg-slate-900
        text-white
        rounded-2xl
        shadow-lg
        font-bold
        text-center
        text-xl
    ">
                📦 {data.label}
            </div>
            <Handle type="source" position={Position.Bottom} />
        </>
    );
}