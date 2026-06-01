export default function Home() {
  return (
    <main className="min-h-screen flex items-center justify-center">
      <div className="w-full max-w-xl text-center">
        <h1 className="text-5xl font-bold mb-4">
          OSSify 🚀
        </h1>

        <p className="text-gray-500 mb-8">
          Discover contributors, expertise and repository knowledge.
        </p>

        <input
          className="w-full border rounded-lg p-4"
          placeholder="https://github.com/pallets/flask"
        />

        <button
          className="mt-4 w-full bg-black text-white p-4 rounded-lg"
        >
          Analyze Repository
        </button>
      </div>
    </main>
  )
}