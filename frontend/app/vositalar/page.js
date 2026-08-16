import Link from "next/link";
import { apiGet } from "../../lib/api";
import { SITE_NAME, SITE_URL } from "../../lib/site";
import { categoryName, hasUzData, NOT_CHECKED, yesNo } from "../../lib/tools";
import { serializeJsonLd } from "../../lib/json-ld.mjs";

export const metadata = {
  title: "AI vositalari katalogi — narxi va O'zbekistonda ishlashi",
  description:
    "ChatGPT, Claude, Gemini va boshqa sun'iy intellekt xizmatlari: nima qiladi, " +
    "qancha turadi, O'zbekistondan qanday to'lanadi va o'zbek tilini qanchalik biladi.",
  alternates: { canonical: "/vositalar" },
  openGraph: {
    title: "AI vositalari katalogi — narxi va O'zbekistonda ishlashi",
    description:
      "Sun'iy intellekt xizmatlari haqida o'zbek tilida: narxi, imkoniyatlari " +
      "va O'zbekistonda ishlashi.",
    url: "/vositalar",
  },
};

function collectionJsonLd(tools) {
  return {
    "@context": "https://schema.org",
    "@type": "CollectionPage",
    name: "AI vositalari katalogi",
    url: `${SITE_URL}/vositalar`,
    inLanguage: "uz",
    isPartOf: { "@id": `${SITE_URL}/#website` },
    publisher: { "@id": `${SITE_URL}/#organization` },
    mainEntity: {
      "@type": "ItemList",
      numberOfItems: tools.length,
      itemListElement: tools.map((tool, index) => ({
        "@type": "ListItem",
        position: index + 1,
        name: tool.name,
        url: `${SITE_URL}/vositalar/${tool.slug}`,
      })),
    },
  };
}

function ToolCard({ tool }) {
  const uz = tool.uz || {};
  const checked = hasUzData(uz);

  return (
    <Link
      href={`/vositalar/${tool.slug}`}
      className="flex flex-col rounded-xl border border-slate-800 bg-slate-900/60 p-4 transition hover:border-blue-600"
    >
      <div className="mb-1 flex items-baseline justify-between gap-2">
        <span className="text-lg font-bold">{tool.name}</span>
        <span className="text-xs text-slate-500">{tool.vendor}</span>
      </div>
      <p className="mb-3 flex-1 text-sm leading-snug text-slate-300">{tool.tagline}</p>
      <div className="flex flex-wrap gap-2 text-xs">
        <span className="rounded-full bg-slate-800 px-2 py-1 text-slate-300">
          {categoryName(tool.tool_category)}
        </span>
        {checked ? (
          <span className="rounded-full bg-blue-500/10 px-2 py-1 text-blue-400">
            🇺🇿 {uz.vpn_kerakmi === false ? "VPN kerak emas" : yesNo(uz.vpn_kerakmi, { yes: "VPN kerak", no: "VPN kerak emas" })}
          </span>
        ) : (
          <span className="rounded-full bg-slate-800 px-2 py-1 text-slate-500">
            {NOT_CHECKED}
          </span>
        )}
      </div>
    </Link>
  );
}

export default async function ToolsPage() {
  const [tools, categories] = await Promise.all([
    apiGet("/api/tools"),
    apiGet("/api/tools/kategoriyalar"),
  ]);
  const list = tools || [];

  return (
    <div className="py-8">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: serializeJsonLd(collectionJsonLd(list)) }}
      />

      <h1 className="mb-3 text-2xl font-bold">🧰 AI vositalari katalogi</h1>
      <p className="mb-6 max-w-2xl text-slate-300">
        Har bir xizmat uchun bitta savolga javob beramiz: u nima qiladi, qancha
        turadi va <strong>O&apos;zbekistondan qanday ishlatiladi</strong> — VPN
        kerakmi, qaysi karta o&apos;tadi, o&apos;zbek tilini qanchalik biladi.
      </p>

      {(categories || []).length > 0 && (
        <div className="mb-6 flex flex-wrap gap-2 text-sm">
          {categories.map((item) => (
            <span
              key={item.kategoriya}
              className="rounded-full border border-slate-700 px-3 py-1 text-slate-300"
            >
              {categoryName(item.kategoriya)}{" "}
              <span className="text-slate-500">({item.soni})</span>
            </span>
          ))}
        </div>
      )}

      {list.length > 0 ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {list.map((tool) => (
            <ToolCard key={tool.slug} tool={tool} />
          ))}
        </div>
      ) : (
        <p className="text-slate-400">Katalog hali to&apos;ldirilmoqda.</p>
      )}

      <p className="mt-8 text-sm text-slate-500">
        Ma&apos;lumotda xatolik ko&apos;rsangiz yoki narx o&apos;zgargan
        bo&apos;lsa — <Link href="/aloqa" className="text-blue-400 hover:underline">bizga xabar bering</Link>.
        {" "}Katalog {SITE_NAME} tomonidan qo&apos;lda tekshiriladi.
      </p>
    </div>
  );
}
