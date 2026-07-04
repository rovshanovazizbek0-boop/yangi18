import Link from "next/link";
import { apiGet } from "../lib/api";

export default async function Header() {
  const categories = (await apiGet("/api/categories")) || [];

  return (
    <header className="border-b border-slate-800">
      <div className="mx-auto flex max-w-6xl flex-col gap-3 px-4 py-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <Link href="/" className="text-xl font-bold">
            🤖 AI News <span className="text-blue-400">Uzbekistan</span>
          </Link>
          <form action="/qidiruv" className="flex gap-2">
            <input
              name="q"
              placeholder="Qidiruv..."
              className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-1.5 text-sm outline-none focus:border-blue-500"
            />
            <button className="rounded-lg bg-blue-600 px-3 py-1.5 text-sm hover:bg-blue-500">
              🔍
            </button>
          </form>
        </div>
        <nav className="flex flex-wrap gap-2 text-sm">
          {categories.map((cat) => (
            <Link
              key={cat.slug}
              href={`/kategoriya/${cat.slug}`}
              className="rounded-full border border-slate-700 px-3 py-1 text-slate-300 hover:border-blue-500 hover:text-white"
            >
              {cat.name}
            </Link>
          ))}
        </nav>
      </div>
    </header>
  );
}
