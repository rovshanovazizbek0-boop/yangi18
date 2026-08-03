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

export default async function sitemap() {
  const [articles, categories] = await Promise.all([
    fetchAllArticles(),
    fetchJson(`${API_URL}/api/categories`),
  ]);

  const articleUrls = (articles || []).map((article) => ({
    url: `${SITE_URL}/maqola/${article.slug}`,
    lastModified: article.published_at ? new Date(article.published_at) : new Date(),
    changeFrequency: "weekly",
    priority: 0.7,
  }));

  const categoryUrls = (categories || []).map((cat) => ({
    url: `${SITE_URL}/kategoriya/${cat.slug}`,
    lastModified: new Date(),
    changeFrequency: "daily",
    priority: 0.8,
  }));

  const staticUrls = ["/haqida", "/aloqa", "/maxfiylik"].map((path) => ({
    url: `${SITE_URL}${path}`,
    lastModified: new Date(),
    changeFrequency: "monthly",
    priority: 0.4,
  }));

  return [
    {
      url: SITE_URL,
      lastModified: new Date(),
      changeFrequency: "always",
      priority: 1.0,
    },
    ...categoryUrls,
    ...staticUrls,
    ...articleUrls,
  ];
}
