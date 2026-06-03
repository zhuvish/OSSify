import { LucideIcon } from "lucide-react";

interface Props {
  icon: LucideIcon;
  value: number;
  title: string;
  subtitle: string;
}

export default function StatCard({
  icon: Icon,
  value,
  title,
  subtitle,
}: Props) {
  return (
    <div className="bg-white rounded-3xl p-6 shadow-sm">

      <div className="flex items-center gap-4">

        <div className="h-16 w-16 rounded-full bg-slate-100 flex items-center justify-center">
          <Icon size={28} />
        </div>

        <div>
          <h3 className="text-5xl font-bold">
            {value}
          </h3>

          <p className="font-medium">
            {title}
          </p>

          <p className="text-sm text-slate-500">
            {subtitle}
          </p>
        </div>

      </div>
    </div>
  );
}