import { apiGet } from "../../lib/api";
import { SITE_NAME, SITE_URL } from "../../lib/site";

export const revalidate = 3600;

export async function GET() {
  let articles = [];
  try {
    articles = (await apiGet("/api/news", { limit: 20 })) || [];
  } catch {
    articles = [];
  }

  const lines = [
    `# ${SITE_NAME}`,
    "",
    "> Dunyodagi eng muhim sun'iy intellekt (AI) yangiliklari, o'zbekcha amaliy qo'llanmalar va AI vositalari katalogi.",
    "",
    "## Asosiy bo'limlar",
    `- [Bosh sahifa](${SITE_URL}/): Eng so'nggi AI yangiliklari va kunlik dayjest`,
    `- [AI'ni o'rganish](${SITE_URL}/organish): Amaliy qo'llanmalar va promptlar`,
    `- [AI vositalari](${SITE_URL}/vositalar): AI servislar narxi va O'zbekistonda ishlashi`,
    `- [Loyiha haqida](${SITE_URL}/haqida)`,
    `- [Sitemap](${SITE_URL}/sitemap.xml)`,
    `- [News Sitemap](${SITE_URL}/news-sitemap.xml)`,
    `- [RSS Feed](${SITE_URL}/api/news/rss)`,
    "",
    "## So'nggi maqolalar",
  ];

  for (const article of articles) {
    const url = `${SITE_URL}/maqola/${article.slug}`;
    const summary = String(article.summary || "")
      .replace(/\s+/g, " ")
      .trim()
      .slice(0, 160);
    lines.push(summary ? `- [${article.title}](${url}): ${summary}` : `- [${article.title}](${url})`);
  }

  return new Response(`${lines.join("\n")}\n`, {
    headers: {
      "Content-Type": "text/plain; charset=utf-8",
      "Cache-Control": "public, s-maxage=3600, stale-while-revalidate=86400",
    },
  });
}
