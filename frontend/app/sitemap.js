import { API_URL } from "../lib/api";
import { SITE_URL } from "../lib/site";

// Deploy build vaqtida backend hali tayyor bo'lmasligi mumkin; sitemap har
// so'rovda server muhitidagi API manzilidan olinadi.
export const dynamic = "force-dynamic";

async function fetchJson(url) {
  try {
    const res = await fetch(url, { next: { revalidate: 300 } });
    return res.ok ? await res.json() : [];
  } catch (error) {
    console.error("Sitemap fetch error:", error);
    return [];
  }
}

async function fetchAllArticles() {
  const pageSize = 100;
  const maxPages = 20;
  const articles = [];

  for (let page = 0; page < maxPages; page += 1) {
    const batch = await fetchJson(
      `${API_URL}/api/news?limit=${pageSize}&offset=${page * pageSize}`,
    );
    if (!Array.isArray(batch) || batch.length === 0) break;
    articles.push(...batch);
    if (batch.length < pageSize) break;
  }

  return articles;
}

function validDate(value) {
  if (!value) return undefined;
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? undefined : date;
}

function newestDate(values) {
  const dates = values.map(validDate).filter(Boolean);
  if (dates.length === 0) return undefined;
  return new Date(Math.max(...dates.map((date) => date.getTime())));
}

export default async function sitemap() {
  const [articles, categories, tools, guides] = await Promise.all([
    fetchAllArticles(),
    fetchJson(`${API_URL}/api/categories`),
    fetchJson(`${API_URL}/api/tools`),
    fetchJson(`${API_URL}/api/guides?limit=100`),
  ]);

  const newestArticle = newestDate(
    (articles || []).map((article) => article.published_at || article.created_at),
  );
  const categoryDates = new Map();
  for (const article of articles || []) {
    const slug = article.category?.slug;
    const date = validDate(article.published_at || article.created_at);
    if (!slug || !date) continue;
    const current = categoryDates.get(slug);
    if (!current || date > current) categoryDates.set(slug, date);
  }

  const articleUrls = (articles || []).map((article) => ({
    url: `${SITE_URL}/maqola/${article.slug}`,
    lastModified: validDate(article.published_at || article.created_at),
    changeFrequency: "weekly",
    priority: 0.7,
  }));

  const categoryUrls = (categories || []).map((cat) => ({
    url: `${SITE_URL}/kategoriya/${cat.slug}`,
    lastModified: categoryDates.get(cat.slug),
    changeFrequency: "daily",
    priority: 0.8,
  }));

  // Vosita sahifalari yangilikdan sekin eskiradi, lekin qidiruvda uzoq
  // yashaydi — shuning uchun ustuvorligi maqoladan yuqori.
  const toolUrls = (tools || []).map((tool) => ({
    url: `${SITE_URL}/vositalar/${tool.slug}`,
    lastModified: validDate(tool.checked_at),
    changeFrequency: "monthly",
    priority: 0.8,
  }));

  const guideUrls = (guides || []).map((guide) => ({
    url: `${SITE_URL}/organish/${guide.slug}`,
    lastModified: validDate(guide.updated_at || guide.verified_at || guide.published_at),
    changeFrequency: "monthly",
    priority: 0.85,
  }));

  const newestGuide = newestDate(
    (guides || []).map((guide) => guide.updated_at || guide.verified_at || guide.published_at),
  );
  const staticPaths = ["/haqida", "/aloqa", "/maxfiylik"];
  if ((tools || []).length > 0) staticPaths.unshift("/vositalar");
  const staticUrls = staticPaths.map((path) => ({
    url: `${SITE_URL}${path}`,
    changeFrequency: "monthly",
    priority: 0.4,
  }));

  return [
    {
      url: SITE_URL,
      lastModified: newestArticle,
      changeFrequency: "hourly",
      priority: 1.0,
    },
    {
      url: `${SITE_URL}/organish`,
      lastModified: newestGuide,
      changeFrequency: "weekly",
      priority: 0.9,
    },
    ...categoryUrls,
    ...toolUrls,
    ...guideUrls,
    ...staticUrls,
    ...articleUrls,
  ];
}
