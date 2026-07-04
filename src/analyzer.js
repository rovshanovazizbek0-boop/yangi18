import Anthropic from "@anthropic-ai/sdk";
import { SYSTEM_PROMPT, ANALYSIS_SCHEMA } from "./prompt.js";

// ANTHROPIC_API_KEY muhit o'zgaruvchisidan olinadi (.env fayliga qarang).
const client = new Anthropic();

const MODEL = process.env.CLAUDE_MODEL || "claude-opus-4-8";

/**
 * Bitta inglizcha AI yangilikni o'zbekcha tahlilga aylantiradi.
 *
 * @param {object} news - { title, content, link, pubDate } ko'rinishidagi yangilik
 * @returns {Promise<object>} - { kategoriya, sarlavha, xulosa, ahamiyati, amaliy_ahamiyat }
 */
export async function analyzeNews(news) {
  const userText = [
    `Title: ${news.title}`,
    news.pubDate ? `Published: ${news.pubDate}` : null,
    news.link ? `Source: ${news.link}` : null,
    "",
    news.content || "",
  ]
    .filter((line) => line !== null)
    .join("\n");

  const response = await client.messages.create({
    model: MODEL,
    max_tokens: 4096,
    system: [
      {
        type: "text",
        text: SYSTEM_PROMPT,
        cache_control: { type: "ephemeral" },
      },
    ],
    output_config: {
      format: {
        type: "json_schema",
        schema: ANALYSIS_SCHEMA,
      },
    },
    messages: [{ role: "user", content: userText }],
  });

  if (response.stop_reason === "refusal") {
    throw new Error("Model bu yangilikni tahlil qilishdan bosh tortdi (refusal).");
  }

  const textBlock = response.content.find((block) => block.type === "text");
  if (!textBlock) {
    throw new Error("API javobida matn topilmadi.");
  }

  const analysis = JSON.parse(textBlock.text);
  return {
    ...analysis,
    manba: news.link || null,
    sana: news.pubDate || null,
    original_sarlavha: news.title,
  };
}

/**
 * Bir nechta yangilikni ketma-ket tahlil qiladi.
 * Xato bo'lgan yangiliklar o'tkazib yuboriladi (natijaga kirmaydi).
 */
export async function analyzeAll(newsItems, { onProgress } = {}) {
  const results = [];
  for (const [index, news] of newsItems.entries()) {
    try {
      onProgress?.(index + 1, newsItems.length, news.title);
      const analysis = await analyzeNews(news);
      results.push(analysis);
    } catch (error) {
      console.error(`  ✗ Tahlil xatosi ("${news.title}"): ${error.message}`);
    }
  }
  return results;
}
