import Link from "next/link";
import ArticleCard from "../components/ArticleCard";
import AdPlaceholder from "../components/AdPlaceholder";
import GuideCard from "../components/GuideCard";
import { apiGet } from "../lib/api";

export default async function HomePage() {
  const [latest, top, digest, trends, guides] = await Promise.all([
    apiGet("/api/news", { limit: 12 }),
    apiGet("/api/news/top", { limit: 10, kunlar: 1 }),
    apiGet("/api/news/digest"),
    apiGet("/api/news/trends"),
    apiGet("/api/guides", { limit: 3 }),
  ]);

  const hasContent = (latest || []).length > 0;

  return (
    <div className="grid gap-8 py-8 lg:grid-cols-[1fr_300px]">
      <div>
        <h1 className="mb-5 text-2xl font-bold">📰 Eng so&apos;nggi AI yangiliklari</h1>
        {hasContent ? (
          <div className="grid gap-5 sm:grid-cols-2">
            {latest.map((article, index) => (
              <ArticleCard key={article.id} article={article} priority={index === 0} />
            ))}
          </div>
        ) : (
          <div className="rounded-xl border border-slate-800 p-10 text-center leading-relaxed text-slate-400">
            Hozircha chop etilgan yangiliklar yo&apos;q.
            <br />
            Backend&apos;da <code className="rounded bg-slate-800 px-2 py-0.5">python -m app.pipeline</code>{" "}
            buyrug&apos;ini ishga tushiring va admin panelda tasdiqlang.
          </div>
        )}

        {(guides || []).length > 0 && (
          <section className="mt-10 rounded-2xl border border-emerald-900/70 bg-emerald-950/20 p-5 sm:p-6">
            <div className="mb-5 flex flex-wrap items-end justify-between gap-3">
              <div>
                <p className="mb-1 text-sm font-semibold text-emerald-400">🎓 AI&apos;ni o&apos;rganish</p>
                <h2 className="text-xl font-bold">Yangilikni o&apos;qibgina qolmay, AI&apos;dan foydalanishni o&apos;rganing</h2>
              </div>
              <Link href="/organish" className="text-sm text-emerald-400 hover:underline">
                Barcha qo&apos;llanmalar →
              </Link>
            </div>
            <div className="grid gap-4 md:grid-cols-3">
              {guides.map((guide) => <GuideCard key={guide.id} guide={guide} compact />)}
            </div>
          </section>
        )}

        {(digest || []).length > 0 && (
          <section className="mt-10">
            <h2 className="mb-4 text-xl font-bold">☀️ Bugungi AI dayjesti</h2>
            <ul className="space-y-2">
              {digest.map((article) => (
                <li key={article.id} className="flex items-start gap-2 text-sm">
                  <span>{"⭐".repeat(article.importance)}</span>
                  <Link href={`/maqola/${article.slug}`} className="hover:text-blue-400">
                    {article.title}
                  </Link>
                </li>
              ))}
            </ul>
          </section>
        )}
      </div>

      <aside className="space-y-8">
        <section>
          <h2 className="mb-3 font-bold">🔥 Top 10 kunlik</h2>
          <div className="space-y-2">
            {(top || []).length > 0 ? (
              top.map((article) => (
                <ArticleCard key={article.id} article={article} compact />
              ))
            ) : (
              <p className="text-sm text-slate-500">Bugun hali yangiliklar yo&apos;q.</p>
            )}
          </div>
        </section>

        <section>
          <AdPlaceholder type="sidebar" />
        </section>

        <section>
          <h2 className="mb-3 font-bold">📈 Trend mavzular</h2>
          <div className="flex flex-wrap gap-2">
            {(trends || []).length > 0 ? (
              trends.map((trend) => (
                <Link
                  key={trend.teg}
                  href={`/qidiruv?q=${encodeURIComponent(trend.teg)}`}
                  className="rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-300 hover:bg-blue-600 hover:text-white"
                >
                  #{trend.teg} <span className="text-slate-500">({trend.soni})</span>
                </Link>
              ))
            ) : (
              <p className="text-sm text-slate-500">Trendlar hali shakllanmadi.</p>
            )}
          </div>
        </section>
      </aside>
    </div>
  );
}
