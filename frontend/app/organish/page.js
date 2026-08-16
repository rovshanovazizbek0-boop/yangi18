import Link from "next/link";
import GuideCard from "../../components/GuideCard";
import { apiGet } from "../../lib/api";
import { providerName } from "../../lib/guides";
import { serializeJsonLd } from "../../lib/json-ld.mjs";
import { SITE_NAME, SITE_URL } from "../../lib/site";

export const metadata = {
  title: "AI'ni o'rganish — amaliy qo'llanmalar",
  description: "ChatGPT, Gemini, Claude va boshqa AI vositalaridan xavfsiz va samarali foydalanishni o'zbek tilida qadam-baqadam o'rganing.",
  alternates: { canonical: "/organish" },
  openGraph: {
    title: "AI'ni o'rganish — amaliy qo'llanmalar",
    description: "AI vositalaridan foydalanish bo'yicha tekshirilgan, qadam-baqadam o'zbekcha darslar.",
    url: "/organish",
  },
};

export default async function LearningPage() {
  const [guidesResponse, toolsResponse] = await Promise.all([
    apiGet("/api/guides", { limit: 100 }),
    apiGet("/api/tools"),
  ]);
  const guides = guidesResponse || [];
  const tools = toolsResponse || [];
  const providers = [...new Set(guides.map((guide) => guide.provider))];
  const jsonLd = {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "CollectionPage",
        "@id": `${SITE_URL}/organish/#page`,
        name: "AI'ni o'rganish",
        description: metadata.description,
        url: `${SITE_URL}/organish`,
        inLanguage: "uz",
        isPartOf: { "@id": `${SITE_URL}/#website` },
      },
      {
        "@type": "ItemList",
        itemListElement: guides.map((guide, index) => ({
          "@type": "ListItem",
          position: index + 1,
          name: guide.title,
          url: `${SITE_URL}/organish/${guide.slug}`,
        })),
      },
      {
        "@type": "BreadcrumbList",
        itemListElement: [
          { "@type": "ListItem", position: 1, name: SITE_NAME, item: SITE_URL },
          { "@type": "ListItem", position: 2, name: "AI'ni o'rganish", item: `${SITE_URL}/organish` },
        ],
      },
    ],
  };

  return (
    <div className="py-8">
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: serializeJsonLd(jsonLd) }} />
      <section className="mb-8 overflow-hidden rounded-2xl border border-emerald-900 bg-gradient-to-br from-emerald-950/80 via-slate-900 to-slate-950 p-7 sm:p-10">
        <p className="mb-3 text-sm font-bold uppercase tracking-widest text-emerald-400">AI Xabar Akademiyasi</p>
        <h1 className="mb-4 max-w-3xl text-3xl font-bold leading-tight sm:text-4xl">AI&apos;ni shunchaki kuzatmang — undan foydalanishni o&apos;rganing</h1>
        <p className="max-w-3xl text-lg leading-relaxed text-slate-300">
          Har bir qo&apos;llanma aniq vazifa, tayyor misol, xavfsizlik qoidasi va rasmiy manbalar bilan beriladi. Dars ostidagi yangiliklar esa vositadagi oxirgi o&apos;zgarishlarni ko&apos;rsatadi.
        </p>
        <div className="mt-6 flex flex-wrap gap-2">
          {providers.map((provider) => (
            <span key={provider} className="rounded-full border border-emerald-800 px-3 py-1 text-sm text-emerald-300">
              {providerName(provider)}
            </span>
          ))}
        </div>
      </section>

      <div className="mb-6 flex flex-wrap items-end justify-between gap-3">
        <div>
          <h2 className="text-2xl font-bold">Qo&apos;llanmalar</h2>
          <p className="mt-1 text-sm text-slate-400">Boshlang&apos;ich darsdan amaliy ish jarayonigacha.</p>
        </div>
        {tools.length > 0 && (
          <Link href="/vositalar" className="text-sm text-blue-400 hover:underline">AI vositalari katalogini ko&apos;rish →</Link>
        )}
      </div>

      {guides.length > 0 ? (
        <div className="grid gap-5 md:grid-cols-2">
          {guides.map((guide) => <GuideCard key={guide.id} guide={guide} />)}
        </div>
      ) : (
        <p className="rounded-xl border border-slate-800 p-8 text-center text-slate-400">Qo&apos;llanmalar server yangilangandan keyin shu yerda chiqadi.</p>
      )}
    </div>
  );
}
