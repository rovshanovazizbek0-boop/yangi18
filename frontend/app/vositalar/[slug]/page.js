import Link from "next/link";
import { notFound } from "next/navigation";
import { cache } from "react";
import { apiGet } from "../../../lib/api";
import { formatDate } from "../../../lib/date";
import { SITE_NAME, SITE_URL } from "../../../lib/site";
import { categoryName, hasUzData, NOT_CHECKED, yesNo } from "../../../lib/tools";
import { serializeJsonLd } from "../../../lib/json-ld.mjs";

const getTool = cache((slug) => apiGet(`/api/tools/${slug}`));

function pageTitle(tool) {
  return `${tool.name} — narxi, imkoniyatlari va O'zbekistonda ishlashi`;
}

export async function generateMetadata({ params }) {
  const { slug } = await params;
  const tool = await getTool(slug);
  if (!tool) notFound();

  const description = `${tool.name} (${tool.vendor}) nima qiladi, qancha turadi va O'zbekistondan qanday ishlatiladi — VPN, to'lov va o'zbek tili haqida.`;

  return {
    title: pageTitle(tool),
    description,
    alternates: { canonical: `/vositalar/${tool.slug}` },
    openGraph: {
      type: "article",
      title: pageTitle(tool),
      description,
      url: `/vositalar/${tool.slug}`,
      siteName: SITE_NAME,
      locale: "uz_UZ",
    },
  };
}

function toolJsonLd(tool) {
  const url = `${SITE_URL}/vositalar/${tool.slug}`;
  const offers = (tool.plans || [])
    .filter((plan) => typeof plan.narx_usd === "number")
    .map((plan) => ({
      "@type": "Offer",
      name: plan.nom,
      price: plan.narx_usd,
      priceCurrency: "USD",
    }));

  const application = {
    "@type": "SoftwareApplication",
    name: tool.name,
    applicationCategory: "AIApplication",
    description: tool.tagline || tool.description?.slice(0, 200),
    url: tool.official_url || url,
    author: { "@type": "Organization", name: tool.vendor },
    ...(offers.length > 0 && { offers }),
  };

  return {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "WebPage",
        "@id": url,
        name: pageTitle(tool),
        inLanguage: "uz",
        isPartOf: { "@id": `${SITE_URL}/#website` },
        publisher: { "@id": `${SITE_URL}/#organization` },
        ...(tool.checked_at && { dateModified: tool.checked_at }),
        mainEntity: application,
      },
      {
        "@type": "BreadcrumbList",
        itemListElement: [
          { "@type": "ListItem", position: 1, name: "Bosh sahifa", item: SITE_URL },
          { "@type": "ListItem", position: 2, name: "AI vositalari", item: `${SITE_URL}/vositalar` },
          { "@type": "ListItem", position: 3, name: tool.name, item: url },
        ],
      },
    ],
  };
}

function Row({ label, children }) {
  return (
    <div className="flex flex-wrap gap-x-3 border-b border-slate-800 py-2 last:border-0">
      <span className="w-32 shrink-0 text-slate-400">{label}</span>
      <span className="flex-1 text-slate-100">{children}</span>
    </div>
  );
}

function Unknown() {
  return <span className="text-slate-500">{NOT_CHECKED}</span>;
}

export default async function ToolPage({ params }) {
  const { slug } = await params;
  const tool = await getTool(slug);
  if (!tool) notFound();

  const uz = tool.uz || {};
  const uzReady = hasUzData(uz);
  const plans = tool.plans || [];

  const [allTools, news] = await Promise.all([
    apiGet("/api/tools"),
    tool.news_category_slug
      ? apiGet("/api/news", { kategoriya: tool.news_category_slug, limit: 5 })
      : Promise.resolve([]),
  ]);

  // Katalogda hali yo'q alternativaga havola qo'ymaymiz — 404 chiqadi.
  const known = new Map((allTools || []).map((item) => [item.slug, item]));
  const alternatives = (tool.alternatives || [])
    .map((altSlug) => known.get(altSlug))
    .filter(Boolean);

  return (
    <article className="mx-auto max-w-3xl py-8">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: serializeJsonLd(toolJsonLd(tool)) }}
      />

      <nav className="mb-3 text-sm text-slate-400" aria-label="Yo'l">
        <Link href="/vositalar" className="hover:text-blue-400">
          🧰 AI vositalari
        </Link>
        <span className="px-2">/</span>
        <span>{tool.name}</span>
      </nav>

      <h1 className="mb-2 text-3xl font-bold leading-tight">{pageTitle(tool)}</h1>
      <p className="mb-6 text-lg text-slate-300">{tool.tagline}</p>

      <section className="mb-8 rounded-xl border border-slate-800 bg-slate-900/60 p-5">
        <h2 className="mb-3 font-bold">⚡ Tez javob</h2>
        <div className="text-sm">
          <Row label="Ishlab chiqaruvchi">{tool.vendor}</Row>
          <Row label="Turi">{categoryName(tool.tool_category)}</Row>
          <Row label="Bepul reja">{yesNo(tool.free_tier, { yes: "Bor", no: "Yo'q" })}</Row>
          <Row label="Narxi">
            {plans.length > 0 ? (
              plans.map((plan) => `${plan.nom} — $${plan.narx_usd}/${plan.davr}`).join(" · ")
            ) : (
              <Unknown />
            )}
          </Row>
          <Row label="VPN kerakmi">
            {yesNo(uz.vpn_kerakmi, { yes: "Ha", no: "Yo'q" })}
          </Row>
          <Row label="To'lov">{uz.tolov || <Unknown />}</Row>
          <Row label="O'zbek tili">
            {uz.ozbek_tili ? (
              <>
                {"⭐".repeat(Math.max(1, Math.min(5, uz.ozbek_tili.baho)))}{" "}
                <span className="text-slate-300">{uz.ozbek_tili.izoh}</span>
              </>
            ) : (
              <Unknown />
            )}
          </Row>
        </div>
      </section>

      <section className="mb-8 rounded-xl border border-blue-900 bg-blue-500/5 p-5">
        <h2 className="mb-3 font-bold text-blue-400">🇺🇿 O&apos;zbekistonda qanday ishlaydi</h2>
        {uzReady ? (
          <div className="space-y-3 text-slate-200">
            {uz.narx_somda && (
              <p>
                <strong>Narxi so&apos;mda:</strong> {uz.narx_somda}
              </p>
            )}
            {uz.tolov && (
              <p>
                <strong>To&apos;lov:</strong> {uz.tolov}
              </p>
            )}
            {(uz.tolov_yollari || []).length > 0 && (
              <div>
                <strong>To&apos;lash yo&apos;llari:</strong>
                <ul className="mt-1 list-inside list-disc text-slate-300">
                  {uz.tolov_yollari.map((way) => (
                    <li key={way}>{way}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ) : (
          <p className="text-slate-300">
            Bu vosita O&apos;zbekistondan hali sinab ko&apos;rilmagan. Sinovdan
            o&apos;tgach — VPN, to&apos;lov va o&apos;zbek tili bo&apos;yicha
            natijalar shu yerda chiqadi. Tajribangiz bo&apos;lsa,{" "}
            <Link href="/aloqa" className="text-blue-400 hover:underline">
              bizga yozing
            </Link>
            .
          </p>
        )}
      </section>

      {tool.description && (
        <section className="mb-8">
          <h2 className="mb-3 text-xl font-bold">{tool.name} nima qiladi?</h2>
          <div className="space-y-4 leading-relaxed text-slate-300">
            {tool.description.split(/\n\s*\n/).map((paragraph, i) => (
              <p key={i}>{paragraph}</p>
            ))}
          </div>
        </section>
      )}

      {alternatives.length > 0 && (
        <section className="mb-8">
          <h2 className="mb-3 text-xl font-bold">🔄 Alternativalar</h2>
          <div className="grid gap-3 sm:grid-cols-2">
            {alternatives.map((alt) => (
              <Link
                key={alt.slug}
                href={`/vositalar/${alt.slug}`}
                className="rounded-lg border border-slate-800 p-3 hover:border-blue-600"
              >
                <div className="font-semibold">{alt.name}</div>
                <div className="text-sm text-slate-400">{alt.tagline}</div>
              </Link>
            ))}
          </div>
        </section>
      )}

      {(news || []).length > 0 && (
        <section className="mb-8">
          <h2 className="mb-3 text-xl font-bold">📰 {tool.name} haqida so&apos;nggi yangiliklar</h2>
          <ul className="space-y-2">
            {news.map((article) => (
              <li key={article.slug}>
                <Link
                  href={`/maqola/${article.slug}`}
                  className="text-slate-200 hover:text-blue-400"
                >
                  {article.title}
                </Link>{" "}
                <span className="text-xs text-slate-500">
                  {formatDate(article.published_at)}
                </span>
              </li>
            ))}
          </ul>
        </section>
      )}

      <div className="flex flex-wrap items-center gap-4 border-t border-slate-800 pt-5 text-sm">
        {tool.official_url && (
          <a
            href={tool.official_url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-400 hover:underline"
          >
            🔗 Rasmiy sayt
          </a>
        )}
        <span className="text-slate-500">
          {tool.checked_at
            ? `✅ Tekshirilgan: ${formatDate(tool.checked_at)}`
            : `⏳ ${NOT_CHECKED}`}
        </span>
      </div>
    </article>
  );
}
