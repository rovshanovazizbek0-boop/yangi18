import Parser from "rss-parser";

// Inglizcha AI yangiliklari olinadigan RSS manbalar.
export const FEEDS = [
  { name: "OpenAI Blog", url: "https://openai.com/news/rss.xml" },
  { name: "Google AI Blog", url: "https://blog.google/technology/ai/rss/" },
  { name: "Anthropic News", url: "https://www.anthropic.com/rss.xml" },
  { name: "TechCrunch AI", url: "https://techcrunch.com/category/artificial-intelligence/feed/" },
  { name: "VentureBeat AI", url: "https://venturebeat.com/category/ai/feed/" },
  { name: "MIT Technology Review AI", url: "https://www.technologyreview.com/topic/artificial-intelligence/feed" },
];

const parser = new Parser({ timeout: 20000 });

/**
 * Barcha manbalardan eng so'nggi yangiliklarni yig'adi.
 *
 * @param {number} perFeed - har bir manbadan nechta yangilik olinadi
 * @returns {Promise<Array<{title, content, link, pubDate, feedName}>>}
 */
export async function fetchLatestNews(perFeed = 3) {
  const all = [];

  const settled = await Promise.allSettled(
    FEEDS.map(async (feed) => {
      const parsed = await parser.parseURL(feed.url);
      return parsed.items.slice(0, perFeed).map((item) => ({
        title: item.title?.trim() || "(sarlavhasiz)",
        content: (item.contentSnippet || item.content || "").slice(0, 4000),
        link: item.link || null,
        pubDate: item.isoDate || item.pubDate || null,
        feedName: feed.name,
      }));
    }),
  );

  settled.forEach((result, i) => {
    if (result.status === "fulfilled") {
      all.push(...result.value);
    } else {
      console.error(`  ✗ Manba o'qilmadi (${FEEDS[i].name}): ${result.reason?.message || result.reason}`);
    }
  });

  // Eng yangi yangiliklar birinchi bo'lib tursin.
  all.sort((a, b) => new Date(b.pubDate || 0) - new Date(a.pubDate || 0));
  return all;
}
