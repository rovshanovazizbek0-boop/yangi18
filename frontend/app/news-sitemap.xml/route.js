import { API_URL } from "../../lib/api";
import { SITE_NAME, SITE_URL } from "../../lib/site";

function escapeXml(value) {
  return String(value || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&apos;");
}

// Har so'rovda qayta hisoblanadi. Aks holda Next.js build paytidagi natijani
// muzlatib qo'yadi — backend o'sha lahzada javob bermasa (Render uyquda bo'lsa),
// sitemap abadiy bo'sh qolib, Google News hech qanday maqola ko'rmaydi.
export const dynamic = "force-dynamic";

export async function GET() {
  let articles = null;
  try {
    const response = await fetch(`${API_URL}/api/news?limit=100`, {
      next: { revalidate: 300 },
    });
    if (response.ok) articles = await response.json();
  } catch (error) {
    console.error("News sitemap fetch error:", error);
  }

  // Bo'sh sitemap Google uchun "yangilik yo'q" degani. Backend javob bermasa
  // 503 qaytaramiz — shunda Google keyinroq qayta uradi.
  if (!articles) {
    return new Response("News sitemap hozircha mavjud emas", { status: 503 });
  }

  const cutoff = Date.now() - 2 * 24 * 60 * 60 * 1000;
  const urls = articles
    .filter((article) => {
      const published = Date.parse(article.published_at || article.created_at || "");
      return Number.isFinite(published) && published >= cutoff;
    })
    .map((article) => {
      const published = new Date(article.published_at || article.created_at).toISOString();
      return `  <url>
    <loc>${escapeXml(`${SITE_URL}/maqola/${article.slug}`)}</loc>
    <news:news>
      <news:publication>
        <news:name>${escapeXml(SITE_NAME)}</news:name>
        <news:language>uz</news:language>
      </news:publication>
      <news:publication_date>${published}</news:publication_date>
      <news:title>${escapeXml(article.title)}</news:title>
    </news:news>
  </url>`;
    })
    .join("\n");

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">
${urls}
</urlset>`;

  return new Response(xml, {
    headers: {
      "Content-Type": "application/xml; charset=utf-8",
      "Cache-Control": "public, s-maxage=300, stale-while-revalidate=600",
    },
  });
}
