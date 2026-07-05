import { API_URL } from "../lib/api";

export default async function sitemap() {
  const baseUrl = "https://aixabar.uz";

  let articles = [];
  try {
    const res = await fetch(`${API_URL}/api/news?limit=100`, { next: { revalidate: 3600 } });
    if (res.ok) {
      articles = await res.json();
    }
  } catch (error) {
    console.error("Sitemap fetch error:", error);
  }

  const articleUrls = (articles || []).map((article) => ({
    url: `${baseUrl}/maqola/${article.slug}`,
    lastModified: article.published_at ? new Date(article.published_at) : new Date(),
    changeFrequency: "daily",
    priority: 0.7,
  }));

  return [
    {
      url: baseUrl,
      lastModified: new Date(),
      changeFrequency: "always",
      priority: 1.0,
    },
    ...articleUrls,
  ];
}
