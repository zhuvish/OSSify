import { LucideIcon } from "lucide-react";

interface Props {
  icon: LucideIcon;
  value: number;
  title: string;
  iconBg: string;
  iconColor: string;
}

export default function StatCard({
  icon: Icon,
  value,
  title,
  iconBg,
  iconColor
}: Props) {
  return (
    <div className="bg-white rounded-xl px-4 py-2 shadow-sm">

      <div className="flex items-center gap-3">

        <div className="w-10 h-10 rounded-full bg-slate-100 flex items-center justify-center ${iconBg}">
          <Icon size={24} strokeWidth={1.8}
          className={iconColor}/>
        </div>

        <div>
          <h3 className="text-xl font-bold">
            {value}
          </h3>

          <p className="text-md text-slate-500">
            {title}
          </p>
        </div>

      </div>
    </div>
  );
}