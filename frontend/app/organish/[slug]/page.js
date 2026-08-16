import Link from "next/link";
import { notFound } from "next/navigation";
import { cache } from "react";
import ArticleCard from "../../../components/ArticleCard";
import { apiGet } from "../../../lib/api";
import { formatDate } from "../../../lib/date";
import { difficultyName, providerName } from "../../../lib/guides";
import { serializeJsonLd } from "../../../lib/json-ld.mjs";
import { seoDescription } from "../../../lib/seo.mjs";
import { SITE_NAME, SITE_URL } from "../../../lib/site";

const getGuide = cache((slug) => apiGet(`/api/guides/${slug}`));

export async function generateMetadata({ params }) {
  const { slug } = await params;
  const guide = await getGuide(slug);
  if (!guide) notFound();

  const title = guide.seo_title || guide.title;
  const description = seoDescription(guide.description || guide.excerpt);
  return {
    title,
    description,
    keywords: guide.tags || [],
    alternates: { canonical: `/organish/${guide.slug}` },
    openGraph: {
      type: "article",
      url: `/organish/${guide.slug}`,
      title,
      description,
      publishedTime: guide.published_at,
      modifiedTime: guide.updated_at,
      siteName: SITE_NAME,
      locale: "uz_UZ",
    },
    twitter: { card: "summary_large_image", title, description },
  };
}

function guideJsonLd(guide) {
  const url = `${SITE_URL}/organish/${guide.slug}`;
  const graph = [
    {
      "@type": "TechArticle",
      "@id": `${url}/#article`,
      mainEntityOfPage: url,
      headline: guide.title,
      description: guide.description,
      datePublished: guide.published_at,
      dateModified: guide.updated_at,
      inLanguage: "uz",
      proficiencyLevel: difficultyName(guide.difficulty),
      timeRequired: `PT${guide.duration_minutes}M`,
      author: { "@type": "Organization", name: SITE_NAME, url: SITE_URL },
      publisher: { "@id": `${SITE_URL}/#organization` },
      citation: (guide.sources || []).map((source) => source.url),
    },
    {
      "@type": "BreadcrumbList",
      itemListElement: [
        { "@type": "ListItem", position: 1, name: SITE_NAME, item: SITE_URL },
        { "@type": "ListItem", position: 2, name: "AI'ni o'rganish", item: `${SITE_URL}/organish` },
        { "@type": "ListItem", position: 3, name: guide.title, item: url },
      ],
    },
  ];
  if ((guide.faq || []).length > 0) {
    graph.push({
      "@type": "FAQPage",
      mainEntity: guide.faq.map((item) => ({
        "@type": "Question",
        name: item.question,
        acceptedAnswer: { "@type": "Answer", text: item.answer },
      })),
    });
  }
  return { "@context": "https://schema.org", "@graph": graph };
}

export default async function GuidePage({ params }) {
  const { slug } = await params;
  const guide = await getGuide(slug);
  if (!guide) notFound();

  const relatedNews = await apiGet("/api/news", {
    kategoriya: guide.related_category_slug || undefined,
    limit: 4,
  });

  return (
    <article className="mx-auto max-w-4xl py-8">
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: serializeJsonLd(guideJsonLd(guide)) }} />

      <nav className="mb-5 text-sm text-slate-500" aria-label="Sahifa yo'li">
        <Link href="/" className="hover:text-white">Bosh sahifa</Link> <span> / </span>
        <Link href="/organish" className="hover:text-white">AI&apos;ni o&apos;rganish</Link>
      </nav>

      <div className="mb-4 flex flex-wrap gap-2 text-xs">
        <span className="rounded-full bg-emerald-500/10 px-3 py-1 font-semibold text-emerald-400">{providerName(guide.provider)}</span>
        <span className="rounded-full bg-slate-800 px-3 py-1 text-slate-300">{difficultyName(guide.difficulty)}</span>
        <span className="rounded-full bg-slate-800 px-3 py-1 text-slate-300">⏱ {guide.duration_minutes} daqiqa</span>
        {guide.generation_type === "ai" && (
          <span className="rounded-full border border-violet-800 bg-violet-500/5 px-3 py-1 text-violet-300">AI agent tayyorlagan kunlik dars</span>
        )}
      </div>
      <h1 className="mb-5 text-3xl font-bold leading-tight sm:text-4xl">{guide.title}</h1>
      <p className="mb-4 border-l-4 border-emerald-500 pl-4 text-lg leading-relaxed text-slate-200">{guide.intro}</p>
      <p className="mb-8 text-sm text-slate-500">Oxirgi tekshiruv: {formatDate(guide.verified_at || guide.updated_at)} · Rasmiy manbalar bilan tekshirilgan</p>

      <nav className="mb-9 rounded-xl border border-slate-800 bg-slate-900/60 p-5" aria-label="Dars mundarijasi">
        <h2 className="mb-3 font-bold">Dars mundarijasi</h2>
        <ol className="space-y-2 text-sm text-slate-300">
          {(guide.sections || []).map((section, index) => (
            <li key={section.title}><a href={`#qadam-${index + 1}`} className="hover:text-emerald-400">{section.title}</a></li>
          ))}
        </ol>
      </nav>

      <div className="space-y-10">
        {(guide.sections || []).map((section, index) => (
          <section key={section.title} id={`qadam-${index + 1}`} className="scroll-mt-6">
            <h2 className="mb-4 text-2xl font-bold">{section.title}</h2>
            <div className="space-y-4 leading-7 text-slate-300">
              {(section.body || []).map((paragraph) => <p key={paragraph}>{paragraph}</p>)}
            </div>
            {(section.steps || []).length > 0 && (
              <ol className="mt-5 space-y-3">
                {section.steps.map((step, stepIndex) => (
                  <li key={step} className="flex gap-3 rounded-lg border border-slate-800 bg-slate-900/40 p-3 text-slate-200">
                    <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-emerald-600 text-xs font-bold text-white">{stepIndex + 1}</span>
                    <span>{step}</span>
                  </li>
                ))}
              </ol>
            )}
            {section.example?.text && (
              <div className="mt-5 rounded-xl border border-blue-900 bg-blue-500/5 p-5">
                <div className="mb-2 text-sm font-bold text-blue-400">✍️ {section.example.label || "Misol"}</div>
                <p className="whitespace-pre-wrap leading-7 text-slate-200">{section.example.text}</p>
              </div>
            )}
            {section.tip && (
              <div className="mt-5 rounded-xl border border-amber-900 bg-amber-500/5 p-4 text-sm leading-6 text-amber-100">💡 {section.tip}</div>
            )}
          </section>
        ))}
      </div>

      {(guide.faq || []).length > 0 && (
        <section className="mt-12 border-t border-slate-800 pt-8">
          <h2 className="mb-5 text-2xl font-bold">Ko&apos;p so&apos;raladigan savollar</h2>
          <div className="space-y-3">
            {guide.faq.map((item) => (
              <details key={item.question} className="rounded-xl border border-slate-800 bg-slate-900/50 p-4">
                <summary className="cursor-pointer font-semibold text-slate-100">{item.question}</summary>
                <p className="mt-3 leading-7 text-slate-300">{item.answer}</p>
              </details>
            ))}
          </div>
        </section>
      )}

      {(guide.sources || []).length > 0 && (
        <section className="mt-10 rounded-xl border border-slate-800 p-5">
          <h2 className="mb-3 font-bold">Rasmiy manbalar</h2>
          <ul className="space-y-2 text-sm">
            {guide.sources.map((source) => (
              <li key={source.url}><a href={source.url} target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:underline">{source.title} ↗</a></li>
            ))}
          </ul>
        </section>
      )}

      {(relatedNews || []).length > 0 && (
        <section className="mt-12 border-t border-slate-800 pt-8">
          <div className="mb-5 flex items-end justify-between gap-3">
            <div>
              <p className="text-sm font-semibold text-emerald-400">Doim yangilanadi</p>
              <h2 className="text-2xl font-bold">Shu mavzudagi oxirgi yangiliklar</h2>
            </div>
            {guide.related_category_slug && <Link href={`/kategoriya/${guide.related_category_slug}`} className="text-sm text-blue-400 hover:underline">Barchasi →</Link>}
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            {relatedNews.map((article) => <ArticleCard key={article.id} article={article} compact />)}
          </div>
        </section>
      )}
    </article>
  );
}
