import RepositoryCard from "@/src/components/RepositoryCard";
import Sidebar from "@/src/components/Sidebar";

export default function RepositoriesPage() {
  return (
    <div className="ml-5 mr-5  space-y-8">

      <div className="flex justify-between items-center">

        <div>
          <h1 className="text-2xl font-bold">
            Repositories
          </h1>
        </div>

        <input
          placeholder="Search repositories..."
          className="
            bg-white
            border
            border-slate-300
            rounded-xl
            px-4
            py-2
            w-72
          "
        />
      </div>

      <div className="grid grid-cols-2 gap-6">

        <RepositoryCard
          name="pallets/flask"
          url="github.com/pallets/flask"
          contributors={67}
          commits={183}
          issues={7}
        />

        <RepositoryCard
          name="django/django"
          url="github.com/django/django"
          contributors={52}
          commits={142}
          issues={11}
        />

      </div>

    </div>
  );
}