import Link from "next/link";
import Image from "next/image";
import { unstable_rethrow } from "next/navigation";
import { apiGet } from "../lib/api";

export default async function Header() {
  // Backend vaqtincha ishlamasa statik sahifalar ham yiqilib ketmasin.
  // Kontent sahifalarining o'zi API xatosini yashirmay error boundary'ga beradi.
  let categories = [];
  let hasTools = false;
  try {
    categories = (await apiGet("/api/categories")) || [];
  } catch (error) {
    unstable_rethrow(error);
    console.error("Header kategoriyalarini olib bo'lmadi:", error);
  }
  try {
    hasTools = ((await apiGet("/api/tools")) || []).length > 0;
  } catch (error) {
    unstable_rethrow(error);
    console.error("Header vositalarini olib bo'lmadi:", error);
  }

  return (
    <header className="border-b border-slate-800">
      <div className="mx-auto flex max-w-6xl flex-col gap-3 px-4 py-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <Link href="/" className="flex items-center gap-2 text-xl font-bold">
            <Image src="/logo.svg" alt="AI Xabar logotipi" width={36} height={36} priority />
            <span>
              AI <span className="text-blue-400">Xabar</span>
            </span>
          </Link>
          <div className="flex w-full flex-wrap items-center gap-3 sm:w-auto sm:gap-4">
            <Link
              href="/organish"
              className="flex items-center gap-1.5 text-sm font-semibold text-emerald-400 transition-colors hover:text-emerald-300"
            >
              🎓 AI&apos;ni o&apos;rganish
            </Link>
            {hasTools && (
              <Link
                href="/vositalar"
                className="flex items-center gap-1.5 text-sm text-slate-300 transition-colors hover:text-blue-400"
              >
                🧰 AI vositalari
              </Link>
            )}
            <a
              href="https://t.me/aixabarlari"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1.5 text-sm text-slate-300 hover:text-sky-400 transition-colors"
            >
              📢 Telegram Kanal
            </a>
            <a
              href="https://t.me/Ainewsuzbek_bot"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1.5 text-sm text-slate-300 hover:text-blue-400 transition-colors"
            >
              🤖 Telegram Bot
            </a>
            <form action="/qidiruv" className="flex w-full gap-2 sm:w-auto">
              <label htmlFor="site-search" className="sr-only">Saytdan qidirish</label>
              <input
                id="site-search"
                name="q"
                placeholder="Qidiruv..."
                className="min-w-0 flex-1 rounded-lg border border-slate-700 bg-slate-900 px-3 py-1.5 text-sm outline-none focus:border-blue-500 sm:flex-none"
              />
              <button aria-label="Qidirish" className="rounded-lg bg-blue-600 px-3 py-1.5 text-sm hover:bg-blue-500">
                🔍
              </button>
            </form>
          </div>
        </div>

        <nav className="hidden flex-wrap gap-2 text-sm sm:flex" aria-label="AI mavzulari">
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

        <details className="group sm:hidden">
          <summary className="cursor-pointer list-none rounded-lg border border-slate-700 px-3 py-2 text-sm text-slate-300 marker:content-none">
            <span className="flex items-center justify-between">
              <span>📂 Mavzular</span>
              <span className="text-slate-500 group-open:rotate-180">⌄</span>
            </span>
          </summary>
          <nav className="mt-2 grid grid-cols-2 gap-2 text-sm" aria-label="Mobil AI mavzulari">
            <Link
              href="/organish"
              className="col-span-2 rounded-lg border border-emerald-800 bg-emerald-500/5 px-3 py-2 font-semibold text-emerald-400"
            >
              🎓 AI&apos;ni o&apos;rganish
            </Link>
            {categories.map((cat) => (
              <Link
                key={cat.slug}
                href={`/kategoriya/${cat.slug}`}
                className="rounded-lg border border-slate-800 px-3 py-2 text-slate-300 hover:border-blue-500 hover:text-white"
              >
                {cat.name}
              </Link>
            ))}
          </nav>
        </details>
      </div>
    </header>
  );
}
