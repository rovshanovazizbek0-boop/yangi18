import Link from "next/link";
import ArticleCard from "../components/ArticleCard";
import AdPlaceholder from "../components/AdPlaceholder";
import GuideCard from "../components/GuideCard";
import { apiGet } from "../lib/api";

export default async function HomePage() {
  const [latest, top, digest, trends, guides, tools] = await Promise.all([
    apiGet("/api/news", { limit: 12 }),
    apiGet("/api/news/top", { limit: 10, kunlar: 1 }),
    apiGet("/api/news/digest"),
    apiGet("/api/news/trends"),
    apiGet("/api/guides", { limit: 3 }),
    apiGet("/api/tools"),
  ]);

  const hasContent = (latest || []).length > 0;
  const featuredTools = (tools || []).slice(0, 6);

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

        {featuredTools.length > 0 && (
          <section className="mt-10 rounded-2xl border border-blue-900/70 bg-blue-950/20 p-5 sm:p-6">
            <div className="mb-5 flex flex-wrap items-end justify-between gap-3">
              <div>
                <p className="mb-1 text-sm font-semibold text-blue-400">🧰 AI vositalari katalogi</p>
                <h2 className="text-xl font-bold">Mashhur AI xizmatlarning narxi va O&apos;zbekistonda ishlashi</h2>
              </div>
              <Link href="/vositalar" className="text-sm text-blue-400 hover:underline">
                Barcha vositalar ({(tools || []).length}) →
              </Link>
            </div>
            <div className="grid gap-4 sm:grid-cols-2 md:grid-cols-3">
              {featuredTools.map((tool) => (
                <Link
                  key={tool.slug}
                  href={`/vositalar/${tool.slug}`}
                  className="flex flex-col justify-between rounded-xl border border-slate-800 bg-slate-900/60 p-4 transition-colors hover:border-blue-500"
                >
                  <div>
                    <div className="mb-1 flex items-center justify-between gap-2">
                      <h3 className="font-bold text-white">{tool.name}</h3>
                      {tool.vendor && <span className="text-xs text-slate-400">{tool.vendor}</span>}
                    </div>
                    <p className="line-clamp-2 text-xs leading-relaxed text-slate-300">{tool.tagline}</p>
                  </div>
                  <div className="mt-3 flex flex-wrap gap-1.5 text-[11px] text-slate-400">
                    {tool.free_tier === true && (
                      <span className="rounded bg-emerald-950/70 px-2 py-0.5 text-emerald-300">Bepul reja bor</span>
                    )}
                    {tool.uz?.vpn_kerakmi === false && (
                      <span className="rounded bg-slate-800 px-2 py-0.5 text-slate-300">VPN shart emas</span>
                    )}
                  </div>
                </Link>
              ))}
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
